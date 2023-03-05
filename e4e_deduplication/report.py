"""
Generates a report.csv file containing the duplicate items.
"""

from pathlib import Path
from typing import List, Set

from e4e_deduplication.file import File
from e4e_deduplication.cache import Cache


class Report:  # pylint: disable=too-few-public-methods
    """
    Generates a report.csv file containing the duplicate items.
    """

    def __init__(
        self,
        duplicate_folders_with_originals_path: Path,
        duplicates_without_originals_path: Path,
        cache: Cache,
        root: Path,
    ):
        self._duplicate_folders_with_originals_path = (
            duplicate_folders_with_originals_path
        )
        self._duplicates_without_originals_path = duplicates_without_originals_path
        self._cache = cache
        self._root = root

    def _find_common_folders(self, duplicates: Set[Path], nonduplicates: Set[Path]):
        duplicate_paths: Set[Path] = {}

        for dupe in duplicates:
            parent = dupe.parent

            if any(n.is_relative_to(parent) for n in nonduplicates):
                duplicate_paths.add(dupe)
                continue

            if parent not in duplicate_paths:
                duplicate_paths.add(parent)

        if len(duplicate_paths) == len(duplicates):
            return duplicates

        return self._find_common_folders(duplicate_paths, nonduplicates)

    def generate(self, original_paths: List[Path]) -> None:
        """
        Generates the report.csv file.
        """
        duplicates, nonduplicates = self._cache.get_duplicates()

        duplicates_with_originals = {
            d
            for d in duplicates
            if any(any(p.is_relative_to(o) for o in original_paths) for p in d)
        }
        duplicates_without_originals = duplicates.difference(duplicates_with_originals)
        collapsed_list_with_originals = {
            p for d in duplicates_with_originals for p in d if p not in original_paths
        }
        common_paths = [
            File(p, self._root)
            for p in self._find_common_folders(
                collapsed_list_with_originals, nonduplicates
            )
        ]

        duplicates_without_originals = [
            [File(p, self._root) for p in d] for d in duplicates_without_originals
        ]

        with open(
            self._duplicate_folders_with_originals_path.absolute(), "w", encoding="utf8"
        ) as file:
            for duplicate in common_paths:
                file.write(f"{duplicate.path}\n")

        with open(
            self._duplicates_without_originals_path.absolute(), "w", encoding="utf8"
        ) as file:
            for duplicate in duplicates_without_originals:
                for item in duplicate:
                    file.write(f"{item.path}, ")

                file.write("\n")
