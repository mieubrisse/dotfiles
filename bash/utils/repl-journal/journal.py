import os
import subprocess
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


def main():
    # TODO read a config file to get tag colors
    entry_store = model.EntryStore(JOURNAL_LOC, BLACKLISTED_PATTERNS)

    output_record = commands.ReferenceableOutputRecord()
    command_parser = commands.CommandParser(output_record).register_command(
        commands.ListCommand(entry_store)
    ).register_command(
        commands.PrintTagsCommand(entry_store)
    ).register_command(
        commands.FindCommand(entry_store)
    ).register_command(
        commands.VimCommand(output_record, entry_store)
    ).register_command(
        commands.AddCommand(output_record, entry_store)
    ).register_command(
        commands.QuitCommand()
    )

    end_args = None
    while end_args is None:
        try:
            user_input = input("\n>> ")
        except EOFError:
            end_args = []
            break
        except KeyboardInterrupt:
            end_args = []
            break

        cleaned_input = user_input.strip()
        if len(cleaned_input) == 0:
            continue
        split_input = cleaned_input.split()

        # If end_args is not None, then we're going to break and run the command
        cmd_output = command_parser.handle_input(split_input)
        end_args = cmd_output.get_end_args()

    if len(end_args) != 0:
        subprocess.run(end_args)

main()

