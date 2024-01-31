from pprint import pprint
from pathlib import Path
import numpy as np
from mooseherder import ExodusReader
from mooseherder import SimData

USER_DIR = Path.home()

def main() -> None:
    """main _summary_
    """
    print('----------------------------------------------------------')
    #output_file = Path('scripts/moose/moose-mech-outtest_out.e')

    output_file = Path('tests/output/moose-mech-outtest_out.e')
    print('Reading exodus file:')
    print(output_file)
    print()

    exodus_reader = ExodusReader(output_file)

    print('Printing all variable keys in exodus file:')
    exodus_reader.print_vars()
    print()
    print('----------------------------------------------------------')
    sim_data = exodus_reader.read_sim_data()
    #print(exodus_reader.get_var('connect1'))
    #print(exodus_reader.get_names('connect1'))
    #print(exodus_reader._data.variables['ss_names'])
    #print(exodus_reader.get_connectivity_names())
    pprint(sim_data.time.shape)
    pprint(sim_data.glob_vars['react_y'].shape)


if __name__ == '__main__':
    main()