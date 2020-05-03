import os
import subprocess
import re
import argparse
import model
import commands

# TODO change to parameterization
JOURNAL_LOC = os.path.expanduser("~/gdrive/journal")

# Files with this pattern won't be loaded to the entry store
BLACKLISTED_PATTERNS = [
    r".*\.swp$",
    r"^.git$",
]
COMPILED_BLACKLISTED_PATTERNS = [re.compile(pattern) for pattern in BLACKLISTED_PATTERNS]


# Classes ====================================================================================================


# Helper Functions ====================================================================================================
def is_valid_journal_entry(journal_dirpath, filename):
    result = os.path.isfile(os.path.join(journal_dirpath, filename))
    for pattern in COMPILED_BLACKLISTED_PATTERNS:
        return result and not pattern.match(filename)
    return result

def load_entries(journal_dirpath):
    journal_filenames = [filename for filename in os.listdir(journal_dirpath) if is_valid_journal_entry(journal_dirpath, filename)]
    entries = [ model.EntryAndMetadata(filename) for filename in journal_filenames]
    return model.EntryStore(entries)

TIMESTAMP_SORT = "TIME"
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

def search_by_name(entry_store, args):
    results = entry_store.get_by_name(user_input)
    if len(results) == 0:
        print("No results")
        return None
    # TODO allow user to customize sort
    render_entries(results, ENTRY_NAME_SORT, False)
    return None

def quit():
    return []

"""
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
"""



def main():
    # TODO read a config file to get tag colors
    entry_store = load_entries(JOURNAL_LOC)

    command_parser = commands.CommandParser().register_command(
        commands.ListCommand(entry_store)
    )

    end_args = None
    while end_args is None:
        user_input = input("\n>> ")

        cleaned_input = user_input.strip()
        if len(cleaned_input) == 0:
            continue
        split_input = cleaned_input.split()

        # If end_args is not None, then we're going to break and run the command
        end_args = command_parser.handle_input(split_input)

    if len(end_args) != 0:
        subprocess.run(end_args)

main()

