#!/usr/bin/python

import os.path
import sys

CD_HIST_FILENAME = ".cd_history"
CD_HIST_FILEPATH = os.path.abspath(os.path.join(os.path.expanduser("~"), CD_HIST_FILENAME))

# Create the file if it doesn't exist
open(CD_HIST_FILEPATH, 'a').close()

cdhist_fp = open(CD_HIST_FILEPATH, 'rw')
cd_hist = cdhist_fp.read().splitlines()
if len(cd_hist) == 0:
    "No cd history"
    sys.exit()

# Print elements
for index, hist_elem in enumerate(cd_hist[-20:]):
    print str(index) + "\t" + hist_elem

print cd_hist

cdhist_fp.close()
