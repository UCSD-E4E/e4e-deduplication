'''Tests deduplication
'''
import logging
import shutil
from pathlib import Path
from random import randbytes, randint
import socket
from tempfile import TemporaryDirectory

from e4e_deduplication.analyzer import Analyzer


def test_same_dir_dedup(test_analyzer: Analyzer):
    """Tests deduplication in a nested directory

    Args:
        test_analyzer (Analyzer): Test Analyzer
    """
    # pylint: disable=too-many-locals
    # Locals for debugging and result assessment
    logger = logging.getLogger('same_dir_dedup')
    with TemporaryDirectory() as reference_dir:
        working_dir = Path(reference_dir).resolve()
        dupe_dir = working_dir.joinpath('dupes')
        dupe_dir.mkdir()

        n_files = randint(0, 1024)
        logger.info(f'Creating {n_files} files')
        for idx in range(n_files):
            file_size = randint(1024, 4096)
            with open(working_dir.joinpath(f'{idx:06d}.bin'), 'wb') as handle:
                handle.write(randbytes(file_size))

        n_dupes = randint(0, n_files)
        logger.info(
            f'Duplicating {n_dupes} files, total {n_files + n_dupes} real files')
        for idx in range(n_dupes):
            idx_to_dupe = randint(0, n_files - 1)
            file_to_duplicate = working_dir.joinpath(f'{idx_to_dupe:06d}.bin')
            dupe_file = dupe_dir.joinpath(f'dupe_{idx:06d}.bin')
            shutil.copy(file_to_duplicate, dupe_file)

        test_analyzer.analyze(working_dir)
        results = test_analyzer.get_duplicates()
        total_files = len(list(working_dir.rglob('*')))
        logger.debug(f'{total_files} total direntries')
        for _, file_set in results.items():
            for file, hostname in file_set:
                assert file.is_absolute()
                assert file.exists()
                assert hostname == socket.gethostname()
        assert sum(len(paths) - 1 for paths in results.values()) == n_dupes

        results = test_analyzer.delete(working_dir=dupe_dir)
        assert len(results) == n_dupes
        assert len(list(working_dir.rglob('dupe_*.bin'))) == n_dupes
        for file_to_delete, _ in results.items():
            assert file_to_delete.is_absolute()
            assert file_to_delete.exists()


def test_separate_dir_dedup(test_analyzer: Analyzer):
    """Tests separate directory deduplication behavior

    Args:
        test_analyzer (Analyzer): Test Analyzer
    """
    # pylint: disable=too-many-locals
    # Disables too many locals to allow for debugging of tests
    logger = logging.getLogger('same_dir_dedup')
    with TemporaryDirectory() as reference_dir, TemporaryDirectory() as duplicate_dir:
        working_dir = Path(reference_dir).resolve()
        dupe_dir = Path(duplicate_dir).resolve()

        n_files = randint(0, 1024)
        logger.info(f'Creating {n_files} files')
        for idx in range(n_files):
            file_size = randint(1024, 4096)
            with open(working_dir.joinpath(f'{idx:06d}.bin'), 'wb') as handle:
                handle.write(randbytes(file_size))

        n_dupes = randint(0, n_files)
        logger.info(f'Duplicating {n_dupes} files')
        for idx in range(n_dupes):
            idx_to_dupe = randint(0, n_files - 1)
            file_to_duplicate = working_dir.joinpath(f'{idx_to_dupe:06d}.bin')
            dupe_file = dupe_dir.joinpath(f'dupe_{idx:06d}.bin')
            shutil.copy(file_to_duplicate, dupe_file)

        test_analyzer.analyze(working_dir)
        test_analyzer.analyze(dupe_dir)
        results = test_analyzer.get_duplicates()
        assert sum(len(paths) - 1 for paths in results.values()) == n_dupes

        total_files = len(list(dupe_dir.rglob('*')))
        results = test_analyzer.delete(working_dir=dupe_dir)
        assert len(list(dupe_dir.rglob('*'))) == total_files
        assert len(results) == n_dupes
        assert len(list(working_dir.rglob('*'))) == n_files
