import re


SNIP_BEFORE = '... '
SNIP_AFTER = ' ...'


class Result(object):
    def __init__(self, filename, linenr, index, message):
        self.filename = filename
        self.linenr = linenr
        self.index = index
        self.message = message
        self.score = 0


def match_lines(filename, search_regex, message_size):
    """
    Returns a filter that returns matching Results in the source of the given file.
    """
    with open(filename, 'r') as f:
        for linenumber, line in enumerate(f.readlines(), start=1):
            # Skip files with invalid lines
            try:
                line.decode('utf-8')
            except:
                return

            match = search_regex.search(line)
            if match:
                start = max([0, match.start()])
                end = max([0, match.end()])
                message = create_snippet(line, start, end, message_size)
                yield Result(filename, linenumber, start, message)


def create_snippet(line, start, end, message_size, message_lead=None):
    size = end - start
    if message_lead is None:
        message_lead = (message_size - size) / 5

    orig = line

    line = re.sub('^\s+', '', line)
    index = max([0, start - (len(orig) - len(line))])

    line = re.sub('\s+$', '', line)

    if len(line) > message_size and index > message_lead:
        reduction = min([len(line) - message_size + len(SNIP_BEFORE), index - message_lead])

        line = SNIP_BEFORE + line[reduction:]
        index = index - reduction + len(SNIP_BEFORE)
        if index < 0:
            index = 0

    if len(line) > message_size:
        line = line[:message_size - len(SNIP_AFTER)] + SNIP_AFTER

    return line
