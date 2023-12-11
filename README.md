[![Pylint](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pylint.yml/badge.svg?branch=gh_actions)](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pylint.yml)
[![pytest](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pytest.yml/badge.svg)](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pytest.yml)
# E4E Deduplication Tool
This tool iterates over a specified directory and generates a list of sha256 checksums.  Once completed it will output a report with a list of all of the duplicate files.

## Installation
### For Developers
```
poetry install
```

### For End Users
```
python -m pip install .
```

## How to execute
```
usage: e4e_deduplication [-h] -d DIRECTORY [-e EXCLUDE] -j JOB_NAME [--clear_cache] [-a ANALYSIS_DEST] [--dry_run] {analyze,delete}

Looks through a single directory and generates a list of duplicate files.

positional arguments:
  {analyze,delete}      Action to take

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        The directory to work on.
  -e EXCLUDE, --exclude EXCLUDE
                        Path to ignore file of absolute path regex patterns to exclude.
  -j JOB_NAME, --job_name JOB_NAME
                        Name of job cache to use.
  --clear_cache         Clears the job cache.
  -a ANALYSIS_DEST, --analysis_dest ANALYSIS_DEST
                        Analysis destination. Defaults to stdout (use "" for stdout)
  --dry_run             Dry run of delete
```

To analyze `.venv` as the job `test_job` using the `dedup_ignore.txt` ignore set and outputting to `stdout`:
```
e4e_deduplication -d .venv -j test_job -e ./dedup_ignore.txt analyze
```

This will output a list of duplicated paths, along with the associated hashes.

To test deleting the files in `.venv/Scripts` using the information from the job `test_job` and outputting the report to `delete.txt`:
```
e4e_deduplication -d .venv/Scripts -j test_job -a delete.txt --dry_run delete
```

To actually delete the files in `.venv/Scripts`:
```
e4e_deduplication -d .venv/Scripts -j test_job delete
```

To reset the job cache and reanalyze `.venv`:
```
e4e_deduplication -d .venv --clear_cache analyze
```
