'''Test Setup
'''
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from e4e_deduplication.analyzer import Analyzer


@pytest.fixture(name='test_analyzer')
def create_test_analyzer():
    """Creates a clean test analyzer

    Yields:
        Analyzer: Test Analyzer app
    """
    with TemporaryDirectory() as cache_dir:
        job_path = Path(cache_dir, 'test.json')
        with Analyzer(ignore_pattern=None, job_path=job_path) as app:
            yield app
