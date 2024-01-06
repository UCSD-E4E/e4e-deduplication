'''Cache v0.7.0 to v1.0.0 upgrade logic
'''
import argparse
import shutil
from pathlib import Path
from socket import gethostname
from tempfile import TemporaryDirectory
from typing import List


def upgrade_cache(hash_file: Path,
                  dest_path: Path,
                  hostname_to_fill: str,
                  valid_hostnames: List[str]):
    """Upgrades a v0.7.0 hash file to a v1.0.0 hash file

    Args:
        hash_file (Path): Hash File to upgrade
        dest_path (Path): Destination for upgraded Hash File
        hostname_to_fill (str): Hostname to fill in
        valid_hostnames (List[str]): List of valid hostnames
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        copy_file = temp_dir / 'hashes.csv'
        shutil.copy(hash_file, copy_file)
        with open(dest_path, 'w', encoding='utf-8') as out_handle, \
                open(copy_file, 'r', encoding='utf-8') as in_handle:
            for line in in_handle:
                parts = line.strip().split(',')
                if parts[-1] not in valid_hostnames:
                    line = line.strip() + f',{hostname_to_fill}\n'
                out_handle.write(line)


def main():
    """CLI for upgrade script
    """
    parser = argparse.ArgumentParser(
        description='e4e_deduplication upgrade cache tool from v0.7.0 to v1.0.0'
    )
    parser.add_argument('--hash_file',
                        type=Path,
                        help='Hash File to upgrade',
                        required=True)
    parser.add_argument('--dest_path',
                        type=Path,
                        help='Path to write upgraded cache to',
                        required=True)
    parser.add_argument('--hostname_to_fill',
                        type=str,
                        default=gethostname(),
                        required=False,
                        help='Hostname to fill in')
    parser.add_argument('--accept',
                        type=str,
                        action='append',
                        help='Sequence of valid hostnames',
                        dest='valid_hostnames',
                        required=True)
    args = parser.parse_args()
    upgrade_cache(**vars(args))


if __name__ == '__main__':
    main()
