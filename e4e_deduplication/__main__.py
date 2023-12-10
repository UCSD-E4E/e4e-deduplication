"""
Provides a cli around the E4E deduplication module.
"""
import logging
import logging.handlers
import re
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import List

from appdirs import AppDirs

from e4e_deduplication.analyzer import Analyzer

app_dirs = AppDirs('e4e-deduplicator')


def configure_loggers():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    log_dest = Path(app_dirs.user_log_dir, 'e4e_dedup.log').resolve()
    log_dest.parent.mkdir(exist_ok=True, parents=True)
    log_file_handler = logging.handlers.RotatingFileHandler(log_dest,
                                                            maxBytes=5*1024*1024,
                                                            backupCount=5)
    log_file_handler.setLevel(logging.DEBUG)

    root_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(root_formatter)
    root_logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    error_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(error_formatter)
    root_logger.addHandler(console_handler)
    logging.Formatter.converter = time.gmtime


def main() -> None:
    """
    Entry point for the CLI.
    """
    configure_loggers()
    logger = logging.getLogger('get_args')
    parser = ArgumentParser(
        description="Looks through a single directory and generates a list of duplicate files."
    )

    parser.add_argument(
        "-d", "--directory", type=Path, required=True, help="The directory to work on."
    )

    parser.add_argument(
        "-e", "--exclude", type=Path, default=None, help="Path to ignore file of absolute path regex patterns to exclude."
    )

    parser.add_argument(
        "-j", "--job_name",
        type=str,
        required=True,
        help="Name of job cache to use."
    )

    parser.add_argument(
        '--clear_cache',
        action="store_true",
        help="Clears the job cache."
    )

    parser.add_argument(
        "-a", "--analysis_dest",
        type=str,
        default='stdout',
        help="Analysis destination"
    )

    parser.add_argument(
        'action',
        type=str,
        choices=['analyze', 'delete'],
        help='Action to take',
        default='analyze'
    )

    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='Dry run of delete'
    )

    args = parser.parse_args()
    directory_path: Path = args.directory.resolve()
    job_path = Path(app_dirs.user_data_dir, args.job_name).with_suffix('.json')
    logger.info(f'Using job path {job_path}')

    logger.info(f'Walking path {directory_path}')

    regex_patterns: List[str] = []
    if args.exclude:
        with open(args.exclude, 'r', encoding='utf-8') as handle:
            for line in handle:
                if line.startswith('#'):
                    continue
                if len(line.strip()) == 0:
                    continue
                regex_patterns.append(line.strip())
    ignore_pattern = re.compile('|'.join(regex_patterns))
    logger.info(f'Using ignore pattern {ignore_pattern}')

    with Analyzer(ignore_pattern=ignore_pattern, job_path=job_path) as app:
        if args.clear_cache:
            app.clear_cache()
        if args.action == 'analyze':
            report = app.analyze(working_dir=directory_path)
        elif args.action == 'delete':
            report = app.delete(working_dir=directory_path, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
