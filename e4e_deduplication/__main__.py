"""
Provides a cli around the E4E deduplication module.
"""
from argparse import ArgumentParser
from pathlib import Path
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
    cache_path = Path(directory_path, "checksums.db").absolute()
    report_path = Path(directory_path, "report.csv").absolute()

    return directory_path, cache_path, report_path, set(args.exclude.split(","))


def _generate_cache(directory: Directory, cache: Cache) -> None:
    for idx, file in enumerate(directory):
        print(file.path)
        cache.add_or_update_file(file)

        if idx % 10:
            cache.commit()

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
