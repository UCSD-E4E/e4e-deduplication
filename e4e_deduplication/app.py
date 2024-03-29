"""
Provides a cli around the E4E deduplication module.
"""
import contextlib
import datetime as dt
import logging
import logging.handlers
import os
import re
import shutil
import socket
import sys
import time
from argparse import ArgumentParser
from importlib import metadata
from pathlib import Path
from typing import Any, List, Optional, TextIO

import semantic_version
from appdirs import AppDirs

from e4e_deduplication.analyzer import Analyzer
from e4e_deduplication.file_filter import load_ignore_pattern
from e4e_deduplication.job_cache import JobCache


class Deduplicator:
    """Deduplicator Application
    """

    def __init__(self, *, app_dirs: Any = None):
        self.__version = semantic_version.Version(
            metadata.version('e4e-deduplication'))
        if app_dirs:
            self.__app_dirs = app_dirs
        else:
            self.__app_dirs = AppDirs(
                'e4e-deduplicator')
        self.configure_loggers()
        self.__log = logging.getLogger('Deduplicator')
        commands = {
            'analyze': self.__configure_analyze_parser,
            'delete': self.__configure_delete_parser,
            'export_cache': self.__configure_export_cache_parser,
            # 'info': self.__configure_info_parser,
            'import_cache': self.__configure_import_cache_parser,
            'list_jobs': self.__configure_list_jobs_parser,
            'drop_tree': self.__configure_drop_tree_parser,
            'report': self.__configure_report_parser
        }
        self.parser = ArgumentParser()
        subparsers = self.parser.add_subparsers()
        parsers = {cmd: subparsers.add_parser(cmd) for cmd in commands}

        for cmd, config_fn in commands.items():
            config_fn(parsers[cmd])

        self.parser.add_argument(
            '--version', action='version', version=str(self.__version))

    def __configure_report_parser(self, parser: ArgumentParser):
        parser.add_argument('-j', '--job_name',
                            type=str,
                            required=True,
                            help='Name of job to generate report for')
        parser.add_argument('-a', '--analysis_dest',
                            type=str,
                            default='',
                            help='Analysis destination. Defaults to stdout (use "" for stdout)')
        parser.add_argument('--ignore_hash',
                            type=str,
                            required=False,
                            action='append',
                            help='Sequence of hashes to ignore')
        parser.set_defaults(func=self._report)

    def _report(self,
                job_name: str,
                analysis_dest: str,
                ignore_hash: List[str] = None):
        job_path = Path(self.__app_dirs.user_data_dir, job_name).resolve()
        self.__log.info(f'Generating report for job at {job_path}')

        self.__generate_report(analysis_dest=analysis_dest,
                               job_path=job_path,
                               ignore_pattern=None,
                               ignore_hashes=ignore_hash)

    def __configure_drop_tree_parser(self, parser: ArgumentParser):
        parser.add_argument('-j', '--job_name',
                            type=str,
                            required=True,
                            help='Name of job cache to use.')
        parser.add_argument('--host',
                            help='Host of directory to drop from',
                            type=str,
                            required=False,
                            default=socket.gethostname())
        parser.add_argument('-d', '--directory',
                            help='The path to drop',
                            type=Path,
                            required=True)
        parser.set_defaults(func=self._drop_tree)

    def _drop_tree(self, job_name: str, host: str, directory: Path):
        self.__log.info(f'Dropping {host}:{directory} from {job_name}')
        job_path = Path(self.__app_dirs.user_data_dir, job_name).resolve()

        with JobCache(job_path) as job:
            job.drop_tree(host, directory)

    def __configure_analyze_parser(self, parser: ArgumentParser):
        parser.add_argument('-d', '--directory',
                            help='The directory to work on',
                            type=Path,
                            action='append',
                            required=True,
                            dest='directories')
        parser.add_argument('-e', '--exclude',
                            help='Path to ignore file of absolute path regex patterns to exclude.',
                            type=Path,
                            default=None)
        parser.add_argument('-j', '--job_name',
                            type=str,
                            required=True,
                            help='Name of job cache to use.')
        parser.add_argument('--clear_cache',
                            action='store_true',
                            help='Clears the job cache.')
        parser.add_argument('-a', '--analysis_dest',
                            type=str,
                            default='',
                            help='Analysis destination. Defaults to stdout (use "" for stdout)')
        parser.add_argument('--ignore_hash',
                            type=str,
                            required=False,
                            action='append',
                            help='Sequence of hashes to ignore')
        parser.set_defaults(func=self._analyze)

    def _analyze(self,
                 directories: List[Path],
                 exclude: Path,
                 job_name: str,
                 clear_cache: bool,
                 analysis_dest: str,
                 ignore_hash: List[str] = None):
        # pylint: disable=too-many-arguments,too-many-locals
        # Required for CLI args, process orchestration
        job_path = Path(self.__app_dirs.user_data_dir, job_name).resolve()
        self.__log.info(f'Using job path {job_path}')

        bad_dirs = []
        for directory in directories:
            if not directory.is_dir():
                bad_dirs.append(directory)
        if len(bad_dirs) > 0:
            raise FileNotFoundError(f'Unknown directories {bad_dirs}')

        for directory in directories:
            directory_path = directory.resolve()
            self.__log.info(f'Walking path {directory_path}')

            if clear_cache:
                user_input = input(
                    'Clearing the cache is a destructive operation, proceed? [y/N]: ')
                if user_input.lower().strip() != 'y':
                    return

            if exclude:
                ignore_pattern = load_ignore_pattern(exclude.resolve())
            else:
                ignore_pattern = None
            self.__log.info(f'Using ignore pattern {ignore_pattern}')

            with Analyzer(ignore_pattern=ignore_pattern, job_path=job_path) as app:
                if clear_cache:
                    app.clear_cache()
                app.analyze(working_dir=directory_path)

        self.__generate_report(analysis_dest, job_path,
                               ignore_pattern, ignore_hashes=ignore_hash)

    def __generate_report(self,
                          analysis_dest: str,
                          job_path: Path,
                          ignore_pattern: Optional[re.Pattern],
                          ignore_hashes: List[str] = None):
        with self.output_writer(analysis_dest) as handle, \
                Analyzer(ignore_pattern=ignore_pattern, job_path=job_path) as app:
            analysis_report = app.get_duplicates(ignore_hashes=ignore_hashes)
            for digest, files in sorted(analysis_report.items(),
                                        key=lambda x: len(x[1]),
                                        reverse=True):
                handle.write(
                    f'File signature {digest} discovered {len(files)} times:\n'
                )
                for file, hostname in files:
                    handle.write(f'\t{hostname}:{file.as_posix()}\n')

    def __configure_delete_parser(self, parser: ArgumentParser):
        parser.add_argument('-d', '--directory',
                            help='The directory to work on.',
                            type=Path,
                            required=True)
        parser.add_argument('-e', '--exclude',
                            help='Path to ignore file of absolute path regex patterns to exclude.',
                            type=Path,
                            default=None)
        parser.add_argument('-j', '--job_name',
                            type=str,
                            required=True,
                            help='Name of job cache to use.')
        parser.add_argument('-s', '--script_dest',
                            type=Path,
                            help='Delete script destination',
                            required=True)
        parser.add_argument('--shell',
                            type=str,
                            choices=['cmd', 'ps', 'sh'],
                            default=None,
                            help='Shell to generate script for')
        parser.set_defaults(func=self._delete)

    def _delete(self,
                directory: Path,
                exclude: Path,
                job_name: str,
                script_dest: Path,
                shell: str = None):
        # pylint: disable=too-many-arguments,too-many-locals
        # Required for CLI args, process orchestration
        job_path = Path(self.__app_dirs.user_data_dir, job_name).resolve()
        self.__log.info(f'Using job path {job_path}')

        directory_path = directory.resolve()
        self.__log.info(f'Walking path {directory_path}')

        script_dest.resolve()

        if exclude:
            ignore_path = exclude.resolve()
            ignore_pattern = load_ignore_pattern(ignore_path)
        else:
            ignore_pattern = None
        self.__log.info(f'Using ignore pattern {ignore_pattern}')

        with Analyzer(ignore_pattern=ignore_pattern, job_path=job_path) as app:
            delete_report = app.delete(
                working_dir=directory_path
            )

        os_shell_map = {
            'posix': 'sh',
            'nt': 'cmd'
        }
        shell_delete_map = {
            'cmd': 'del /f "{path}" &:: {digest}',
            'ps': 'Remove-Item -Path "{path}" -Force # {digest}',
            'sh': 'rm -f "{path}" # {digest}'
        }
        if shell:
            del_fmt = shell_delete_map[shell]
        else:
            del_fmt = shell_delete_map[os_shell_map[os.name]]

        with self.output_writer(script_dest.as_posix()) as handle:
            for file, digest in delete_report.items():
                handle.write(del_fmt.format(
                    path=str(file), digest=digest) + '\n')

        script_dest.chmod(0o766)

    def __configure_export_cache_parser(self, parser: ArgumentParser):
        parser.add_argument('-j', '--job_name',
                            help='name of job cache to use',
                            type=str,
                            required=True)
        parser.add_argument('-o', '--output',
                            type=Path,
                            help='filename to export cache CSV as',
                            required=True)
        parser.set_defaults(func=self._export_cache)

    def _export_cache(self, job_name: str, output: Path) -> None:
        job_path = Path(self.__app_dirs.user_data_dir, job_name).resolve()
        self.__log.info(f'Using job path {job_path}')
        shutil.copy(job_path.joinpath('hashes.csv'), output.resolve())

    def __configure_import_cache_parser(self, parser: ArgumentParser):
        parser.add_argument('-i', '--input_file',
                            type=Path,
                            required=True,
                            help='hashes.csv to import')
        parser.add_argument('-n', '--name',
                            type=str,
                            required=True,
                            help='job name to import as')
        parser.add_argument('--overwrite',
                            action='store_true',
                            help='overwrite an existing job')
        parser.set_defaults(func=self._import_cache)

    def _import_cache(self, input_file: Path, name: str, overwrite: bool) -> None:
        job_path = Path(self.__app_dirs.user_data_dir, name)
        if not overwrite:
            if job_path.is_dir():
                print(f'A job named {name} already exists!')
                return
        job_path.mkdir(parents=True, exist_ok=True)
        shutil.copy(input_file, job_path.joinpath('hashes.csv'))

    def __configure_list_jobs_parser(self, parser: ArgumentParser):
        parser.set_defaults(func=self._list_jobs)

    def _list_jobs(self) -> None:
        for path in Path(self.__app_dirs.user_data_dir).glob('*'):
            print(path.name)

    def output_writer(self, spec: str) -> TextIO:
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

    def configure_loggers(self):
        """Configures the loggers
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        log_dest = Path(self.__app_dirs.user_log_dir,
                        'e4e_dedup.log').resolve()
        log_dest.parent.mkdir(exist_ok=True, parents=True)
        self.__log_file_handler = logging.handlers.RotatingFileHandler(log_dest,
                                                                       maxBytes=5*1024*1024,
                                                                       backupCount=5)
        self.__log_file_handler.setLevel(logging.DEBUG)

        root_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__log_file_handler.setFormatter(root_formatter)
        root_logger.addHandler(self.__log_file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(error_formatter)
        root_logger.addHandler(console_handler)
        logging.Formatter.converter = time.gmtime
        # See https://docs.python.org/3/library/logging.html#logging.Formatter.formatTime
        # See https://stackoverflow.com/a/58777937
        logging.Formatter.formatTime = (
            lambda self, record, datefmt=None: dt.datetime.fromtimestamp(
                record.created, dt.timezone.utc).astimezone().isoformat())

    def __enter__(self):
        return self

    def __exit__(self, exc, exv, exp):
        self.__log_file_handler.close()

    def main(self):
        """Main entry point
        """
        args = self.parser.parse_args()
        arg_dict = vars(args)

        arg_fn = args.func
        arg_dict.pop('func')
        arg_fn(**arg_dict)


def main() -> None:
    """
    Entry point for the CLI.
    """
    with Deduplicator() as app:
        app.main()


if __name__ == '__main__':
    main()
