"""
Provides a cli around the E4E deduplication module.
"""
import contextlib
import logging
import logging.handlers
import sys
import time
from argparse import ArgumentParser
from pathlib import Path
from typing import TextIO

from appdirs import AppDirs

from e4e_deduplication.analyzer import Analyzer
from e4e_deduplication.file_filter import load_ignore_pattern

app_dirs = AppDirs('e4e-deduplicator')


def writer(spec: str) -> TextIO:
    """Creates a writer for either stdout or a file

    Args:
        spec (str): Output specifier

    Returns:
        TextIO: Text IO object

    Yields:
        Iterator[TextIO]: stdout
    """
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout
    return open(spec, 'w', encoding='utf-8') if spec else stdout()


def configure_loggers():
    """Configures the loggers
    """
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
    console_handler.setLevel(logging.WARNING)

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
        description='Looks through a single directory and generates a list of duplicate files.'
    )

    parser.add_argument(
        '-d', '--directory',
        type=Path,
        required=True,
        help='The directory to work on.'
    )

    parser.add_argument(
        '-e', '--exclude',
        type=Path,
        default=None,
        help='Path to ignore file of absolute path regex patterns to exclude.'
    )

    parser.add_argument(
        '-j', '--job_name',
        type=str,
        required=True,
        help='Name of job cache to use.'
    )

    parser.add_argument(
        '--clear_cache',
        action='store_true',
        help='Clears the job cache.'
    )

    parser.add_argument(
        '-a', '--analysis_dest',
        type=str,
        default='',
        help='Analysis destination. Defaults to stdout (use "" for stdout)'
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
    job_path = Path(app_dirs.user_data_dir, args.job_name).with_suffix('.db')
    logger.info(f'Using job path {job_path}')

    logger.info(f'Walking path {directory_path}')

    if args.exclude:
        ignore_path: Path = args.exclude
        ignore_pattern = load_ignore_pattern(ignore_path)
    logger.info(f'Using ignore pattern {ignore_pattern}')

    with Analyzer(ignore_pattern=ignore_pattern, job_path=job_path) as app:
        if args.clear_cache:
            app.clear_cache()
        if args.action == 'analyze':
            analysis_report = app.analyze(working_dir=directory_path)
        elif args.action == 'delete':
            delete_report = app.delete(working_dir=directory_path,
                                       dry_run=args.dry_run)

    with writer(args.analysis_dest) as handle:
        if args.action == 'analyze':
            for digest, files in sorted(analysis_report.items(),
                                        key=lambda x: len(x[1]),
                                        reverse=True):
                handle.write(
                    f'File signature {digest} discovered {len(files)} times:\n')
                for file in files:
                    handle.write(f'\t{file.as_posix()}\n')
        elif args.action == 'delete':
            for file, digest in delete_report.items():
                handle.write(f'Deleted {file.as_posix()} with hash {digest}\n')


if __name__ == '__main__':
    main()
