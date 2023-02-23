"""
Provides a cli around the E4E deduplication module.
"""
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from typing import Tuple

from e4e_deduplication.cache import Cache
from e4e_deduplication.directory import Directory
from e4e_deduplication.report import Report


def _get_args() -> Tuple[Path, Path, Path]:
    parser = ArgumentParser(
        description="Looks through a single directory and generates a list of duplicate files."
    )

    parser.add_argument(
        "-d", "--directory", type=Path, required=True, help="The directory to work on."
    )

    parser.add_argument(
        "-e", "--exclude", type=str, default="", help="Paths to exclude."
    )

    args = parser.parse_args()
    directory_path = args.directory.absolute()
    cache_path = Path(directory_path, "checksums.db.7z").absolute()
    report_path = Path(directory_path, "report.csv").absolute()

    return directory_path, cache_path, report_path, set(args.exclude.split(","))


def _seconds_to_minutes(seconds: float):
    return seconds / 60


def _generate_cache(directory: Directory, cache: Cache) -> None:
    start_time = perf_counter()
    dirty = False
    for idx, file in enumerate(directory):
        if file not in cache:
            print(file.path)
        updated = cache.add_or_update_file(file)
        dirty = dirty or updated

        # Avoid the overhead of committing when nothing has changed.
        if not updated and not dirty:
            continue

        # Commit every 10 minutes or every 10 items.
        # Whichever is first.  Some files take a long time to checksum.
        if idx % 10 or _seconds_to_minutes(start_time - perf_counter()) >= 10:
            start_time = perf_counter()
            cache.commit()
            dirty = False

    cache.clear_deleted()
    cache.commit()


def main() -> None:
    """
    Entry point for the CLI.
    """
    directory_path, cache_path, report_path, excluded_files = _get_args()

    directory = Directory(directory_path, excluded_files)

    with Cache(cache_path, directory_path) as cache:
        _generate_cache(directory, cache)

        report = Report(report_path, cache)
        report.generate()


if __name__ == "__main__":
    main()
