'''Test Setup
'''
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from utils import create_random_file

from e4e_deduplication.analyzer import Analyzer


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
