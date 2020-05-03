import os
import datetime
from collections import defaultdict
import subprocess
import re

# TODO change to parameterization
JOURNAL_LOC = os.path.expanduser("~/gdrive/journal")

# Files with this pattern won't be loaded to the entry store
BLACKLISTED_PATTERNS = [
    r".*\.swp$",
    r"^.git$",
]
COMPILED_BLACKLISTED_PATTERNS = [re.compile(pattern) for pattern in BLACKLISTED_PATTERNS]


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
        tag_str = "   \033[35m%s" % " ".join(sorted(self.tags)) if len(self.tags) > 0 else ""
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

    def get_tags(self):
        return self._tag_lookup.keys()

    def get_by_tag(self, tag):
        return self._tag_lookup.get(tag, set())

    def get_by_name(self, keyword):
        return [ entry for entry in self._entries if keyword in entry.pseudo_name]

class Command:
    def __init__(self, aliases, func, help_str):
        self.aliases = set(aliases)
        self.func = func
        self.help_str = help_str

# Helper Functions ====================================================================================================
def is_valid_journal_entry(journal_dirpath, filename):
    result = os.path.isfile(os.path.join(journal_dirpath, filename))
    for pattern in COMPILED_BLACKLISTED_PATTERNS:
        return result and not pattern.match(filename)
    return result

def load_entries(journal_dirpath):
    journal_filenames = [filename for filename in os.listdir(journal_dirpath) if is_valid_journal_entry(journal_dirpath, filename)]
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

# ================ Commands =========================
def help():
    print("")
    for cmd in COMMANDS:
        aliases_str = ", ".join(sorted(cmd.aliases))
        padded_aliases = aliases_str.ljust(25, " ")
        print("  %s%s" % (padded_aliases, cmd.help_str))
    return None

def print_tags(entry_store):
    tags = sorted(entry_store.get_tags())
    for tag in tags:
        print(" - %s" % tag)
    return None

def list_entries(entry_store, args):
    results = entry_store.get_all()
    if len(results) == 0:
        print("No entries")
        return None
    # TODO allow user to customize sort
    render_entries(results, ENTRY_NAME_SORT, False)
    return None

def search_by_name(entry_store, user_input):
    results = entry_store.get_by_name(user_input)
    if len(results) == 0:
        print("No results")
        return None
    # TODO allow user to customize sort
    render_entries(results, ENTRY_NAME_SORT, False)
    return None

def quit():
    return []

COMMANDS = [
    Command(
        ["?","help"], 
        lambda store, args: help(),
        "Prints command help"
    ),
    Command(
        ["tags"],
        lambda store, args: print_tags(),
        "Prints tags in use in the journal"
    ),
    Command(
        ["ls","list"],
        lambda store, args: list_entries(store, args),
        "Lists all entries in the journal"
    ),
    Command(
        ["q","quit","exit"],
        lambda store, args: quit(),
        "Quits the journal CLI"
    ),
]
CMD_ALIAS_TO_FUNC = {}
for cmd in COMMANDS:
    for alias in cmd.aliases:
        CMD_ALIAS_TO_FUNC[alias] = cmd.func

def handle_args(entry_store, args):
    """
    Handles the given user input string
    """
    command = args[0]
    remaining_args = args[1:]
    command_func = CMD_ALIAS_TO_FUNC.get(command.lower(), None)
    if command_func is None:
        print("Unknown command '%s'" % command)
        return None
    return command_func(entry_store, remaining_args)

def main():
    # TODO read a config file to get tag colors
    entry_store = load_entries(JOURNAL_LOC)

    end_args = None
    while end_args is None:
        user_input = input("\n>> ")
        cleaned_input = user_input.strip()
        if len(cleaned_input) == 0:
            continue
        split_input = cleaned_input.split()

        # If end_args is not None, then we're going to break and run the command
        end_args = handle_args(entry_store, split_input)

    if len(end_args) != 0:
        subprocess.run(end_args)

main()

