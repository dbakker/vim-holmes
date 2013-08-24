import os.path
from os.path import relpath, splitext, basename, dirname, abspath
import re
from fnmatch import fnmatch


DEFAULT_SKIP_FILES = set('tags|.gitignore'.split('|'))
DEFAULT_SKIP_EXTS = set('pyc|o|bin|dat|jar|gif|png|jpg|bmp|gz|tar|7z|lz|lzh|zip|z|ico|class|exe|dll|war|tmp|bak'.split('|'))

low_priority_globs = set()
exclude_globs = set()


def matches_glob(file, globs):
    file_basename = basename(file)

    for glob in globs.split(';'):
        if fnmatch(file, glob):
            return True
        if fnmatch(file_basename, glob):
            return True

    return False


def score(filename, main_file):
    """
    Assigns a numerical score to files. Files with scores
    of 0 or under 0 are not included in results by default.
    """
    score = 1000
    filename = abspath(filename)
    main_file = abspath(main_file)

    rel = relpath(filename, dirname(main_file))
    target_root, target_ext = splitext(filename)
    main_root, main_ext = splitext(main_file)
    target_base = basename(filename)

    if matches_glob(filename, exclude_globs):
        return -1000
    if target_ext[1:].lower() in DEFAULT_SKIP_EXTS:
        return -1000
    if target_base.lower() in DEFAULT_SKIP_FILES or target_base.endswith('~'):
        return -1000

    # Heuristically skip minified js/css
    if target_ext.lower() in ['.js', '.css']:
        try:
            if target_root.endswith('.min'):
                return -1000

            with open(filename, 'r') as f:
                for line in f.readlines(10):
                    if len(line) > 500:
                        return -1000
        except:
            raise

    if matches_glob(filename, low_priority_globs):
        score -= 500

    # Give files of the same type or the same name higher scores
    if target_root == main_root:
        score += 200
    if target_ext == main_ext:
        score += 100

    # Favor files in subdirectories over upper directories
    if rel.startswith('..'):
        score -= 100
    score -= len(re.findall('/', rel)) * 10

    return score
