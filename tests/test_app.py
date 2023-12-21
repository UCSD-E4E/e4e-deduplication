'''Tests Application
'''
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from conftest import MockAppDirs, TestDuplicatedSet

from e4e_deduplication.app import Deduplicator


def test_dedup_same_dir(subdir_dup: TestDuplicatedSet, temp_appdirs: MockAppDirs):
    """Tests dedup app on same dir with default os script

    Args:
        subdir_dup (TestDuplicatedSet): Test Set
        temp_appdirs (MockAppDirs): AppDirs
    """
    with Deduplicator(app_dirs=temp_appdirs) as app:
        with TemporaryDirectory() as tmpdir:
            # pylint: disable=protected-access
            # Test to evaluate this behavior
            temp_dir = Path(tmpdir).resolve()
            analysis_dest = temp_dir.joinpath('analysis')
            app._analyze(
                directory=subdir_dup.reference_dir,
                exclude=None,
                job_name='test_dedup_same_dir',
                clear_cache=False,
                analysis_dest=analysis_dest.as_posix()
            )
            os_script_map = {
                'posix': '.sh',
                'nt': '.bat'
            }
            script_dest = temp_dir.joinpath(
                'delete').with_suffix(os_script_map[os.name])
            app._delete(
                directory=subdir_dup.dupe_dir,
                exclude=None,
                job_name='test_dedup_same_dir',
                script_dest=script_dest,
            )
            subprocess.check_call(
                [script_dest.as_posix()],
                shell=True
            )
            for dupe in subdir_dup.duplicate_map:
                assert not dupe.exists()


def test_dedup_same_dir_ps1(subdir_dup: TestDuplicatedSet, temp_appdirs: MockAppDirs):
    """Tests deduplication app on same dir with PS1 script

    Args:
        subdir_dup (TestDuplicatedSet): Test Set
        temp_appdirs (MockAppDirs): Temporary AppDirs
    """
    with Deduplicator(app_dirs=temp_appdirs) as app:
        with TemporaryDirectory() as tmpdir:
            # pylint: disable=protected-access
            # Test to evaluate this behavior
            temp_dir = Path(tmpdir).resolve()
            analysis_dest = temp_dir.joinpath('analysis')
            app._analyze(
                directory=subdir_dup.reference_dir,
                exclude=None,
                job_name='test_dedup_same_dir',
                clear_cache=False,
                analysis_dest=analysis_dest.as_posix()
            )
            os_script_map = {
                'posix': '.sh',
                'nt': '.ps1'
            }
            script_dest = temp_dir.joinpath(
                'delete').with_suffix(os_script_map[os.name])
            app._delete(
                directory=subdir_dup.dupe_dir,
                exclude=None,
                job_name='test_dedup_same_dir',
                script_dest=script_dest,
                shell='ps'
            )
            if os.name == 'nt':
                subprocess.check_call(
                    ['powershell.exe', script_dest.as_posix()],
                    shell=True
                )
                for dupe in subdir_dup.duplicate_map:
                    assert not dupe.exists()
