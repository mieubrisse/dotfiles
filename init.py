#!/usr/bin/python

import os
import sys
import json
import subprocess
import shutil


# Add symlinks
def process_brews(brews_obj):
    # Stubbed out for now
    print "Nothing here!"

def yes_no_prompt(prompt):
    """Give user prompt and wait for a 'y' or 'n' input"""
    print prompt
    while True:
	choice = raw_input("[Yn]: ")
	choice = choice.strip().lower()
	if choice == "y": 
	    return True
        elif choice == "n":
            return False
        print "Invalid input"

def process_symlinks(symlink_obj):
    """Processes a 'symlink' block of the config file"""
    for link, dest in symlink_obj.iteritems():
        link = os.path.abspath(os.path.expanduser(link))
        dest = os.path.abspath(os.path.expanduser(dest))
        
        # Make sure destination exists
        if not os.path.exists(dest):
            print >> sys.stderr, "Error linking %s -> %s: No file found at %s; skipping link" % (link, dest, dest)
            continue

        # Give user option to overwrite existing file if link path already exists
        # Compare with islink() first so Python will test if the link itself exists
        if os.path.islink(link) or os.path.exists(link):
            # Don't bother user with prompt if link already exists and points to right spot!
            if os.path.samefile(link, dest):
                print "Skipping link %s -> %s: link already exists" % (link, dest)
                continue

	    if not yes_no_prompt("Error linking %s -> %s: File already exists at %s; overwrite?"  % (link, dest, link)):
	        continue
            
            # If user chose to overwrite, delete existing file or directory
	    if os.path.islink(link):
		os.unlink(link)
            elif os.path.isfile(link):
                os.remove(link)
            elif os.path.isdir(link):
                shutil.rmtree(link)
            else:
                print >> sys.stderr, "Unable to delete file at %s" % (lik)
                continue
        os.symlink(dest, link)
        print "Successfully linked %s -> %s" % (link, dest)

def process_block(config_obj):
    """Processes the config array to ensure a setup ordering"""
    for block in config_obj:
        process_symlinks(block["symlinks"])

os.chdir(os.path.dirname(sys.argv[0]))
subprocess.call(["git", "submodule", "update", "--init", "--recursive"])

config_file = open("config.json", "r")
config_obj = json.load(config_file)
process_block(config_obj)

