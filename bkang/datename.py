import datetime
from typing import Dict, List, Optional, Self, Tuple, Union
from pathlib import Path


class Datename:
    __date_str_format = "%Y-%m-%d-%H-%M-%S"

    def _get_date_str(self, date: Optional[Self] = None) -> str:
        """
        Get a string representation of the date.
        """
        if date is None:
            date = datetime.datetime.now()
        return date.strftime(self.__date_str_format)


    def _parse_date_str(self, date_str: str) -> Dict[str, int]:
        """
        Parse a date string into a dictionary.
        """
        try:
            date = datetime.datetime.strptime(date_str, self.__date_str_format)
            return {
                "year": date.year,
                "month": date.month,
                "day": date.day,
                "hour": date.hour,
                "minute": date.minute,
                "second": date.second
            }
        except ValueError:
            raise ValueError(f"Invalid date string: {date_str}")

    @staticmethod
    def path_to_datename(s: Union[Path, str]) -> Self:
        """
        Convert a string to a Datename object.
        """
        if isinstance(s, str):
            s = Path(s)
        date_str = s.stem
        return Datename(date_str)
    
    @staticmethod
    def is_valid_date_str(date_str: str) -> bool:
        """
        Check if a date string is valid.
        """
        try:
            date = datetime.datetime.strptime(date_str, Datename.__date_str_format)
            return True
        except ValueError:
            return False
    
    def __init__(self, date: Union[Path, str, Self, int, None] = None) -> None:
        if date is None:
            self.date_str = self._get_date_str()
        elif isinstance(date, Path):
            date_str = date.stem
            self.date_str = date_str
        elif isinstance(date, str):
            self.date_str = date
        elif isinstance(date, datetime.datetime):
            self.date_str = self._get_date_str(date)
        elif isinstance(date, Datename):
            self.date_str = date.date_str
        elif isinstance(date, int):
            unix_time = date
            date = datetime.datetime.fromtimestamp(unix_time)
            self.date_str = self._get_date_str(date)
        else:
            raise ValueError(f"Invalid date type: {type(date)}")
        # Validate the date string
        _ = self._parse_date_str(self.date_str)
    
    @property
    def unix_time(self) -> int:
        return int(datetime.datetime.strptime(self.date_str, self.__date_str_format).timestamp())


    def __str__(self) -> str:
        return self.date_str
    
    def __repr__(self) -> str:
        return f"DateName({self.date_str})"
    
    def __sub__(self, other: Self) -> Self:
        other = Datename(other)
        return Datename(self.unix_time - other.unix_time)
    
    def __add__(self, other: Self) -> int:
        other = Datename(other)
        return Datename(self.unix_time + other.unix_time)
    
    def __eq__(self, other: Self) -> bool:
        other = Datename(other)
        return self.date_str == other.date_str
    
    def __lt__(self, other: Self) -> bool:
        other = Datename(other)
        return self.unix_time < other.unix_time
    
    def __le__(self, other: Self) -> bool:
        other = Datename(other)
        return self.unix_time <= other.unix_time
    
    def __gt__(self, other: Self) -> bool:
        other = Datename(other)
        return self.unix_time > other.unix_time
    
    def __ge__(self, other: Self) -> bool:
        other = Datename(other)
        return self.unix_time >= other.unix_time
    
    def __ne__(self, other: Self) -> bool:
        other = Datename(other)
        return self.date_str != other.date_str
    
    def __hash__(self) -> int:
        return hash(self.date_str)
    
    def __int__(self) -> int:
        return self.unix_time
    
    def pretty(self) -> str:
        """
        Pretty print the date.
        """
        date = datetime.datetime.strptime(self.date_str, self.__date_str_format)
        return date.strftime("%a %d %b %Y %H:%M")
    
    @classmethod
    def one_year(cls) -> str:
        # any date would do
        return Datename("2024-01-01-00-00-00") - Datename("2023-01-01-00-00-00")

    @classmethod
    def one_month(cls) -> str:
        # any date would do
        return Datename("2023-02-01-00-00-00") - Datename("2023-01-01-00-00-00")

    @classmethod
    def one_week(cls) -> str:
        # any date would do
        return Datename("2023-01-08-00-00-00") - Datename("2023-01-01-00-00-00")
    
    @classmethod
    def one_day(cls) -> str:
        # any date would do
        return Datename("2023-01-08-00-00-00") - Datename("2023-01-01-00-00-00")
    
    @classmethod
    def one_hour(cls) -> str:
        # any date would do
        return Datename("2023-01-01-01-00-00") - Datename("2023-01-01-00-00-00")
    
    @classmethod
    def one_minute(cls) -> str:
        # any date would do
        return Datename("2023-01-01-00-01-00") - Datename("2023-01-01-00-00-00")


