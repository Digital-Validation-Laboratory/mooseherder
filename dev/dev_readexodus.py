from pprint import pprint
from pathlib import Path
import numpy as np
from mooseherder import ExodusReader
from mooseherder import SimReadConfig

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
    read_config = exodus_reader.get_read_config()
    sim_data = exodus_reader.read_sim_data(read_config)

    np.set_printoptions(precision=6,edgeitems=1,linewidth=100,threshold=10)
    pprint(sim_data.node_vars['disp_x'][:,-1])


if __name__ == '__main__':
    main()