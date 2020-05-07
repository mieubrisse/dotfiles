import abc
import argparse
from enum import Enum, auto

class CommandOutputRecord:
    """
    Supplier-type class containing the CommandOutput of the last-ran command
    """
    def __init__(self):
        self._last_output = None

    def get_last_output(self):
        return self._last_output

    def set_last_output(self, output):
        self._last_output = output

class CommandResultType(Enum):
    TAG = auto()
    JOURNAL_ENTRY = auto()

class CommandOutput:
    """
    Object which each command must return containing various metadata about how the CLI should proceed
    """
    def __init__(self, result_list, result_type, end_args):
        """
        Args:
            result_list: List of results that the command returned, which can be used as references for the
                input into future commands. None and empty array have the same significance here - no results
                were returned, so the user cannot use this command's output for future references.
            result_type: Type of result contained inside the result_list (if any), which dictates what the
                user can do with the results in future commands.
            end_args: If None, indicates that the CLI should continue after this command; if empty array,
                it means the CLI should exit without doing anything, and if this is anything other than empty
                array then this command will be executed as the CLI exits.
        """
        self._result_list = list(result_list) if result_list is not None else []
        self._result_type = result_type
        self._end_args = end_args

    def get_result_list(self):
        return self._result_list

    def get_result_type(self):
        return self._result_type

    def get_end_args(self):
        return self._end_args

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
            An instance of CommandOutput encapsulating the results of running the user's command
        """
        if not self._parser_configured:
            self.configure_parser(self._parser)
            self._parser_configured = True
        try:
            parsed_args = vars(self._parser.parse_args(args))
        except SystemExit:
            return CommandOutput(None, None, None)
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

class QuitCommand(AbstractCommand):
    def __init__(self):
        super().__init__("quit", "Quit the CLI")

    def configure_parser(self, parser):
        pass

    def run_specific_logic(self, parsed_args):
        return CommandOutput(None, None, [])

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
        sort_func = AbstractEntryListingCommand._ENTRY_SORTING_FUNCS[sort_type]
        sorted_entries = sorted(
            entries,
            key=sort_func,
            reverse=sort_reverse
        )

        if len(sorted_entries) == 0:
            print("  No results")
        else:
            for entry in sorted_entries:
                print(entry)

        entry_ids = [entry.get_id() for entry in sorted_entries]
        return CommandOutput(entry_ids, CommandResultType.JOURNAL_ENTRY, None)

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
        return CommandOutput(tags, CommandResultType.TAG, None)


class AbstractResultConsumingCommand(AbstractCommand):
    """
    Abstract base class for commands that consume the output of previous commands
    """

    # Character used to indicate that previous results should be used
    REFERENCE_LEADER = "@"

    _INPUT_ARG = "input"

    def __init__(self, cmd_str, help_str, cmd_output_record):
        super().__init__(cmd_str, help_str)
        self._cmd_output_record = cmd_output_record

    def configure_parser(self, parser):
        parser.add_argument(AbstractResultConsumingCommand._INPUT_ARG, nargs="+")
        self.configure_result_consuming_parser(parser)

    def run_specific_logic(self, parsed_args):
        input_items = parsed_args[AbstractResultConsumingCommand._INPUT_ARG]
        transformed_items = list(input_items)

        # Validate we're consuming the appropriate result type
        expected_output_type = self.get_consumed_result_type()
        for idx, item in enumerate(input_items):
            if not item.startswith(AbstractResultConsumingCommand.REFERENCE_LEADER):
                continue

            last_cmd_output = self._cmd_output_record.get_last_output()
            if last_cmd_output is None:
                print("Reference error with '%s': No previous command results to use!" % item)
                return CommandOutput(None, None, None)

            output_results = last_cmd_output.get_result_list()
            if len(output_results) == 0:
                print("Reference error with '%s': Previous command did not return any results and so cannot be referenced" % item)
                return CommandOutput(None, None, None)

            output_type = last_cmd_output.get_result_type()
            if output_type != expected_output_type:
                print("Reference error with '%s': Expected result type '%s' but previous command's result type was '%s'" % (item, expected_output_type, output_type))
                return CommandOutput(None, None, None)

            reference_idx_str = item.lstrip(AbstractResultConsumingCommand.REFERENCE_LEADER)
            try:
                reference_idx = int(reference_idx_str)
            except ValueError:
                print("Reference error with '%s': Must be an integer list index" % item)
                return CommandOutput(None, None, None)
            if not (reference_idx >= 0 and reference_idex < len(output_results)):
                print("Reference error with '%s': Index is out-of-bounds of prevoius result list" % item)
                return CommandOutput(None, None, None)
            transformed_items[idx] = output_results[reference_idx]

        return self.process_transformed_input(transformed_items)

    @abc.abstractmethod
    def get_consumed_result_type(self):
        """
        The type of result that this command consumes
        """
        return

    @abc.abstractmethod
    def configure_result_consuming_parser(self):
        """
        Extra command-specific parser configuration
        """
        return

    @abc.abstractmethod
    def process_transformed_input(self, transformed_input):
        """
        Run logic on the user's input, with references already transformed
        """
        return

class VimCommand(AbstractResultConsumingCommand):
    """
    Command to open journal entries in Vim
    """

    def __init__(self, cmd_output_record):
        super().__init__("vim", "Opens journal entries in Vim, using 'vsp' if more than one entry is given", cmd_output_record)

    def configure_result_consuming_parser(self, parser):
        pass

    def get_consumed_result_type(self):
        return CommandResultType.JOURNAL_ENTRY

    def process_transformed_input(self, transformed_input):
        for item in transformed_input:
            print("Would open %s" % item)
        return CommandOutput(None, None, None)

class CommandParser():
    """
    Lookup class to take in a user's input and call the appropriate registered command
    """

    def __init__(self, cmd_output_record):
        self._alias_to_cmd = {}
        self._cmd_output_record = cmd_output_record

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
        if command is not None:
            cmd_output = command.execute(remaining_input)
        else:
            print("Unknown command '%s'" % command_str)
            cmd_output = CommandOutput(None, None, None)
        self._cmd_output_record.set_last_output(cmd_output)
        return cmd_output

    def _print_help(self):
        """
        Prints help strings for all registered commands
        """
        print("")
        for cmd_str, cmd in self._alias_to_cmd.items():
            padded_cmd_str = ("  " + cmd_str).ljust(25, " ")
            print("  %s%s" % (padded_cmd_str, cmd.get_help_str()))
