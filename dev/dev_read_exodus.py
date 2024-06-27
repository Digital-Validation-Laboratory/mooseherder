from pathlib import Path
from mooseherder import ExodusReader

def main() -> None:
    output_file = Path.home()/'moose-workdir'/'dice_output'/'DICe_solution.e'
    exodus_reader = ExodusReader(output_file)

    sim_data = exodus_reader.read_all_sim_data()

    print()
    print(sim_data.time)
    print(sim_data.coords)
    print(sim_data.node_vars)
    print()

if __name__ == '__main__':
    main()
