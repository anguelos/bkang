from functools import wraps
import fcntl
from pathlib import Path
import tempfile
import subprocess
import sys
from typing import IO, Union
import toml
import json
import os


def single_instance_aborting(lock_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lock_file_path = os.path.join(tempfile.gettempdir(), f"{lock_name}.lock")
            with open(lock_file_path, "w") as lock_file:
                try:
                    # Try to acquire exclusive lock (non-blocking)
                    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    print(f"[Lock acquired: {lock_name}]")
                    return func(*args, **kwargs)
                except BlockingIOError:
                    print(f"[Already running: {lock_name}]")
                    return None  # Or raise, or log, depending on use case
        return wrapper
    return decorator


def get_cmd_output(cmd: str, show_cmd: bool = True, show_output: bool = True, output_file: IO = sys.stdout, dry_run: bool = False) -> str:
    """
    Get the output of a command.
    """
    if show_cmd:
        print(cmd, file=output_file)
    if dry_run:
        result = "NA"
    else:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if show_output:
        print(result.stdout, file=output_file)
    return result.stdout.strip()


def mkdir_p(path: Union[str, Path]) -> None:
    """
    Create a directory if it does not exist.
    """
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
