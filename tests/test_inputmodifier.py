#
#
#

import pytest
from mooseherder.inputmodifier import InputModifier

def test_moose_write():
    input_file = 'examples/model-mech-test.i'
    input_modifier = InputModifier(input_file,'#','')
    input_modifier.write_file('/home/rspencer/mooseherder/examples/model-mech-test_mod.i')