"""
Represents a file.
"""

import hashlib
from pathlib import Path


class File:
    """
    Represents a file.
    """

    def __init__(self, path: Path, root: Path) -> None:
        self._path = path
        self._root = root

    @property
    def size(self) -> int:
        """
        File size in bytes.
        """
        return self._path.lstat().st_size

    @property
    def name(self) -> str:
        """
        The name of the file.
        """
        return self._path.name

    @property
    def path(self) -> str:
        """
        The path to the file relative to the root directory.
        This is also the path that will be relative to the cache.db
        """
        return self._path.relative_to(self._root).as_posix()

    @property
    def mtime(self) -> float:
        """
        Gets the last modified time.
        """
        return self._path.lstat().st_mtime

    @property
    def checksum(self) -> str:
        """
        Gets a sha256 checksum.  This is recacluated everytime this function is called in case it changes.
        """
        with open(self._path, "rb") as f:
            checksum = hashlib.file_digest(f, "sha256")

        return checksum.hexdigest()
