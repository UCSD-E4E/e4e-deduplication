# E4E Deduplication Tool
This tool iterates over a specified directory and generates a list of sha256 checksums.  Once completed it will output a report.csv with a list of all of the duplicate files.

## Installation
### For Developers
```
poetry install
```

### For End Users
```
poetry install --no-root
```

## How to execute
```
poetry run e4e_deduplication --directory <directory to test>
```

This will produce a CSV where each line represents a set of duplicates.