import urwid
import re
from collections import defaultdict

"""
if body_focused:
    if leader_char is valid command leader char:
        focus the footer
    else:
        pass keypress through
if footer_focused:
    if enter is pressed:
        execute cmd
    if leader_char is live-reloading leader char and current string + keypress matches the command:
        execute cmd
    pass through
"""
PADDING_COLS = 2

class EagerlyProcessedCommand:
    def __init__(self, command_func, eager_processing_regex_str):
        self.command_func = command_func
        self.eager_processing_regex = re.compile(eager_processing_regex_str)

class CommandRouter:
    def __init__(self):
        # These leader characters will indicate that the user's input ought to be processed eagerly for matching commands
        self.eager_processing_commands = defaultdict(lambda: [])

        # TODO will probably have to rewrite how lazy command are implemented when they become more complex
        # These leader characters indicate that the user's input will be processed only when the user presses enter
        self.lazy_processing_commands = {}

    # TODO Probably cleaner to do this in the constructor
    def add_cmd(self, leader_chars, processor, eager_processing_regex_str=None):
        """
        leader_chars - set of characters that are valid first chars for initiating the given command
        eager_processing_regex_str - regex that, if matched, will call the command function
        """
        for char in set(leader_chars):
            if eager_processing_regex_str is None:
                if char in self.eager_processing_commands.keys():
                    raise ValueError("Cannot register '%s' as lazily-processed - already registered as an eagerly-processed command" % char)
                self.lazy_processing_commands[char] = processor
            else:
                if char in self.lazy_processing_commands.keys():
                    raise ValueError("Cannot register '%s' as eagerly-processed - already registered as a lazily-processed command" % char)
                matching_commands = self.eager_processing_commands[char]
                matching_commands.append(
                    EagerlyProcessedCommand(processor, eager_processing_regex_str)
                )
        return self   # Because fluent APIs are great

    def is_valid_command_leader_char(self, char):
        return char in self.eager_processing_commands.keys() or char in self.lazy_processing_commands.keys()

    def is_eager_processing_leader_char(self, char):
        return char in self.eager_processing_commands.keys()

    def get_matching_processors(self, command_string):
        leader = command_string[0]
        results = []
        if self.is_eager_processing_leader_char(leader):
            leader_matches = self.eager_processing_commands[leader]
            full_matches = filter(lambda command: command.eager_processing_regex.fullmatch(command_string), leader_matches)
            results = [command.command_func for command in full_matches]
        else:
            # TODO I'll probably have to rewrite this one day
            results = [self.lazy_processing_commands[leader]]
        return results

class VimBindingsCheckBox(urwid.CheckBox):
    def keypress(self, size, key):
        if key == 'x':
            key = 'enter'
        return super().keypress(size, key)

class VimBindingsListBox(urwid.ListBox):

    def keypress(self, size, key):
        if key == 'J':
            curr_idx = self.focus_position
            num_items = len(self.body)
            new_idx = min(num_items - 1, curr_idx + 15)
            self.set_focus(new_idx, coming_from='above')
            return None
        if key == 'K':
            curr_idx = self.focus_position
            new_idx = max(0, curr_idx - 15)
            self.set_focus(new_idx, coming_from='below')
            return None
        if key == 'G':
            num_items = len(self.body)
            self.set_focus(num_items - 1, coming_from='above')
            return None
        if key == 'k':
            key = 'up'
        if key == 'j':
            key = 'down'

        return super().keypress(size, key)

class SearchBox(urwid.Edit):
    def keypress(self, size, key):
        if key == 'escape':
            # TODO global variable reference
            frame.set_focus('body')
            return None
        return super().keypress(size, key)

class MainFrame(urwid.Frame):
    def __init__(self, body, footer):
        super().__init__(body, footer=footer)
        # NOTE: this might be slow, matching against everything - I might need to redo this

        self.command_router = CommandRouter().add_cmd(
            ["g"] + [str(i) for i in range(1,10)],
            self._process_jump_command,
            eager_processing_regex_str="(gg|[1-9][0-9]*G)"
        )

    def keypress(self, size, key):
        result = key

        # First try handling with our custom handlers
        if self.get_focus() == 'body':
            result = self._process_body_keypress(key)
        elif self.get_focus() == 'footer':
            result = self._process_footer_keypress(key)

        # If we still haven't handled the keypress, pass it to the superclass
        if result is not None:
            result = super().keypress(size, key)
        return result

    def _process_body_keypress(self, key):
        if self.command_router.is_valid_command_leader_char(key):
            self._focus_footer(key)
            return None
        if key == 'enter':
            # TODO open the thing under the cursor
            return None
        if key == 'a':
            # TODO create a new file
            return None
        if self.command_router.is_valid_command_leader_char(key):
            self._focus_footer(key)
            return None
        return key

    def _process_footer_keypress(self, key):
        if key == 'esc':
            self._quit_command_and_focus_body()
            return None

        command_text = self.contents['footer'][0].get_edit_text()
        if key == 'enter':
            # TODO processs the input!!
            processors = self.command_router.get_matching_processors(command_text)
            if len(processors) == 0:
                # TODO display no valid commands error
                pass
            elif len(processors) >= 2:
                # TODO display ambiguous command error
                pass
            processors[0](command_text)
            self._quit_command_and_focus_body()
            return None

        if key == 'backspace' and len(command_text) == 1:
            self._quit_command_and_focus_body()
            return None

        if self.command_router.is_eager_processing_leader_char(command_text[0]):
            command_to_be = command_text + key
            processors = self.command_router.get_matching_processors(command_to_be)
            if len(processors) == 1:
                processors[0](command_to_be)
                self._quit_command_and_focus_body()
                return None

        return key

    def _focus_footer(self, initiating_char):
        self.contents['footer'][0].insert_text(initiating_char)
        self.focus_position = 'footer'

    def _quit_command_and_focus_body(self):
        self.contents['footer'][0].set_edit_text("")
        self.focus_position = 'body'

    def _process_jump_command(self, command_str):
        body_listbox = self.contents['body'][0]
        output_index = None
        if command_str == "gg":
            output_index = 0
        elif command_str[-1] == "G":
            num_list_items = len(body_listbox.body)
            g_stripped = command_str.rstrip("G")
            try:
                output_index = min(num_list_items, int(g_stripped)) - 1
            except ValueError:
                raise ValueError("Invalid command string '%s' for jump command" % command_str)
        if output_index is None:
            raise ValueError("Invalid command string '%s' for jump command" % command_str)
        body_listbox.set_focus(output_index)

def handle_unhandled_input(key):
    if key == 'q':
        raise urwid.ExitMainLoop()

def main():
    button_list = [VimBindingsCheckBox(str(item)) for item in range(1, 51)]
    listbox = VimBindingsListBox(button_list)
    search_box = urwid.Edit()
    frame = MainFrame(listbox, search_box)
    urwid.MainLoop(
        frame,
        unhandled_input=handle_unhandled_input
    ).run()

main()
