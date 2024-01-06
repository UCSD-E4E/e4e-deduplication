'''Tests Cache upgrades
'''
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from e4e_deduplication import (cache_0_7_to_1_0_upgrade,
                               cache_1_2_to_1_3_upgrade)


def test_0_7_to_1_0_upgrade():
    """Tests v0.7.0 to v1.0.0 upgrade
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        hash_file = temp_dir / 'hashes.csv'
        dest_path = temp_dir / 'dest.csv'
        hostname_to_fill = 'new_hostname'
        valid_hostnames = ['old_hostname']

        with open(hash_file, 'w', encoding='utf-8') as handle:
            for idx in range(16):
                handle.write(
                    f'{idx:12d},f{temp_dir.joinpath(f"{idx:08d}.bin").as_posix()}\n')
            for idx in range(16, 32):
                handle.write(
                    f'{idx:12d},f{temp_dir.joinpath(f"{idx:08d}.bin").as_posix()},old_hostname\n')

        cache_0_7_to_1_0_upgrade.upgrade_cache(
            hash_file=hash_file,
            dest_path=dest_path,
            hostname_to_fill=hostname_to_fill,
            valid_hostnames=valid_hostnames
        )
        valid_hostnames.append(hostname_to_fill)
        with open(dest_path, 'r', encoding='utf-8') as handle:
            for line in handle:
                parts = line.strip().split(',')
                assert parts[-1] in valid_hostnames
                assert parts[2] in valid_hostnames
                assert len(parts) == 3


def test_1_2_to_1_3_upgrade():
    """Tests v1.2.0 to v1.3.0 upgrade
    """
    with TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir).resolve()
        hash_file = temp_dir / 'hashes.csv'
        dest_path = temp_dir / 'dest.csv'

        with open(hash_file, 'w', encoding='utf-8') as handle:
            for idx in range(16):
                handle.write(
                    f'{idx:12d},f{temp_dir.joinpath(f"{idx:08d}.bin").as_posix()},old_hostname\n')
            for idx in range(16, 32):
                handle.write(
                    f'{idx:12d},f{temp_dir.joinpath(f"{idx:08d},comma.bin").as_posix()}'
                    ',old_hostname\n')

        cache_1_2_to_1_3_upgrade.upgrade_cache(
            hash_file=hash_file,
            dest_path=dest_path
        )

        with open(dest_path, 'r', encoding='utf-8') as handle:
            for line in handle:
                document = json.loads(line)
                assert 'digest' in document
                assert 'host' in document
                assert 'path' in document
                assert Path(document['path'])
