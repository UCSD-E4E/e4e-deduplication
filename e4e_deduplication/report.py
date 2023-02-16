"""
Generates a report.csv file containing the duplicate items.
"""

from pathlib import Path

from e4e_deduplication.cache import Cache


class Report:  # pylint: disable=too-few-public-methods
    """
    Generates a report.csv file containing the duplicate items.
    """

    def __init__(self, path: Path, cache: Cache):
        self._path = path
        self._cache = cache

    def generate(self) -> None:
        """
        Generates the report.csv file.
        """
        duplicates = self._cache.get_duplicates()

        with open(self._path.absolute(), "w", encoding="utf8") as file:
            for duplicate in duplicates:
                for item in duplicate:
                    file.write(f"{item.path}, ")

                file.write("\n")
