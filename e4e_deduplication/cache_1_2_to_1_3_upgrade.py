'''Cache v1.2.0 to v1.3.0 upgrade logic
'''
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse


def upgrade_cache(
        hash_file: Path,
        dest_path: Path):
    """Upgrades v1.2.0 to v1.3.0 caches

    Args:
        hash_file (Path): Hash file to upgrade
        dest_path (Path): Destination of upgraded cache
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        copy_file = temp_dir / 'v1.2_hashes.csv'
        shutil.copy(hash_file, copy_file)
        with open(dest_path, 'w', encoding='utf-8') as out_handle, \
                open(copy_file, 'r', encoding='utf-8') as in_handle:
            for line in in_handle:
                parts = line.strip().split(',')
                host = parts[-1]
                digest = parts[0]
                path = Path(','.join(parts[1:-1]))
                document = json.dumps({
                    'digest': digest,
                    'path': path.as_posix(),
                    'host': host
                })
                out_handle.write(document + '\n')


def main():
    """CLI Interface
    """
    parser = argparse.ArgumentParser(
        description='e4e_deduplication upgrade cache tool from v1.2.0 to v1.3.0'
    )
    parser.add_argument('--hash_file',
                        type=Path,
                        help='v1.2.0 hash file to upgrade',
                        required=True)
    parser.add_argument('--dest_path',
                        type=Path,
                        help='Path to write upgraded v1.3.0 cache to',
                        required=True)
    args = parser.parse_args()
    upgrade_cache(**vars(args))