def get_prune_list(snapshots: List[Path], yearly_count: int = -1, monthly_count: int = 12, weekly_count: int = 5, daily_count: int = 7, hourly_count: int = 24, minute_count: int = 0) -> Tuple[List[Path], List[Path]]:
        old_to_new_snapshots = list((sorted(snapshots.copy())))
        if len(old_to_new_snapshots) == 0:
            return [], []
        keep = [old_to_new_snapshots[0]]
        keep_years = [old_to_new_snapshots[0]]
        keep_months = [keep[0]]
        keep_weeks = [keep[0]]
        keep_days = [keep[0]]
        keep_hours = [keep[0]]
        keep_minutes = [keep[0]]
        for snapshot in old_to_new_snapshots[1:]:
            snapshot_date = Datename(snapshot.name)
            if (yearly_count < 0 or len(keep_years) < yearly_count) and snapshot_date - Datename(keep_years[-1]) >= Datename.one_year():
                keep_years.append(snapshot)
            if (monthly_count < 0 or len(keep_months) < monthly_count) and snapshot_date - Datename(keep_months[-1]) >= Datename.one_month():
                keep_months.append(snapshot)
            if (weekly_count < 0 or len(keep_weeks) < weekly_count) and snapshot_date - Datename(keep_weeks[-1]) >= Datename.one_week():
                keep_weeks.append(snapshot)
            if (daily_count < 0 or len(keep_days) < daily_count) and snapshot_date - Datename(keep_days[-1]) >= Datename.one_day():
                keep_days.append(snapshot)
            if (hourly_count < 0 or len(keep_hours) < hourly_count) and snapshot_date - Datename(keep_hours[-1]) >= Datename.one_hour():
                keep_hours.append(snapshot)
            if (minute_count < 0 or len(keep_minutes) < minute_count) and  snapshot_date - Datename(keep_minutes[-1]) >= Datename.one_minute():
                keep_minutes.append(snapshot)
        keep = keep_years + keep_months + keep_weeks + keep_days + keep_hours + keep_minutes
        keep = set(keep)
        prune = set(old_to_new_snapshots) - keep
        prune = [str(s) for s in prune]
        keep = [str(s) for s in keep]
        return list(prune), list(keep)


