"""
Provides a cli around the E4E deduplication module.
"""
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter
from typing import Set, Tuple

from e4e_deduplication.cache import Cache
from e4e_deduplication.directory import Directory
from e4e_deduplication.report import Report


def _get_args() -> Tuple[Path, Path, Path, Set[Path], bool]:
    parser = ArgumentParser(
        description="Looks through a single directory and generates a list of duplicate files."
    )

    parser.add_argument(
        "-d", "--directory", type=Path, required=True, help="The directory to work on."
    )

    parser.add_argument(
        "-e", "--exclude", type=str, default="", help="Paths to exclude."
    )

    parser.add_argument(
        "-s",
        "--skip-recheck",
        action="store_true",
        help="Skips updating files in the cache.",
    )

    parser.add_argument(
        "-o",
        "--originals",
        type=str,
        default="",
        help="Directories to consider original.",
    )

    args = parser.parse_args()
    directory_path = args.directory.absolute()
    cache_path = Path(directory_path, "checksums.db.7z").absolute()
    duplicate_folders_with_originals_path = Path(
        directory_path, "duplicate_folders_with_originals.csv"
    ).absolute()
    duplicates_without_originals_path = Path(
        directory_path, "duplicates_without_originals.csv"
    ).absolute()

    return (
        directory_path,
        cache_path,
        duplicate_folders_with_originals_path,
        duplicates_without_originals_path,
        {Path(directory_path, exclude) for exclude in args.exclude.split(",")},
        {Path(directory_path, original) for original in args.originals.split(",")},
        args.skip_recheck,
    )


def _seconds_to_minutes(seconds: float):
    return seconds / 60


def _generate_cache(directory: Directory, cache: Cache) -> None:
    start_time = perf_counter()
    dirty = False
    for idx, file in enumerate(directory):
        print(file.path)
        dirty = dirty or cache.add_or_update_file(file)

        # Avoid the overhead of committing when nothing has changed.
        if not dirty:
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
    (
        directory_path,
        cache_path,
        duplicate_folders_with_originals_path,
        duplicates_without_originals_path,
        excluded_paths,
        original_paths,
        skip_mtime_recheck,
    ) = _get_args()

    directory = Directory(directory_path, excluded_paths)

    with Cache(
        cache_path, directory_path, skip_mtime_check=skip_mtime_recheck
    ) as cache:
        cache.log_run(directory, excluded_paths, original_paths, skip_mtime_recheck)
        _generate_cache(directory, cache)

        report = Report(duplicate_folders_with_originals_path, duplicates_without_originals_path, cache)
        report.generate()


if __name__ == "__main__":
    main()
