import abc
import argparse
from enum import Enum

class AbstractCommand(abc.ABC):
    def __init__(self, cmd_str, help_str):
        self._cmd_str = cmd_str.strip().lower()
        self._help_str = help_str
        self._parser = argparse.ArgumentParser(prog=self._cmd_str)
        self._parser_configured = False

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
        if not self._parser_configured:
            self.configure_parser(self._parser)
            self._parser_configured = True
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

class AbstractEntryListingCommand(AbstractCommand):
    """
    Abstract class for listing entries
    """
    _SORT_TYPE_ARG = "sort_type"
    _REVERSE_ARG = "reverse"

    _TIMESTAMP_SORT = "time"
    _ENTRY_NAME_SORT = "name"
    _ENTRY_SORTING_FUNCS = {
        _TIMESTAMP_SORT: lambda entry_and_metadata: entry_and_metadata.creation_timestamp,
        _ENTRY_NAME_SORT: lambda entry_and_metadata: entry_and_metadata.pseudo_name,
    }

    def __init__(self, cmd_str, help_str):
        super().__init__(cmd_str, help_str)

    def configure_parser(self, parser):
        parser.add_argument(
            "-s",
            dest=AbstractEntryListingCommand._SORT_TYPE_ARG,
            choices=AbstractEntryListingCommand._ENTRY_SORTING_FUNCS.keys(),
            default=AbstractEntryListingCommand._TIMESTAMP_SORT,
            help="Sort the response by the given value",
        )
        parser.add_argument(
            "-r",
            dest=AbstractEntryListingCommand._REVERSE_ARG,
            default=False,
            action="store_true",
            help="Reverse sort direction",
        )
        # TODO something here to make sure they don't override an existing flag?
        self.configure_listing_parser(parser)

    def run_specific_logic(self, parsed_args):
        entries = self.get_entries(parsed_args)
        sort_type = parsed_args[AbstractEntryListingCommand._SORT_TYPE_ARG]
        sort_reverse = parsed_args[AbstractEntryListingCommand._REVERSE_ARG]

        if len(entries) == 0:
            print("  No results")
        else:
            sort_func = AbstractEntryListingCommand._ENTRY_SORTING_FUNCS[sort_type]
            sorted_entries = sorted(
                entries,
                key=sort_func,
                reverse=sort_reverse
            )
            for entry in sorted_entries:
                print(entry)
        return None

    @abc.abstractmethod
    def configure_listing_parser(self, parser):
        """
        Extra parser configuration for the specific entry-listing subclasses
        """
        return

    @abc.abstractmethod
    def get_entries(self, parsed_args):
        """
        Get the journal entries that will be displayed (order will be discarded)
        """
        return

class ListCommand(AbstractEntryListingCommand):

    def __init__(self, entry_store):
        super().__init__("ls", "Lists journal entries")
        self._entry_store = entry_store

    def configure_listing_parser(self, parser):
        pass

    def get_entries(self, parsed_args):
        return self._entry_store.get_all()

class FindCommand(AbstractEntryListingCommand):
    _TAG_FIND_TYPE = "tag"
    _NAME_FIND_TYPE = "name"

    _FIND_TYPE_ARG = "find_type"
    _SEARCH_TERM_ARG = "search_term"

    def __init__(self, entry_store):
        super().__init__("find", "Finds journal entries using a search term")
        self._entry_store = entry_store
        self._find_funcs = {
            FindCommand._TAG_FIND_TYPE: lambda keyword: self._entry_store.get_by_tag(keyword),
            FindCommand._NAME_FIND_TYPE: lambda keyword: self._entry_store.get_by_name(keyword),
        }

    def configure_listing_parser(self, parser):
        parser.add_argument(
            "-t",
            dest=FindCommand._FIND_TYPE_ARG,
            action="store_const",
            const=FindCommand._TAG_FIND_TYPE,
            help="Search for a tag",
        )
        parser.add_argument(
            FindCommand._SEARCH_TERM_ARG,
            help="Term to search for",
        )

    def get_entries(self, parsed_args):
        find_type = parsed_args.get(FindCommand._FIND_TYPE_ARG)
        # Default to name find if no flag was specified
        find_type = find_type if find_type is not None else FindCommand._NAME_FIND_TYPE

        term = parsed_args[FindCommand._SEARCH_TERM_ARG]
        find_func = self._find_funcs[find_type]
        return find_func(term)

class PrintTagsCommand(AbstractCommand):
    def __init__(self, entry_store):
        super().__init__("tags", "Print tags used in the journal")
        self._entry_store = entry_store

    def configure_parser(self, parser):
        pass

    def run_specific_logic(self, parsed_args):
        tags = sorted(self._entry_store.get_tags())
        for tag in tags:
            print(" - %s" % tag)
        return None

class QuitCommand(AbstractCommand):
    def __init__(self):
        super().__init__("quit", "Quit the CLI")

    def configure_parser(self, parser):
        pass

    def run_specific_logic(self, parsed_args):
        return []

class CommandParser():
    def __init__(self):
        self._alias_to_cmd = {}

    def register_command(self, cmd):
        alias = cmd.get_cmd_str().strip().lower()
        if alias in self._alias_to_cmd.keys():
            raise ValueError("Cannot register command with alias '%s'; this alias has already been registered" % alias)
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
        print("")
        for cmd_str, cmd in self._alias_to_cmd.items():
            padded_cmd_str = ("  " + cmd_str).ljust(25, " ")
            print("  %s%s" % (padded_cmd_str, cmd.get_help_str()))
