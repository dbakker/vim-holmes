#!/usr/bin/env python

import subprocess
import os.path
from os.path import basename, splitext, join, realpath, isdir, isfile, abspath, expanduser
import os
import re
import sys
import argparse
import score
import match
import threading
from fnmatch import fnmatch
import itertools


DEFAULT_IGNORE_DIRS = set('.git|.svn|CVS|.hs'.split('|'))
found_filenames = set()


def get_filenames(path):
    """
    Returns all potentially searchable files within the given folder.
    """
    global found_filenames
    if isfile(path):
        return found_filenames.add(path)
    if path in ignored_dirs:
        return

    files = os.listdir(path)
    for file in files:
        # Make sure links are only followed once
        file = realpath(join(path, file))
        if file in found_filenames:
            continue
        found_filenames.add(file)

        if isdir(file) and recurse_directories:
            if basename(file) not in DEFAULT_IGNORE_DIRS:
                get_filenames(file)


def process_files(files, source, regex, max_results):
    out = []
    for filename in filter(isfile, files):
        file_score = score.score(filename, source)
        for result in match.match_lines(filename, regex, int(args.message_size)):
            result.score = file_score
            filename = os.path.relpath(result.filename, os.path.curdir)
            out += ['%s:%d:%d:%s' % (filename, result.linenr, result.index + 1, result.message)]
            if max_results is not None:
                max_results -= 1
                if max_results <= 0:
                    return out

    return out


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grep replacement for Vim')
    parser.add_argument('--message-size',
                        dest='message_size',
                        default=64,
                        help='set the maximum size to which messages should be trimmed')
    parser.add_argument('--source',
                        dest='source',
                        default=None,
                        help='the source file the regular expression came from, used to sort results more relevantly')
    parser.add_argument('--ignore-dir',
                        dest='ignored_dirs',
                        action='append',
                        default=[],
                        help='Ignore directory.')
    parser.add_argument('--smart-case',
                        dest='smart_case',
                        action='store_true',
                        default=False,
                        help='simulates the "smartcase" setting of Vim. make regular expressions with no upper case letters ignore case')
    parser.add_argument('-n', '--no-recurse',
                        dest='recurse_directories',
                        action='store_false',
                        default=True,
                        help='no descending into subdirectories')
    parser.add_argument('-r', '-R', '--recurse',
                        dest='recurse_directories',
                        action='store_true',
                        default=True,
                        help='recurse into subdirectories')
    parser.add_argument('--exclude',
                        dest='exclude_files',
                        action='append',
                        default=[],
                        help='Exclude files matching the specified glob.')
    parser.add_argument('--low-priority',
                        dest='low_priority_globs',
                        action='append',
                        default=[],
                        help='Put files matching the given glob at the bottom of the results list.')
    parser.add_argument('-Q', '--literal',
                        dest='literal',
                        action='store_true',
                        default=False,
                        help='search for the given pattern literally instead of as regex')
    parser.add_argument('-i', '-y', '--ignore-case',
                        dest='ignore_case',
                        action='store_true',
                        default=False,
                        help='ignore case distinctions in the pattern')
    parser.add_argument('-w', '--word-regexp',
                        dest='word_regexp',
                        action='store_true',
                        default=False,
                        help='select only those lines containing whole words')
    parser.add_argument('--max-results',
                        dest='max_results',
                        default=None,
                        help='never return more than the specified number of results')
    parser.add_argument('pattern', help='pattern to find.')
    parser.add_argument('file', metavar='file', help='Files to search.', nargs='*')
    args = parser.parse_args()

    paths_to_search = args.file
    if not paths_to_search:
        paths_to_search = [os.path.curdir]

    source = args.source
    if not source:
        source = paths_to_search[0]

    ignored_dirs = set(map(abspath, map(expanduser, args.ignored_dirs)))

    recurse_directories = args.recurse_directories

    for path in paths_to_search:
        get_filenames(path)

    if args.ignore_case or (args.smart_case and not re.search('[A-Z]', args.pattern)):
        flags = re.IGNORECASE
    else:
        flags = 0

    pattern_string = args.pattern
    if args.literal:
        pattern_string = re.escape(pattern_string)
    if args.word_regexp:
        pattern_string = "\\b%s\\b" % pattern_string

    regex = re.compile(pattern_string, flags)

    files = found_filenames

    score.exclude_globs = ';'.join(args.exclude_files)
    score.low_priority_globs = ';'.join(args.low_priority_globs)

    # Map files into (score, filename) tuples
    files = map(lambda filename: (score.score(filename, source), filename), files)

    # Filter and sort files
    files = filter(lambda x: x[0] > 0, files)
    files = sorted(files, reverse=True)

    # Get back filenames
    files = list(zip(*files)[1])

    print(os.linesep.join(process_files(files, source, regex, args.max_results)))
