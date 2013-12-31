#!/usr/bin/python

import os
import sys
import json
import subprocess

os.chdir(os.path.dirname(sys.argv[0]))
subprocess.call(["git", "submodule", "update", "--init", "--recursive"])

config_file = open("config.json")
config = json.load(config_file)

# Add symlinks
symlinks = config['symlinks']
for link, dest in symlinks.iteritems():
    link = os.path.abspath(os.path.expanduser(link))
    dest = os.path.abspath(os.path.expanduser(dest))
    
    # Make sure destination exists
    if not os.path.exists(dest):
        print >> sys.stderr, "Error in linking %s -> %s: No file found at %s; skipping link" % (link, dest, dest)
        continue
    # Give user option to overwrite existing file if link path already exists
    if os.path.exists(link):
        while True:
            choice = raw_input("Error in linking %s -> %s: File already exists at %s; overwrite? (y/n): " % (link, dest, link))
            # choice = raw_input("File already exists at " + str(link) + "; overwrite? (y/n): ")
            choice = choice.strip().lower()
            if choice == "y" or choice == "n":
                break
        if choice == "n":
            continue

    os.symlink(dest, link)
    print "Successfully created link %s -> %s" % (link, dest)

