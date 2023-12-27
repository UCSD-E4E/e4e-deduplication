'''Test Setup
'''
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from random import randbytes, randint
from tempfile import TemporaryDirectory
from typing import Dict

import pytest
from nas_unzip.nas import nas_unzip
from utils import create_random_file

from e4e_deduplication.analyzer import Analyzer


@pytest.fixture(name='creds', scope='session')
def create_creds() -> Dict[str, str]:
    """Obtains the credentials

    Returns:
        Dict[str, str]: Username and password dictionary
    """
    if Path('credentials.json').is_file():
        with open('credentials.json', 'r', encoding='ascii') as handle:
            return json.load(handle)
    else:
        value = os.environ['NAS_CREDS'].splitlines()
        assert len(value) == 2
        return {
            'username': value[0],
            'password': value[1]
        }


@pytest.fixture(name='big_hash_cache', scope='session')
def get_big_hash_cache(creds) -> Path:
    """Retrieves the big hash cache

    Args:
        creds (Dict[str, str]): NAS Credentials

    Returns:
        Path: Path to data

    Yields:
        Iterator[Path]: Path to data
    """
    with TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir).resolve()
        if not Path('hashes.csv').is_file():
            nas_unzip(
                network_path=('smb://e4e-nas.ucsd.edu:6021/temp/github_actions/e4e-deduplication'
                              '/big_hash_cache.zip'),
                output_path=path,
                username=creds['username'],
                password=creds['password']
            )
        else:
            shutil.copy(Path('hashes.csv'), path / 'hashes.csv')
        yield path


@pytest.fixture(name='test_analyzer')
def create_test_analyzer():
    """Creates a clean test analyzer

    Yields:
        Analyzer: Test Analyzer app
    """
    with TemporaryDirectory() as cache_dir:
        job_path = Path(cache_dir, 'test')
        with Analyzer(ignore_pattern=None, job_path=job_path) as app:
            yield app


@pytest.fixture(name='test_file', params=['size'])
def create_test_file(request: pytest.FixtureRequest) -> Path:
    """Creates a test file with the specified size

    Args:
        size (int): Desired size of file

    Returns:
        Path: Path to test file

    Yields:
        Iterator[Path]: Path to test file
    """
    with TemporaryDirectory() as tmp_dir:
        temp_file = Path(tmp_dir, 'temp_file').resolve()
        size = request.param
        create_random_file(temp_file, size)
        yield temp_file


@dataclass
class TestDuplicatedSet:
    """Duplicated Files Test Set

    """
    reference_dir: Path
    dupe_dir: Path
    n_files: int
    n_dupes: int
    max_file_size: int

    def __post_init__(self):
        self.reference_dir = self.reference_dir.resolve()
        self.dupe_dir = self.dupe_dir.resolve()
        assert self.reference_dir.exists()
        assert self.dupe_dir.exists()

        for idx in range(self.n_files):
            file_size = randint(0, self.max_file_size)
            with open(self.reference_dir.joinpath(f'{idx:06d}'), 'wb') as handle:
                handle.write(randbytes(file_size))

        self.__duplicate_map = {}
        for idx in range(self.n_dupes):
            idx_to_dupe = randint(0, self.n_files - 1)
            file_to_duplicate = self.reference_dir.joinpath(
                f'{idx_to_dupe:06d}')
            dupe_file = self.dupe_dir.joinpath(f'dupe_{idx:06d}')
            shutil.copy(file_to_duplicate, dupe_file)
            self.__duplicate_map[dupe_file] = file_to_duplicate

    @property
    def duplicate_map(self) -> Dict[Path, Path]:
        """Retrieves the duplicated paths

        Returns:
            Dict[Path, Path]: Mapping of duplicated path to original path
        """
        return self.__duplicate_map


@pytest.fixture(name='subdir_dup')
def create_subdir_duplicates() -> TestDuplicatedSet:
    """Creates subdirectory duplicated test set

    Yields:
        TestDuplicatedSet: Test Set
    """
    with TemporaryDirectory() as refdir:
        ref_dir = Path(refdir).resolve()
        dupe_dir = ref_dir.joinpath('dupes')
        dupe_dir.mkdir()

        n_files = randint(0, 1024)
        n_dupes = randint(0, n_files)
        yield TestDuplicatedSet(
            reference_dir=ref_dir,
            dupe_dir=dupe_dir,
            n_files=n_files,
            n_dupes=n_dupes,
            max_file_size=4096
        )


@pytest.fixture(name='subdir_dup')
def create_sep_dir_duplicates() -> TestDuplicatedSet:
    """Creates separate directory test set

    Yields:
        TestDuplicatedSet: Test Set
    """
    with TemporaryDirectory() as refdir, TemporaryDirectory() as dupedir:
        ref_dir = Path(refdir).resolve()
        dupe_dir = Path(dupedir).resolve()

        n_files = randint(0, 1024)
        n_dupes = randint(0, n_files)
        yield TestDuplicatedSet(
            reference_dir=ref_dir,
            dupe_dir=dupe_dir,
            n_files=n_files,
            n_dupes=n_dupes,
            max_file_size=4096
        )


@dataclass
class MockAppDirs:
    """Mock AppDirs
    """
    user_data_dir: str
    user_cache_dir: str
    user_log_dir: str
    user_config_dir: str
    site_data_dir: str
    site_config_dir: str


@pytest.fixture(name='temp_appdirs')
def create_temp_appdirs():
    """Creates temporary appdirs

    Yields:
        MockAppDirs: Temporary AppDirs
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        app_dirs = MockAppDirs(
            user_data_dir=temp_dir.joinpath('user_data').as_posix(),
            user_cache_dir=temp_dir.joinpath('user_cache').as_posix(),
            user_log_dir=temp_dir.joinpath('user_log').as_posix(),
            user_config_dir=temp_dir.joinpath('user_config').as_posix(),
            site_data_dir=temp_dir.joinpath('site_data').as_posix(),
            site_config_dir=temp_dir.joinpath('site_config').as_posix()
        )
        yield app_dirs
