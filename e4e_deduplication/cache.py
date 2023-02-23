"""
Represents a database to keep track of checksums between runs.
"""
from pathlib import Path
from sqlite3 import Connection, Cursor, connect
from typing import Dict, List

import py7zr

from e4e_deduplication.file import File


class Cache:
    """
    Represents a database to keep track of checksums between runs."""

    def __init__(self, path: Path, root: Path, skip_mtime_check=False) -> None:
        self._path = path
        self._root = root
        self._cache_root = Path(Path.home(), ".cache", "e4e", "deduplication")
        self._cache_root.mkdir(exist_ok=True, parents=True)
        self._cache_path = Path(self._cache_root, path.name[:-3])

        self._skip_mtime_check = skip_mtime_check

        self._connection: Connection = None
        self._cursor: Cursor = None

    def __enter__(self):
        # If we have a valid checksums.db file,
        # let's use it as a starting point.
        if self._path.exists() and (
            not self._does_cache_exist()
            or self._path.lstat().st_mtime > self._cache_path.lstat().st_mtime
        ):
            with py7zr.SevenZipFile(self._path, "r") as archive:
                archive.extractall(self._cache_root)

        self._connection = connect(self._cache_path)
        self._cursor = self._connection.cursor()

        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS files
            (name text, path text, size int, mtime float, checksum blob, seen integer)"""
        )

        self._cursor.execute(
            """CREATE TABLE IF NOT EXISTS metadata
            (key text, value text)"""
        )

        # This adds the RootPath property if it does not already exist.
        results = list(
            self._cursor.execute(
                "SELECT key, value FROM metadata WHERE key = 'RootPath'"
            )
        )
        if not results:
            self._cursor.execute(
                "INSERT INTO metadata VALUES ('RootPath', ?)", (self._root.as_posix(),)
            )

        self._connection.commit()

        results = self._cursor.execute("SELECT path, mtime FROM files")

        return self

    def __exit__(self, *args) -> None:
        self.commit()
        self._cursor.close()

        # This is intended to replace the file within the archive if it already exists.
        # This is to get around the recycle bin on Synology.
        with py7zr.SevenZipFile(self._path, "w") as archive:
            archive.write(self._cache_path)

        # Cleanup after ourselves.
        # The existance of the checksums.db is an indication that we did not complete successfully.
        self._cache_path.unlink()

    def __contains__(self, file: File) -> bool:
        results = self._cursor.execute(
            "SELECT seen WHERE path = ?",
            (file.path,),
        )

        return any(results)

    def _does_cache_exist(self) -> bool:
        if not self._cache_path.exists():
            return False

        with connect(self._cache_path) as connection:
            cursor = connection.cursor()
            results = list(
                cursor.execute("SELECT value FROM metadata WHERE key = 'RootPath'")
            )
            value = None
            if results:
                value = results[0]

                return value == self._root.as_posix()

            # The metadata key for the RootPath is missing.
            return False

    def _add_item(self, file: File) -> None:
        # This encurs the cost of calculating the checksum.
        self._cursor.execute(
            "INSERT INTO files VALUES (?, ?, ?, ?, ?, 1)",
            (file.name, file.path, file.size, file.mtime, file.checksum),
        )

    def _update_item(self, file: File) -> bool:
        # If we are not changing files, then this isn't necessary.
        if self._skip_mtime_check:
            return False

        results = self._cursor.execute(
            "SELECT mtime FROM files WHERE path = ?",
            (file.path,),
        )

        # We don't want to recalculate the checksum if the file hasn't changed.
        mtime = list(results)[0]
        if mtime == file.mtime:
            return False

        # Calling this incurs the penalty of recalcuating the checksum.
        self._cursor.execute(
            """UPDATE files
                SET size = ?,
                    mtime = ?,
                    checksum = ?,
                    seen = 1
                WHERE path = ?;""",
            (file.size, file.mtime, file.checksum, file.path),
        )

        return True

    def add_or_update_file(self, file: File, commit=True) -> bool:
        """
        Adds or updates the specified File object in the cache.
        Only commits to file if commit==True.
        If commit==False, ensure to call .commit() separately.
        """
        updated = False
        if file in self:
            updated = self._update_item(file)
        else:
            self._add_item(file)
            updated = True

        # We may wish to commit to the database elsewhere.
        if commit:
            self.commit()

        return updated

    def get_duplicates(self) -> List[List[File]]:
        """
        Gets a list of all of the duplicate file objects in the cache.
        """
        results = self._cursor.execute("SELECT path, checksum FROM files")

        # Use checksums as the indicator if the file is the same.
        # This helps us account for files that were copied later, or files with different names.
        files_by_checksum: Dict[bytes, List[str]] = {}
        for path, checksum in results:
            if checksum not in files_by_checksum:
                files_by_checksum[checksum] = []

            files_by_checksum[checksum].append(path)

        # Filter to a list where we only have checksums with duplicates.
        return [
            [File(Path(self._root, f), self._root) for f in v]
            for _, v in files_by_checksum.items()
            if len(v) > 1
        ]

    def clear_deleted(self) -> None:
        """
        Removes files that were not seen this run.
        That means they were deleted or renamed.
        """
        # These are files we did not see this run.
        self._cursor.execute("DELETE FROM files WHERE seen = 0")

        self.commit()

    def commit(self) -> None:
        """
        Commits the cache to file.
        """
        self._connection.commit()
