'''Test Setup
'''
import json
import os
import shutil
from pathlib import Path
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
