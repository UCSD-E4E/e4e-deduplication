'''Utility Functions
'''

from pathlib import Path
from typing import Generator


def path_to_str(gen: Generator[Path, None, None]) -> Generator[str, None, None]:
    """Inline generator that converts Path objects to the canonical string representation

    Args:
        gen (Generator[Path, None, None]): rglob generator

    Yields:
        Generator[str, None, None]: string representation generator
    """
    for path in gen:
        yield path.as_posix()
