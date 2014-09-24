#!/usr/bin/python

import sys

dev_tty = open("/dev/tty", "w")
def print_msg(msg):
    print >> dev_tty, msg

def validate_choices(choice_str, input_lines):
    """Validates the user's string of choices, returning the choices object if successful or raising a RuntimeError if not"""
    indices = []
    choices = map(str.strip, choice_str.split(","))
    for choice in choices:
        # Ignore empty selections
        if not choice:
            continue

        choice_range = map(str.strip, choice.split("-"))

        # Single choice case
        if len(choice_range) == 1:
            index = choice_range[0]
            try:
                indices.append([int(index)])
            except ValueError:
                raise RuntimeError("Choice '" + choice_range + "' must be a digit: " + choice)

        # Choice range case
        elif len(choice_range) == 2:
            if not (choice_range[0].isdigit() and choice_range[1].isdigit()):
                raise RuntimeError("Choice range '%s-%s' must be digits" % (choice_range[0], choice_range[1]))
            range_start = int(choice_range[0])
            range_end = int(choice_range[1])
            if range_start >= range_end:
                raise RuntimeError("Range start '%d' must be less than range end '%d'" % (range_start, range_end))
            if range_start < 0:
                raise RuntimeError("Range start must be >= 0" % (range_start))
            if range_end >= len(input_lines):
                raise RuntimeError("Range end '%d' must be less than the list length" % (range_end))
            indices.append([range_start, range_end])

        # WTF case
        else:
            raise RuntimeError("Invalid selection: " + choice)

    # User selected no choices
    if len(indices) == 0:
        raise RuntimeError("Select at least one valid index")
    return indices

input_lines = []
for line in sys.stdin:
    line = line.strip()
    input_lines.append(line)

# Change stdin back to user's input
sys.stdin = open('/dev/tty')

results = []
if len(input_lines) == 0:
    print_msg("No results")
elif len(input_lines) == 1:
    print_msg("One result: " + input_lines[0])
    results.append(input_lines[0])
else:
    # Let user choose which lines they want
    for idx, line in enumerate(input_lines):
        print_msg("%i\t%s" % (idx, line))

    selection_valid = False
    indices = []
    while not selection_valid:
        print_msg("Use which? ")
        choice_str = raw_input()
        try: 
            indices = validate_choices(choice_str, input_lines)
            selection_valid = True;
        except RuntimeError as e:
            print_msg(str(e))
    for index_set in indices:
        if len(index_set) == 1:
            results.append(input_lines[index_set[0]])
        elif len(index_set) == 2:
            # Need to increment stop index by 1 for intuitive range behavior
            for index in range(index_set[0], index_set[1] + 1):
                results.append(input_lines[index])
        else:
            print "Ignoring invalid index set: " + str(index_set)

for result in results:
    print result

dev_tty.close()
