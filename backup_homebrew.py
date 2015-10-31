'''
Downloads all packages and casks the user has installed via Homebrew to a JSON file, and optionally runs Git commit & push if the output file is in a Git repo
Author: mieubrisse
'''

import argparse
import subprocess
import os
import re
import sys
import json

_OUTPUT_FILEPATH_ARGVAR = "output_filepath"
_DO_GIT_COMMIT_ARGVAR = "do_git_commit"
_GIT_COMMIT_MESSAGE_ARGVAR = "git_commit_message"

_BREW_CMD = "brew"
_CASK_BREWNAME = "caskroom/cask/brew-cask"
_DEFAULT_GIT_COMMIT_MSG = "Automated Homebrew backup"

def _parse_args(argv):
    ''' Parses args into a dict of ARGVAR=value, or None if the argument wasn't supplied '''
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(_OUTPUT_FILEPATH_ARGVAR, metavar="<output JSON file>", help="Destination to output file")
    parser.add_argument("-c", "--git-commit", dest=_DO_GIT_COMMIT_ARGVAR, action="store_true", default=False, help="Git commit & push the output file to the repo it's inside")
    parser.add_argument("-m", "--commit-message", dest=_GIT_COMMIT_MESSAGE_ARGVAR, metavar="<commit message>", default=_DEFAULT_GIT_COMMIT_MSG, help="Commit message to use when pushing Homebrew changes")
    return vars(parser.parse_args(argv))

def _validate_args(args):
    return None
 
def _print_error(msg):
    sys.stderr.write('Error: ' + msg + '\n')

def _get_brews():
    package_version_lines = subprocess.check_output([_BREW_CMD, "list", "--versions"]).splitlines()
    split_lines = (line.split() for line in package_version_lines )
    package_versions = { items[0]: items[1:] for items in split_lines }

    user_installed_packages = subprocess.check_output([_BREW_CMD, "leaves"]).splitlines()
    return_obj = {}
    for package in user_installed_packages:
        package_info = subprocess.check_output([_BREW_CMD, "info", package])
        matches = re.search('Built from source with:(.*)$', package_info, re.MULTILINE)
        package_options = matches.group(1).split() if matches else []
        return_obj[package] = { 
                # Sorting is necessary because the order we get these from Homebrew is non-deterministic
                # If we don't sort, we'll be committing changes in ordering constantly
                "versions": sorted(package_versions[os.path.basename(package)]),
                "options": sorted(package_options),
                }
    return return_obj

def main(argv):
    args = _parse_args(map(str, argv))
    err = _validate_args(args)
    if err is not None:
        return err

    output_filepath = os.path.realpath(args[_OUTPUT_FILEPATH_ARGVAR])
    do_git_commit = args[_DO_GIT_COMMIT_ARGVAR]
    commit_msg = args[_GIT_COMMIT_MESSAGE_ARGVAR]

    if subprocess.call(["command", "-v", _BREW_CMD, ], stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT) != 0:
        _print_error("No homebrew found")
        return 1

    return_obj = {}
    brews = _get_brews()
    return_obj["brews"] = brews
    return_obj["taps"] = subprocess.check_output([_BREW_CMD, "tap"]).splitlines()

    casks_list = subprocess.check_output([_BREW_CMD, "cask", "list"]).splitlines() if _CASK_BREWNAME in brews else []
    return_obj["casks"] = casks_list

    with open(output_filepath, 'w') as output_fp:
        json.dump(return_obj, output_fp, indent=4, sort_keys=True)

    if do_git_commit:
        output_dirpath = os.path.dirname(output_filepath)
        git_cmd = ["git", "-C", output_dirpath]

        if subprocess.call(git_cmd + ["diff", "--quiet", output_filepath]) == 1:
            git_commands = [
                    ["add", output_filepath], 
                    ["commit", "-m", commit_msg], 
                    # TODO Debugging
                    # git_cmd + ["push"],
                    ]
            git_commands = map(lambda command_fragment: git_cmd + command_fragment, git_commands)
            for command in git_commands:
                try:
                    subprocess.check_output(command, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as e:
                    _print_error("'{}' failed with exit code {} and output:\n{}".format(" ".join(command), e.returncode, e.output))
                    return 1

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
