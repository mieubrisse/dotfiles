import abc
import argparse
from enum import Enum

class AbstractCommand(abc.ABC):
    def __init__(self, cmd_str, help_str):
        self._cmd_str = cmd_str.strip().lower()
        self._parser = argparse.ArgumentParser(prog=self._cmd_str)
        self.configure_parser(self._parser)

    def execute(self, args):
        """
        Called when the user calls this function

        Args:
        args: user arguments to this command, if any

        Returns:
        None to indicate that the journal CLI should keep running, or an array
            of args to run after the journal CLI exits if this command is to exit
            the CLI.
        """
        try:
            parsed_args = vars(self._parser.parse_args(args))
        except SystemExit:
            return None
        return self.run_specific_logic(parsed_args)


    def get_cmd_str(self):
        """
        Returns:
        The string identifying this command
        """
        return self._cmd_str

    def get_help_str(self):
        return self._help_str

    @abc.abstractmethod
    def configure_parser(self, parser):
        """
        Abstract method for registering the appropriate args on the parser

        Args:
        parser: argparse parser that should have add_argument calls made on it
        """
        return

    @abc.abstractmethod
    def run_specific_logic(self, parsed_args):
        """
        Runs command-specific logic

        Args:
        parsed_args: results of parsing using the configured parser

        Returns:
        If this command should end the CLI, return a list of args to exit the
            journal CLI with (empty list to run nothing); if the CLI should keep
            running, returns None
        """
        return

class ListCommand(AbstractCommand):
    _SORT_TYPE_ARG = "sort_type"
    _REVERSE_ARG = "reverse"

    _TIMESTAMP_SORT = "time"
    _ENTRY_NAME_SORT = "name"
    _ENTRY_SORTING_FUNCS = {
        _TIMESTAMP_SORT: lambda entry_and_metadata: entry_and_metadata.creation_timestamp,
        _ENTRY_NAME_SORT: lambda entry_and_metadata: entry_and_metadata.pseudo_name,
    }

    def __init__(self, entry_store):
        super().__init__("ls", "Lists journal entries")
        self._entry_store = entry_store

    def configure_parser(self, parser):
        parser.add_argument(
            "-s",
            dest=ListCommand._SORT_TYPE_ARG,
            choices=ListCommand._ENTRY_SORTING_FUNCS.keys(),
            default=ListCommand._ENTRY_NAME_SORT,
            action="store"
        )
        parser.add_argument(
            "-r",
            dest=ListCommand._REVERSE_ARG,
            default=False,
            action="store_true"
        )

    def run_specific_logic(self, parsed_args):
        results = self._entry_store.get_all()
        if len(results) == 0:
            print("No entries")
            return None

        # TODO break this out to its own class
        ListCommand._render_entries(
            results,
            parsed_args[ListCommand._SORT_TYPE_ARG],
            parsed_args[ListCommand._REVERSE_ARG],
        )
        return None

    # TODO break this into a parent class
    def _render_entries(entries, entry_sort_type, sort_reverse):
        if len(entries) == 0:
            print("              \033[90m<No results>")
            return

        sorted_entries = sorted(entries, key=ListCommand._ENTRY_SORTING_FUNCS[entry_sort_type], reverse=sort_reverse)
        for entry in sorted_entries:
            print(entry)

class CommandParser():
    def __init__(self):
        self._alias_to_cmd = {}

    def register_command(self, cmd):
        alias = cmd.get_cmd_str().strip().lower()
        if alias in self._alias_to_cmd.keys():
            raise ValueError("Cannot register command with alias '%s'; this alias has already been registered")
        self._alias_to_cmd[alias] = cmd
        return self

    def handle_input(self, user_input):
        """
        Args:
        user_input: array of user input
        """
        command_str = user_input[0].lower()
        if command_str == "help":
            self._print_help()
            return None

        remaining_input = user_input[1:]
        command = self._alias_to_cmd.get(command_str, None)
        if command is None:
            print("Unknown command '%s'" % command_str)
            return None
        return command.execute(remaining_input)

    def _print_help(self):
        """
        Prints help strings for all registered commands
        """
        for cmd_str, cmd in self._alias_to_cmd.items():
            padded_cmd_str = ("  " + cmd_str).ljust(25, " ")
            print("  %s%s" % (padded_cmd_str, cmd.get_help_str()))
