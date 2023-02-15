from pathlib import Path

from cache import Cache


class Report:
    def __init__(self, path: str, cache: Cache):
        self._path = Path(path)
        self._cache = cache

    def generate(self):
        duplicates = self._cache.get_duplicates()

        with open(self._path.absolute(), "w") as f:
            for duplicate in duplicates:
                for item in duplicate:
                    f.write(f"{item.path}, ")

                f.write("\n")
