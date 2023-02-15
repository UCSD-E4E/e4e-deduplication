from argparse import ArgumentParser
from pathlib import Path

from cache import Cache
from directory import Directory
from report import Report


def _get_args():
    parser = ArgumentParser(
        description="Looks through a single directory and generates a list of duplicate files."
    )

    parser.add_argument(
        "-d", "--directory", type=str, required=True, help="The directory to work on."
    )

    args = parser.parse_args()
    directory_path = Path(args.directory)
    cache_path = Path(directory_path, "checksums.db")
    report_path = Path(directory_path, "report.csv")

    return directory_path, cache_path, report_path


def _generate_cache(directory: Directory, cache: Cache):
    for file in directory:
        cache.add_or_update_file(file, commit=False)

    cache.commit()


def main():
    directory_path, cache_path, report_path = _get_args()

    cache = Cache(cache_path.absolute(), directory_path.absolute())
    directory = Directory(directory_path.absolute())

    _generate_cache(directory, cache)

    report = Report(report_path.absolute(), cache)
    report.generate()


if __name__ == "__main__":
    main()
