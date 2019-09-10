import os
from shutil import copyfile

# add files to bin directory so they can be run from anywhere.

username = os.getcwd().split('/')[2]
bin_dir = f"/Users/{username}/bin"
cwd = os.path.abspath(os.path.dirname(__file__))

# create ~/bin if it doesn't already exist.
try:
    os.mkdir(bin_dir)
except FileExistsError:
    pass

# copy report.py to bin
copyfile(cwd + "/report.py", bin_dir + "/report.py")

# create new executable to run script
with open('bin_dir' + '/power-scraper', 'w+') as f:
    f.write('#!/bin/bash\npython3 ~bin/report.py $@')