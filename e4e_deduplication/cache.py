from sqlite3 import connect
from typing import Dict, List, Tuple

from file import File


class Cache:
    def __init__(self, path: str, root: str):
        self._root = root
        self._connection = connect(path)
        self._cursor = self._connection.cursor()

        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS files
            (name text, path text, size int, mtime float, checksum text)"""
        )

        self._connection.commit()

    def _item_in_cache(self, file: File):
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files WHERE path = ?",
            (file.path,),
        )

        return any(results)

    def _add_item(self, file: File):
        self._cursor.execute(
            "INSERT INTO files VALUES (?, ?, ?, ?, ?)",
            (file.name, file.path, file.size, file.mtime, file.checksum),
        )

    def _update_item(self, file: File):
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files WHERE path = ?",
            (file.path,),
        )

        _, _, _, mtime, _ = [r for r in results][0]
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

    def add_or_update_file(self, file: File, commit=True):
        if self._item_in_cache(file):
            self._update_item(file)
        else:
            self._add_item(file)

        if commit:
            self.commit()

    def get_duplicates(self):
        results = self._cursor.execute(
            "SELECT name, path, size, mtime, checksum FROM files"
        )

        files_by_checksum: Dict[str, List[str]] = {}
        for _, path, _, _, checksum in results:
            if checksum not in files_by_checksum:
                files_by_checksum[checksum] = []

            files_by_checksum[checksum].append(path)

        return [
            [File(f"{self._root}/{f}", self._root) for f in v]
            for _, v in files_by_checksum.items()
            if len(v) > 1
        ]

    def commit(self):
        self._connection.commit()
