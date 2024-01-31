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

    output_file = Path('tests/output/moose-mech-outtest_out.e')
    print('Reading exodus file:')
    print(output_file)
    print()

    exodus_reader = ExodusReader(output_file)

    print('Printing all variable keys in exodus file:')
    exodus_reader.print_vars()
    print()
    print('----------------------------------------------------------')
    sim_data = exodus_reader.read_all_sim_data()
    #print(exodus_reader.get_var('connect1'))
    #print(exodus_reader.get_names('connect1'))
    #print(exodus_reader._data.variables['ss_names'])
    #print(exodus_reader.get_connectivity_names())
    np.set_printoptions(precision=6,edgeitems=1,linewidth=100,threshold=10)
    pprint(sim_data.node_vars['disp_x'][:,-1])


if __name__ == '__main__':
    main()