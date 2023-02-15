import os
from hashlib import sha256
from pathlib import Path


class File:
    def __init__(self, path: str, root: str):
        self._path = Path(path)
        self._root = Path(root)

    @property
    def size(self):
        return os.path.getsize(self._path)

    @property
    def name(self):
        return self._path.name

    @property
    def path(self):
        return f'./{"/".join(self._path.relative_to(self._root).parts)}'

    @property
    def mtime(self):
        return os.path.getmtime(self._path)

    @property
    def checksum(self):
        checksum = sha256()
        with open(self._path.absolute(), "rb") as f:
            while True:
                buf = f.read(2**20)
                if not buf:
                    break
                checksum.update(buf)

        return checksum.hexdigest()
