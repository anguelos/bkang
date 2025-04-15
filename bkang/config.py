from pathlib import Path
from typing import Any
import toml
import importlib.resources as pkg_resources
from . import resources


def load_config() -> dict:
    """
    Load the configuration file.
    """
    config_path = Path(__file__).parent / "resources" / "config.toml"
    if not config_path.is_file():
        config_path = Path(__file__).parent / "resources" / "default_config.toml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")    
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
    """
    Update the fargv dictionary with the configuration.
    """
    config = load_config()
    for key, value in config.items():
        if key in d:
            d[key] = value
    return d


def update_config_from_fargv(args: Any) -> dict:
    config_d = load_config()
    for key, value in args.__dict__.items():
        if key in config_d:
            config_d[key] = value
    save_config(config_d)
    return config_d


def config_file_is_valid(config_file: str) -> bool:
    default_config_path = Path(__file__).parent / "resources" / "default_config.toml"
    with open(default_config_path, "r") as f:
        default_config = toml.load(f)
    with open(config_file, "r") as f:
        config = toml.load(f)
    if set(config.keys()) != set(default_config.keys()):
        return False
    for key, value in default_config.items():
        if type(value) != type(config[key]):
            return False
    return True


def config_main():
    """
    Main function to load and print the configuration.
    """
    import fargv
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
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    config = load_config()
    print(config)


def setup_main():
    """
    Main function to set up the configuration.
    """
    import fargv
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
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    config = update_config_from_fargv(args)
    print(config)
