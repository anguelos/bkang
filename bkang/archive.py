from abc import ABC, abstractmethod
import os
from typing import Dict, List, Optional, Self, Tuple, Union
from pathlib import Path
from datetime import datetime
import shutil

from .util import single_instance_aborting, get_cmd_output
from .datename import Datename



class AstractArchive(ABC):
    """
    Abstract class for creating and managing archives.
    """    

    @classmethod
    def path_to_datename(cls, path: Union[Path, str]) -> Datename:
        """
        Convert a path to a date string.
        """
        if isinstance(path, str):
            path = Path(path)
        assert path.is_directory()
        date_str = path.stem
        return Datename(date_str)
    
    def requirements_installed(self) -> bool:
        """
        Check if the archive can run.
        """
        if os.name != "posix":
            return False
        if not shutil.which("rsync"):
            return False
        if not self.archive_root.is_dir():
            return False
        if not self.current_path.is_dir():
            return False
        if not self.snapshots_path.is_dir():
            return False
        return True
    
    def init_dirs(self):
        try:
            self.archive_root.mkdir(parents=True, exist_ok=True)
            self.current_path.mkdir(parents=True, exist_ok=True)
            self.snapshots_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise Exception(f"Error creating directories: {e}")

    def __init__(self, archive_root: Union[str, Path], current_name: str = "current", snapshots_name: str = "snapshots", yearly_count: int = -1, monthly_count: int = 12, weekly_count: int = 5, daily_count: int = 7, hourly_count: int = 24) -> None:
        if isinstance(archive_root, str):
            archive_root = Path(archive_root)
        self.archive_root: Path = archive_root
        self.current_name: str = current_name
        self.snapshots_name: str = snapshots_name
        self.yearly_count: int = yearly_count
        self.montly_count: int = monthly_count
        self.weekly_count: int = weekly_count
        self.daily_count: int  = daily_count
        self.hourly_count: int = hourly_count
        self.init_dirs()
        assert self.requirements_installed(), "Requirements not installed"
    
    @property
    def current_path(self) -> Path:
        """
        Get the path of the archive where currents are accumulated.
        """
        return self.archive_root / self.current_name

    @property
    def snapshots_path(self) -> Path:
        """
        Get the path of the archive where snapshots are stored.
        """
        return self.archive_root / self.snapshots_name

    def list_snapshots(self) -> List[Path]:
        """
        List all snapshots in the archive.
        """
        return sorted(self.archive_root.glob("**/*"))

    def get_prune_snapshots(self) -> Tuple[List[Path], List[Path]]:
        """
        Get snapshots to prune.
        """
        old_to_new_snapshots = self.list_snapshots()
        keep = [old_to_new_snapshots[0]]
        keep_years = [old_to_new_snapshots[0]]
        keep_months = [Datename(keep[0])]
        keep_weeks = [Datename(keep[0])]
        keep_days = [Datename(keep[0])]
        keep_hours = [Datename(keep[0])]
        keep_minutes = [Datename(keep[0])]

        for snapshot in old_to_new_snapshots[1:]:
            snapshot_date = Datename(snapshot)
            if (self.yearly_count < 0 or len(keep_years) < self.yearly_count) and Datename(keep_years[-1]) - snapshot_date > Datename.one_year():
                keep_years.append(snapshot_date)
            if (self.montly_count < 0 or len(keep_months) < self.montly_count) and Datename(keep_months[-1]) - snapshot_date > Datename.one_month():
                keep_months.append(snapshot_date)
            if (self.weekly_count < 0 or len(keep_weeks) < self.weekly_count) and Datename(keep_weeks[-1]) - snapshot_date > Datename.one_week():
                keep_weeks.append(snapshot_date)
            if (self.daily_count < 0 or len(keep_days) < self.daily_count) and Datename(keep_days[-1]) - snapshot_date > Datename.one_day():
                keep_days.append(snapshot_date)
            if (self.hourly_count < 0 or len(keep_hours) < self.hourly_count) and Datename(keep_hours[-1]) - snapshot_date > Datename.one_hour():
                keep_hours.append(snapshot_date)
            if (self.minute_count < 0 or len(keep_minutes) < self.minute_count) and Datename(keep_minutes[-1]) - snapshot_date > Datename.one_minute():
                keep_minutes.append(snapshot_date)
        keep = keep_years + keep_months + keep_weeks + keep_days + keep_hours + keep_minutes
        keep = set(keep)
        prune = set(old_to_new_snapshots) - keep
        return list(prune), list(keep)

    def get_update_current_cmdstr(self, src: str) -> None:
        """
        Update the current archive.
        """
        return f"rsync -aAXH --delete {src}/ {str(self.current_path)}/"


    @abstractmethod
    def get_create_snapshot_cmd(self) -> str:
        """
        Create a snapshot of the archive.
        """
        pass

    @abstractmethod
    def get_delete_snapshot_cmd(self, snapshot_path: Union[str, Path]) -> str:
        """
        Delete files from the archive.
        """
        pass

    def create_snapshot(self, src: str, dryrun: bool = True) -> None:
        """
        Create a snapshot of the archive.
        """
        cmd = self.get_create_snapshot_cmd()
        os.system(cmd)