def list_prune_main():
    from .config import update_fargv_dict
    from .util import get_cmd_output, single_instance_aborting
    import fargv
    import glob
    import sys
    p = {
        "archive_root": "./",
        "snapshots_name": "snapshots",
        "yearly_count": -1,
        "monthly_count": 12,
        "weekly_count": 5,
        "daily_count": 7,
        "hourly_count": 24,
        "verbose": 1,
        "no_dry_run": False,
        "fstype": ("btrfs", "hardlinks")
    }
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    if args.no_dry_run:
        assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
    snapshots = glob.glob(f"{args.archive_root}/{args.snapshots_name}/*")
    snapshots = [Path(s) for s in snapshots]
    snapshots = [s for s in snapshots if s.is_dir() and Datename.is_valid_date_str(s.name)]
    prune, keep = get_prune_list(snapshots, args.yearly_count, args.monthly_count, args.weekly_count, args.daily_count, args.hourly_count)
    if args.verbose > 0:
        print(f"Snapshots to prune:\n\t{'\n\t'.join(prune)}", "\n", file=sys.stderr)
        print(f"Snapshots to keep:\n\t{'\n\t'.join(keep)}", "\n", file=sys.stderr)
    for snapshot in prune:
        if args.mode == "list":
            res_str = f"{snapshot}"
        elif args.mode == "btrfs":
            res_str = f"btrfs subvolume delete {snapshot}"
        elif args.mode == "hardlinks":
            res_str = f"rm -Rf {snapshot}"
        else:
            raise ValueError(f"Invalid mode: {args.mode}")
        if args.no_dry_run:
            @single_instance_aborting("prune_snapshot")
            def prune_snapshot():
                get_cmd_output(res_str, show_cmd=False, show_output=True)
            prune_snapshot()
        else:
            print(res_str, file=sys.stdout)


def sync_current_main():
    from .config import update_fargv_dict
    from .util import get_cmd_output, single_instance_aborting
    import fargv
    import glob
    import sys
    p = {
        "archive_address": "127.0.0.1",
        "backup_src": "/home/",
        "archive_root": "./",
        "current_name": "current",
        "verbose": 1,
        "no_dry_run": False,
        "mode": ("btrfs", "hardlinks")
    }
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    if args.no_dry_run:
        assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
    if args.backup_src.endswith("/"):
        args.backup_src = args.input[:-1]
    if args.archive_root.endswith("/"):
        args.archive_root = args.archive_root[:-1]
    if args.current_name.endswith("/"):
        args.current_name = args.current_name[:-1]
    cmd = f"rsync -aAXH --delete {args.backup_src}/ {args.archive_address}:{args.archive_root}/{args.current_name}{args.backup_src}/"
    if args.no_dry_run:
        assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
        @single_instance_aborting("sync_current")
        def sync_current():
            get_cmd_output(cmd, show_cmd=True, show_output=True)
        sync_current()
    else:
        print(cmd, file=sys.stdout)


def take_snapshot_main():
    from .config import update_fargv_dict
    from .util import get_cmd_output, single_instance_aborting
    import fargv
    import glob
    import sys
    p = {
        "archive_root": "./",
        "current_name": "current",
        "snapshots_name": "snapshots",
        "no_dry_run": False,
        "fstype": ("btrfs", "hardlinks")
    }
    update_fargv_dict(p)
    args, _ = fargv.fargv(p)
    if args.no_dry_run:
        assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
    if args.archive_root.endswith("/"):
        args.archive_root = args.archive_root[:-1]
    if args.current_name.endswith("/"):
        args.current_name = args.current_name[:-1]
    if args.snapshots_name.endswith("/"):
        args.snapshots_name = args.snapshots_name[:-1]
    if args.fstype == "btrfs":
        cmd = f"btrfs subvolume snapshot {args.archive_root}/{args.current_name} {args.archive_root}/{args.snapshots_name}/{str(Datename())}"
        if args.no_dry_run:
            assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
            get_cmd_output(cmd, show_cmd=False, show_output=True)
        else:
            print(cmd, file=sys.stdout)
    elif args.fstype == "hardlinks":
        cmd = f"cp --link -a {args.archive_root}/{args.current_name} {args.archive_root}/{args.snapshots_name}/{str(Datename())}"
        if args.no_dry_run:
            assert args.archive_root.startswith("/"), "Only absolute paths are allowed when not dry running."
            @single_instance_aborting("take_snapshot_main")
            def take_snapshot_main():
                get_cmd_output(cmd, show_cmd=True, show_output=True)
            take_snapshot_main()
        else:
            print(cmd, file=sys.stdout)
    else:
        raise ValueError(f"Invalid fstype: {args.fstype}")
