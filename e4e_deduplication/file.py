"""
Represents a file.
"""
from hashlib import sha256
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
    def checksum(self) -> bytes:
        """
        Gets a sha256 checksum.
        This is recacluated everytime this function is called in case it changes.
        """

        print(f'Starting checksum on "{self.path}".')

        # We are opting to do this rather than using the built in method
        # because it was not supported in Python 3.8.
        checksum = sha256()
        with open(self._path.absolute(), "rb") as file:
            while True:
                buf = file.read(2**20)
                if not buf:
                    break
                checksum.update(buf)

        return checksum.digest()
