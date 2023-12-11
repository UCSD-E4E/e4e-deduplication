'''Test Ignore Filter
'''
from pathlib import Path
from tempfile import TemporaryDirectory

from e4e_deduplication.file_filter import load_ignore_pattern


def test_synology():
    """Tests that the synology special folders are caught by the file filters
    """
    ignore_path = Path('dedup_ignore.txt')
    pattern = load_ignore_pattern(ignore_path)
    with TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir).resolve()
        ea_dir = root_dir.joinpath('@eaDir')
        ea_dir.mkdir()
        recycle = root_dir.joinpath('#recycle')
        recycle.mkdir()
        assert len(list(root_dir.glob('*'))) > 1
        assert pattern.search(ea_dir.as_posix())
        assert pattern.search(recycle.as_posix())
