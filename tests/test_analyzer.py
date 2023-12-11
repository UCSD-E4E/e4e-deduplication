'''Tests analyzer load
'''
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from e4e_deduplication.analyzer import Analyzer


def test_naive_jobfile():
    """Tests a jobfile with an empty dict
    """
    with TemporaryDirectory() as tmpdir:
        job_path = Path(tmpdir, 'job.json')
        with open(job_path, 'w', encoding='utf-8') as handle:
            json.dump({}, handle)
        with Analyzer(None, job_path) as analyzer:
            assert analyzer
