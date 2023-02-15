from pathlib import Path

from file import File


class Directory:
    def __init__(self, path: str, root: str = None):
        self._path = Path(path)
        self._file_iterator = None
        self._root = Path(root) if root else self._path

    def _get_files(self):
        for p in self._path.iterdir():
            if p.is_dir():
                for f in Directory(p.absolute(), root=self._root.absolute()):
                    yield f
            elif p.is_file():
                yield File(p.absolute(), self._root.absolute())
            else:
                raise NotImplementedError

    def __iter__(self):
        return self._get_files()
