'''File Path Filter
'''
import re
from pathlib import Path
from typing import List


def load_ignore_pattern(ignore_path: Path) -> re.Pattern:
    """Loads the ignore pattern from file

    Args:
        ignore_path (Path): Path to ignore file

    Returns:
        re.Pattern: Regex pattern
    """
    regex_patterns: List[str] = []
    with open(ignore_path, 'r', encoding='utf-8') as handle:
        for line in handle:
            if line.startswith('#'):
                continue
            if len(line.strip()) == 0:
                continue
            regex_patterns.append(line.strip())
    ignore_pattern = re.compile('|'.join(regex_patterns))
    return ignore_pattern
