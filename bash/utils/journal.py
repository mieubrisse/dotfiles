import os
import datetime
from collections import defaultdict
import argparse

# TODO change to parameterization
JOURNAL_LOC = "/Users/zerix/gdrive/journal"

# Classes ====================================================================================================

# Keys for the dict of file + metadata we pass around
class EntryAndMetadata:
    """
    Class to contain information about a journal entry - filename on disk, date of creation, tags, etc.
    """

    MISSING_DATE_FORMAT_DATE = datetime.datetime(1970, 1, 1, 0, 0, 0)    # Date we assume an entry was written if we can't parse the date
    FILENAME_DATE_FMTS = [
        "%Y-%m-%d_%H-%M-%S",
        "%Y-%m-%d"
    ]

    def __init__(self, filename):
        filename_minus_ext, extension = os.path.splitext(filename)

        filename_fragments = filename_minus_ext.split("~")
        self.pseudo_name = filename_fragments[0] + extension
        created_timestamp_str = filename_fragments[1] if len(filename_fragments) >= 2 else ""
        tags_str = filename_fragments[2] if len(filename_fragments) >= 3 else ""

        self.creation_timestamp = EntryAndMetadata.MISSING_DATE_FORMAT_DATE
        for date_format in EntryAndMetadata.FILENAME_DATE_FMTS:
            try:
                self.creation_timestamp = datetime.datetime.strptime(created_timestamp_str, date_format)
                break
            except ValueError:
                pass
        self.tags = tags_str.split(",") if len(tags_str) > 0 else []

    def __repr__(self):
        return self.filename

    def __str__(self):
        tag_str = "   \033[35m%s" % " ".join(self.tags) if len(self.tags) > 0 else ""
        return "\033[33m%s   \033[37m%s%s" % (self.creation_timestamp, self.pseudo_name, tag_str)


class EntryStore:
    """
    Takes a list of EntryAndMetadata and processes it in an easily-queryable format
    """

    def __init__(self, entry_list):
        self._entries = set(entry_list)
        self._tag_lookup = defaultdict(lambda: set())
        for entry in self._entries:
            for tag in entry.tags:
                self._tag_lookup[tag].add(entry)

    def get_all(self):
        return self._entries

    def get_by_tag(self, tag):
        return self._tag_lookup.get(tag, set())

    def get_by_name(self, keyword):
        return [ entry for entry in self._entries if keyword in entry.pseudo_name]

# Helper Functions ====================================================================================================
def load_entries():
    journal_filenames = [filename for filename in os.listdir(JOURNAL_LOC) if os.path.isfile(os.path.join(JOURNAL_LOC, filename))]
    entries = [ EntryAndMetadata(filename) for filename in journal_filenames]
    return EntryStore(entries)

TIMESTAMP_SORT = "DATE"
ENTRY_NAME_SORT = "NAME"
ENTRY_SORTING_FUNCS = {
    TIMESTAMP_SORT: lambda entry_and_metadata: entry_and_metadata.creation_timestamp,
    ENTRY_NAME_SORT: lambda entry_and_metadata: entry_and_metadata.pseudo_name,
}
def render_entries(entries, entry_sort_type, sort_reverse):
    if len(entries) == 0:
        print("              \033[90m<No results>")
        return

    sorted_entries = sorted(entries, key=ENTRY_SORTING_FUNCS[entry_sort_type], reverse=sort_reverse)
    for entry in sorted_entries:
        print(entry)

# Commands ====================================================================================================

def list_entries(args):
    entry_store = load_entries()
    render_entries(entry_store.get_all(), args.sort, args.reverse)

def find_entries(args):
    entry_store = load_entries()
    if args.tag:
        entries = entry_store.get_by_tag(args.tag)
    if args.name:
        entries = entry_store.get_by_name(args.name)
    render_entries(entries, args.sort, args.reverse)

# Arg Parsing ====================================================================================================
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--sort", default=TIMESTAMP_SORT, choices=ENTRY_SORTING_FUNCS.keys())
parser.add_argument("-r", "--reverse", default=False, action='store_true')
subparsers = parser.add_subparsers(dest='command')
subparsers.required = True

LIST_COMMAND = "ls"
FIND_COMMAND = "find"
COMMAND_MAP = {
    LIST_COMMAND: list_entries,
    FIND_COMMAND: find_entries,
}

# ls command
ls_parser = subparsers.add_parser(LIST_COMMAND, help="Listing journal entries")

# find command
find_parser = subparsers.add_parser(FIND_COMMAND, help="Finding journal entries based off criteria")
search_type_group = find_parser.add_mutually_exclusive_group(required=True)
search_type_group.add_argument("-t", "--tag")
search_type_group.add_argument("-n", "--name")

args = parser.parse_args()

COMMAND_MAP[args.command](args)
