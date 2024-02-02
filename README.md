[![Pylint](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pylint.yml/badge.svg)](https://github.com/UCSD-E4E/e4e-deduplication/actions/workflows/pylint.yml)
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
usage: e4e_deduplication [-h] [--version] {analyze,delete,export_cache,import_cache,list_jobs,drop_tree,report} ...

positional arguments:
  {analyze,delete,export_cache,import_cache,list_jobs,drop_tree,report}

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

usage: e4e_deduplication analyze [-h] -d DIRECTORIES [-e EXCLUDE] -j JOB_NAME [--clear_cache] [-a ANALYSIS_DEST] [--ignore_hash IGNORE_HASH]

options:
  -h, --help            show this help message and exit
  -d DIRECTORIES, --directory DIRECTORIES
                        The directory to work on
  -e EXCLUDE, --exclude EXCLUDE
                        Path to ignore file of absolute path regex patterns to exclude.
  -j JOB_NAME, --job_name JOB_NAME
                        Name of job cache to use.
  --clear_cache         Clears the job cache.
  -a ANALYSIS_DEST, --analysis_dest ANALYSIS_DEST
                        Analysis destination. Defaults to stdout (use "" for stdout)
  --ignore_hash IGNORE_HASH
                        Sequence of hashes to ignore

usage: e4e_deduplication delete [-h] -d DIRECTORY [-e EXCLUDE] -j JOB_NAME -s SCRIPT_DEST [--shell {cmd,ps,sh}]

options:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        The directory to work on.
  -e EXCLUDE, --exclude EXCLUDE
                        Path to ignore file of absolute path regex patterns to exclude.
  -j JOB_NAME, --job_name JOB_NAME
                        Name of job cache to use.
  -s SCRIPT_DEST, --script_dest SCRIPT_DEST
                        Delete script destination
  --shell {cmd,ps,sh}   Shell to generate script for

usage: e4e_deduplication export_cache [-h] -j JOB_NAME -o OUTPUT

options:
  -h, --help            show this help message and exit
  -j JOB_NAME, --job_name JOB_NAME
                        name of job cache to use
  -o OUTPUT, --output OUTPUT
                        filename to export cache CSV as

usage: e4e_deduplication import_cache [-h] -i INPUT_FILE -n NAME [--overwrite]

options:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input_file INPUT_FILE
                        hashes.csv to import
  -n NAME, --name NAME  job name to import as
  --overwrite           overwrite an existing job
```

To analyze `.venv` as the job `test_job` using the `dedup_ignore.txt` ignore set and outputting to `stdout`:
```
e4e_deduplication analyze -d .venv -j test_job -e ./dedup_ignore.txt 
```

This will output a list of duplicated paths, along with the associated hashes.

To test deleting the files in `.venv/Scripts` using the information from the job `test_job` and outputting the deletion script to `delete.sh`:
```
e4e_deduplication analyze -d .venv/Scripts -j test_job -s delete.sh
```

To actually delete the files in `.venv/Scripts`, simply execute `delete.sh`.

To reset the job cache and reanalyze `.venv`:
```
e4e_deduplication analyze -d .venv --clear_cache
```

To upgrade a hostname agnostic job cache:
```
e4e_deduplication_config upgrade_cache -j test_job 
```