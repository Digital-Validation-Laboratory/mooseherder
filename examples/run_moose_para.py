#==============================================================================
# RUN PARALLEL MOOSE FROM PYTHON 
#
# Author: Lloyd Fletcher
#==============================================================================

import os

n_tasks = os.cpu_count()
print(n_tasks)