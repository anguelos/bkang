from pathlib import Path
import toml
import importlib.resources as pkg_resources
import os
import tempfile
import subprocess
from crontab import CronTab

from . import resources
from typing import Any


def get_config_path() -> Path:
    config_path = Path(__file__).parent / "resources" / "config.toml"
    return config_path


def test_ssh_noauth(host, port=22, username=None, timeout=2):
    ssh_command = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=" + str(timeout)]
    if port != 22:
        ssh_command += ["-p", str(port)]
    if username:
        ssh_command.append(f"{username}@{host}")
    else:
        ssh_command.append(host)

    try:
        result = subprocess.run(ssh_command + ["exit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        print(f"SSH attempt failed: {e}")
        return False


def load_config() -> dict:
    """
    Load the configuration file.
    """
    config_path = get_config_path()
    if not config_path.is_file():
        default_config_path = Path(__file__).parent / "resources" / "default_config.toml"
        open(config_path, "w").write(open(default_config_path, "r").read())
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file (and default) not found: {config_path}")    
    with open(config_path, "r") as f:
        config = toml.load(f)
    return config


def save_config(config: dict) -> None:
    """
    Save the configuration file.
    """
    config_path = Path(__file__).parent / "resources" / "config.toml"
    with open(config_path, "w") as f:
        toml.dump(config, f)


def update_fargv_dict(d: dict) -> dict:
    config = load_config()
    for key, value in config.items():
        if key in d:
            if isinstance(d[key], tuple):
                assert value in d[key], f"Invalid value for {key}: {value}. Expected one of {d[key]}"
                new_order = list(d[key])
                new_order.remove(value)
                new_order.insert(0, value)
                d[key] = tuple(new_order)
            elif isinstance(d[key], list) and len(d[key]) == 2 and isinstance(d[key][0], tuple):
                assert value in d[key][0], f"Invalid value for {key}: {value}. Expected one of {d[key]}"
                new_order = list(d[key][0])
                new_order.remove(value)
                new_order.insert(0, value)
                d[key] = [new_order, d[key][1]]
            else:
                d[key] = value
    return d


def update_config_from_fargv(args: Any) -> dict:
    config_d = load_config()
    for key, value in args.__dict__.items():
        if key in config_d:
            config_d[key] = value
    save_config(config_d)
    return config_d


def validate_config_str(config_file_contents: str) -> bool:
    default_config_path = Path(__file__).parent / "resources" / "default_config.toml"
    with open(default_config_path, "r") as f:
        default_config = toml.load(f)
    config = toml.loads(config_file_contents)
    if set(config.keys()) != set(default_config.keys()):
        return False
    for key, value in default_config.items():
        if type(value) != type(config[key]):
            return False
    if config["mode"] not in ["client", "server"," local"]:
        return False
    if config["mode"] == "local" and config["archive_address"] not in ["localhost", "127.0.0.1"]:
        return False
    return True


def edit_file_like_visudo(original_path):
    editor = os.environ.get('EDITOR', 'vi')
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
        temp_path = tmp_file.name
        # Copy original content to temp file
        with open(original_path, 'r') as orig_file:
            contents = orig_file.read()
            tmp_file.write(contents)
            tmp_file.flush()
    try:
        # Open the editor
        subprocess.call([editor, temp_path])

        # Read modified content
        with open(temp_path, 'r') as tmp_file:
            modified_contents = tmp_file.read()

        # Validate
        if validate_config_str(modified_contents):
            # Replace original file
            with open(original_path, 'w') as orig_file:
                orig_file.write(modified_contents)
            print("Changes applied successfully.")
        else:
            print("Validation failed. Original file unchanged.")
    finally:
        os.remove(temp_path)



def config_main():
    """
    Main function to load and print the configuration.
    """
    import fargv
    p = {
        "action": ("edit","reset", "view"),
    }
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    if args.action == "view":
        config = open(get_config_path()).read()
        print(config)
    elif args.action == "reset":
        config_path = get_config_path()
        default_config_path = Path(__file__).parent / "resources" / "default_config.toml"
        open(config_path, "w").write(open(default_config_path, "r").read())
        print(f"Configuration reset to default: {config_path}")
    elif args.action == "edit":
        edit_file_like_visudo(get_config_path())


def setup_main():
    """
    Main function to set up the configuration.
    """
    import fargv
    from crontab import CronTab
    import getpass
    p = {
        "archive_root": "/mnt/backup",
        "current_name": "current",
        "snapshots_name": "snapshots",
        "yearly_count": -1,
        "monthly_count": 12,
        "weekly_count": 5,
        "daily_count": 7,
        "hourly_count": 24
    }
    with CronTab(user=getpass.getuser()) as cron:
        cron.remove_all(comment="bkang-prune setup automatic")
        cron.remove_all(comment="bkang-sync setup automatic")
        cron.remove_all(comment="bkang-snapshot setup automatic")
        # cron.write() is implicitly called from the context manager
    edit_file_like_visudo(get_config_path())
    config = load_config()
    if config["mode"] in ["client", "local"]:
        if not test_ssh_noauth(host=config["archive_address"], port=22):
            print(f"SSH access to {config['archive_address']} failed. Please check your SSH keys. Aborting bkang setup.")
            return
        if config["sync_crontab_freq"].strip() != "":
            with CronTab(user=getpass.getuser()) as cron:
                # Add cron jobs for the client mode
                job = cron.new(command=f"bkang-sync", comment="bkang-sync setup automatic")
                job.setall(config["sync_crontab_freq"])
    if config["mode"] in ["server", "local"]:
        with CronTab(user=getpass.getuser()) as cron:
            # Add cron jobs for the server mode
            if config["prune_crontab_freq"].strip() != "":
                with CronTab(user=getpass.getuser()) as cron:
                    # Add cron jobs for the server mode
                    job = cron.new(command=f"bkang-prune", comment="bkang-prune setup automatic")
                    job.setall(config["prune_crontab_freq"])
            if config["snapshot_crontab_freq"].strip() != "":
                with CronTab(user=getpass.getuser()) as cron:
                    # Add cron jobs for the server mode
                    job = cron.new(command=f"bkang-prune", comment="bkang-prune setup automatic")
                    job.setall(config["prune_crontab_freq"])
