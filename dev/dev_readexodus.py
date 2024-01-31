from pprint import pprint
from pathlib import Path
import numpy as np
from mooseherder import ExodusReader

USER_DIR = Path.home()

def main() -> None:
    """main _summary_
    """
    print('----------------------------------------------------------')
    #output_file = Path('scripts/moose/moose-mech-outtest_out.e')

    output_file = Path('scripts/moose-test-cases/moose-mech-subdom-2d-o2_out.e')
    print('Reading exodus file:')
    print(output_file)
    print()

    exodus_reader = ExodusReader(output_file)

    print('Printing all variable keys in exodus file:')
    exodus_reader.print_vars()
    print()
    print('----------------------------------------------------------')

    #print(exodus_reader.get_var('connect1'))
    #print(exodus_reader.get_names('connect1'))
    #print(exodus_reader._data.variables['ss_names'])
    #print(exodus_reader.get_connectivity_names())
    pprint(exodus_reader.get_var('side_ss2'))
    pprint(exodus_reader.get_var('node_ns2').shape)
    pprint(exodus_reader.get_var('elem_ss2'))

if __name__ == '__main__':
    main()