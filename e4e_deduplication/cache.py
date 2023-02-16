"""
Represents a database to keep track of checksums between runs.
"""

from pathlib import Path
from sqlite3 import connect
from typing import Dict, List

from e4e_deduplication.file import File


class Cache:
    """
    Represents a database to keep track of checksums between runs."""

    def __init__(self, path: str, root: str) -> None:
        self._root = root
        self._connection = connect(path)
        self._cursor = self._connection.cursor()

        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS files
            (name text, path text, size int, mtime float, checksum text)"""
        )

        self._connection.commit()

    def _item_in_cache(self, file: File) -> bool:
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files WHERE path = ?",
            (file.path,),
        )

        return any(results)

    def _add_item(self, file: File) -> None:
        self._cursor.execute(
            "INSERT INTO files VALUES (?, ?, ?, ?, ?)",
            (file.name, file.path, file.size, file.mtime, file.checksum),
        )

    def _update_item(self, file: File) -> None:
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files WHERE path = ?",
            (file.path,),
        )

        _, _, _, mtime, _ = list(results)[0]
        if mtime == file.mtime:
            return

        self._cursor.execute(
            """UPDATE files
                SET size = ?,
                    mtime = ?,
                    checksum = ?
                WHERE path = ?;""",
            (file.size, file.mtime, file.checksum, file.path),
        )

    def add_or_update_file(self, file: File, commit=True) -> None:
        """
        Adds or updates the specified File object in the cache.
        Only commits to file if commit==True.
        If commit==False, ensure to call .commit() separately.
        """
        if self._item_in_cache(file):
            self._update_item(file)
        else:
            self._add_item(file)

        if commit:
            self.commit()

    def get_duplicates(self) -> List[List[File]]:
        """
        Gets a list of all of the duplicate file objects in the cache.
        """
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files"
        )

        files_by_checksum: Dict[str, List[str]] = {}
        for _, path, _, _, checksum in results:
            if checksum not in files_by_checksum:
                files_by_checksum[checksum] = []

            files_by_checksum[checksum].append(path)

        return [
            [File(Path(self._root, f), self._root) for f in v]
            for _, v in files_by_checksum.items()
            if len(v) > 1
        ]

    def commit(self) -> None:
        """
        Commits the cache to file.
        """
        self._connection.commit()
