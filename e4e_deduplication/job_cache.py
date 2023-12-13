'''Job Cache
'''
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Dict, Set


class JobCache:
    """Sqlite3 backed job cache
    """

    def __init__(self, path: Path) -> None:
        self.__db_path = path

    def __enter__(self) -> JobCache:
        self.open()
        return self

    def open(self):
        """Opens the cache
        """
        self.__create_table()

    def __exit__(self, exc, exv, exp) -> None:
        self.close()

    def close(self):
        """Closes the cache
        """

    def __create_table(self) -> None:
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            cur.execute(
                'CREATE TABLE IF NOT EXISTS hash_cache(path text, digest text)')

    def __contains__(self, digest: str) -> bool:
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            res = cur.execute(
                f"SELECT * FROM hash_cache where digest = '{digest}'")
            return res.fetchone() is not None

    def __getitem__(self, digest: str) -> Set[Path]:
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            res = cur.execute(
                f'SELECT path FROM hash_cache where digest = "{digest}"'
            )
            return {Path(row[0]) for row in res.fetchall()}

    def add(self, path: str, digest: str):
        """Adds the path and digest to the job cache

        Args:
            path (Path): Path of file
            digest (str): File digest
        """
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            cur.execute(
                f'INSERT INTO hash_cache VALUES ("{Path(path).as_posix()}", "{digest}")')
            _db.commit()

    def get_duplicates(self) -> Dict[str, Set[Path]]:
        """Generates the mapping of duplicates

        Returns:
            Dict[str, Set[Path]]: duplicates mapping
        """
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            res = cur.execute('SELECT digest, path FROM hash_cache f1 WHERE digest IN '
                              '(SELECT digest FROM hash_cache f2 WHERE f1.path <> f2.path)')
            rows = res.fetchall()
        result: Dict[str, Set[Path]] = {}
        for digest, path in rows:
            if digest not in result:
                result[digest] = {Path(path)}
            else:
                result[digest].add(Path(path))
        return result

    def clear(self) -> None:
        """Clears the job cache
        """
        with sqlite3.connect(self.__db_path) as _db, closing(_db.cursor()) as cur:
            cur.execute('DELETE FROM hash_cache')
            _db.commit()
