'''
==============================================================================
RUN ALL: helper script to run all examples to check for errors

Author: Lloyd Fletcher
==============================================================================
'''
import os
import subprocess
from pprint import pprint

example_dir = 'examples/'
all_files = os.listdir(example_dir)

example_files = list()
for ff in all_files:
    if ('ex' in ff) and ('.py' in ff):
        example_files.append(example_dir + ff)

example_files.sort()
print('Running all examples files listed below:')
pprint(example_files)
print()

for ee in example_files:
    run_str = 'python '+ ee
    print(run_str)
    subprocess.run(run_str, shell=True)





