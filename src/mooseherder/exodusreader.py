"""
===============================================================================
EXODUS READER
Used to read output *.e from MOOSE simulations.

There are several different cases that lead to different MOOSE output formats.

1) Outputs can have 2 or 3 spatial dimensions for nodal DOFs
    (e.g. disp_x, disp_y and possibly disp_z)
2) Element output may or may not be present (e.g. stress/strain)
    2.1) Element outputs might appear as nodal variables if
         material_output_order = FIRST or greater
    2.2) Element output is split by block if material_output_order = CONSTANT
4) Sub-domains may or may not be present but see 2.1 above for exception

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
"""
from pathlib import Path
import netCDF4 as nc
import numpy as np
import numpy.typing as npt
from mooseherder.simdata import SimData, SimReadConfig


class ExodusReader:
    """Class to read exodus files output by MOOSE using the netCDF package.
    """
    def __init__(self, exodus_file: Path):
        """__init__: Construct class by reading the exodus file using the
        netCDF package.

        Args:
            exodus_file (Path): path to the exodus file to read

        Raises:
            FileNotFoundError: the specified exodus file does not exist
        """

        if not exodus_file.is_file() and exodus_file.suffix != '.e':
            raise FileNotFoundError('Exodus file not found at specified path')

        self._exodus_path = exodus_file
        self._data = nc.Dataset(str(self._exodus_path))


    def get_names(self, key: str | None) -> npt.NDArray | None:
        """get_names: Extract a list of variable names from the dataset. Useful
        for getting node/element/sideset/global variables names.

        Args:
            key (str | None): string key used to extract a list of names from
                the dataset e.g. 'node_var_names'. If key is None returns None.

        Returns:
            npt.NDArray | None: numpy array of strings representing the names
                that correspond to the variables in the dataset. Returns None
                if the specified key does not exist in the dataset.
        """
        if key not in self._data.variables or key is None:
            return None

        return nc.chartostring(np.array(self._data.variables[key]))


    def get_var(self, key: str) -> npt.NDArray:
        """get_var: Extract a numeric variable from the dataset.

        Args:
            key (str): key corresponding to the variable in the dataset. e.g.
                'time_whole'

        Returns:
            npt.NDArray: numpy numeric array containing the variable data.
        """
        if key not in self._data.variables:
            return np.array([])

        return np.array(self._data.variables[key]).T


    def get_connectivity_names(self) -> npt.NDArray:
        """get_connectivity_names:

        Returns:
            npt.NDArray: array of element connectivity keys as strings of the
                form connectX where X is an integer of 1 or greater e.g.
                connect1.
        """
        names = np.array([])
        for bb in range(self.get_num_elem_blocks()):
            key = f'connect{bb+1:d}'
            if key in self._data.variables:
                names = np.append(names,key)

        return names


    def get_connectivity(self) -> dict[str,npt.NDArray]:
        """get_connectivity:

        Returns:
            dict[str,npt.NDArray]: dictionary containing the element
                connectivity tables based on keys related to the subdomain e.g.
                key 'connect1' returns the element connectivity table for
                subdomain 1. The table has dimensions N by n_e where N is the
                total number of nodes in the subdomain and n_e is the number
                of nodes per element.
        """
        connect = dict({})
        for key in self.get_connectivity_names():
            connect[key] = self.get_var(key)

        return connect


    def get_sideset_names(self) -> npt.NDArray | None:
        """get_sideset_names:

        Returns:
            npt.NDArray | None: numpy array of strings corresponding to the
                sideset names specified in the simulation. Returns None if no
                sideset names are found.
        """
        return self.get_names('ss_names')


    def get_sidesets(self, names: npt.NDArray | None
                     ) -> dict[tuple[str,str], npt.NDArray] | None:
        """get_sidesets:

        Args:
            names (npt.NDArray | None): numpy array of strings specifying the
                sideset names to extract from the dataset. If None return None.

        Returns:
            dict[tuple[str,str], npt.NDArray] | None: dictionary of sideset
                nodes and element sets by name. The key is a tuple with the
                first string being the sideset name and the second being either
                'node' or 'elem'. Returns None if no sidesets found.
        """
        if names is None:
            return None

        node_key_tag = 'node_ns'
        elem_key_tag = 'elem_ss'

        side_sets = dict({})
        for ii,nn in enumerate(names): # type: ignore
            node_key = f'{node_key_tag}{ii+1:d}'
            elem_key = f'{elem_key_tag}{ii+1:d}'

            side_sets[(nn,'node')] = self.get_var(node_key)
            side_sets[(nn,'elem')] = self.get_var(elem_key)

        return side_sets


    def get_all_sidesets(self) -> dict[tuple[str,str], npt.NDArray] | None:
        """get_all_sidesets:

        Returns:
            dict[tuple[str,str], npt.NDArray] | None: dictionary of sideset
                nodes and element sets by name. The key is a tuple with the
                first string being the sideset name and the second being either
                'node' or 'elem'. Returns None if no sidesets found.
        """

        return self.get_sidesets(self.get_sideset_names())


    def get_node_var_names(self) -> npt.NDArray | None:
        """get_node_var_names:

        Returns:
            npt.NDArray | None: numpy array of strings containing the nodal
                variable names. Returns None if no nodal variables are found.
        """
        return self.get_names('name_nod_var')


    def get_node_vars(self, names: npt.NDArray | None) -> dict[str,npt.NDArray] | None:
        """get_node_vars:

        Args:
            names (npt.NDArray | None): numpy array of strings that are the
                variable

        Returns:
            dict[str,npt.NDArray] | None: _description_
        """
        if names is None:
            return None

        key_tag = 'vals_nod_var'
        vars = dict({})

        for ii,nn in enumerate(names): # type: ignore
            key = f'{key_tag}{ii+1:d}'
            vars[nn] = self.get_var(key)

        return vars


    def get_all_node_vars(self) -> dict[str, npt.NDArray] | None:
        """get_all_node_vars _summary_

        Returns:
            dict[str, npt.NDArray] | None: _description_
        """
        return self.get_node_vars(self.get_node_var_names())


    def get_elem_var_names(self) -> npt.NDArray | None:
        """get_elem_var_names _summary_

        Returns:
            npt.NDArray | None: _description_
        """
        return self.get_names('name_elem_var')


    def get_elem_var_names_and_blocks(self) -> list[tuple[str,int]] | None:
        """get_elem_var_names_and_blocks _summary_

        Returns:
            list[tuple[str,int]] | None: _description_
        """
        if self.get_elem_var_names is None or self.get_num_elem_blocks() is None:
            return None

        blocks = [ii+1 for ii in range(self.get_num_elem_blocks())] # type: ignore
        names_blocks = list([])

        for nn in self.get_elem_var_names(): # type: ignore
            for bb in blocks:
                names_blocks.append((str(nn),bb))

        return names_blocks


    def get_num_elem_blocks(self) -> int:
        """get_num_elem_blocks _summary_

        Returns:
            int: _description_
        """
        return self.get_names('eb_names').shape[0] # type: ignore


    def get_elem_vars(self, names_blocks: list[tuple[str,int]] | None
                      ) -> dict[tuple[str,int],npt.NDArray] | None:
        """get_elem_vars _summary_

        Args:
            names (npt.NDArray | None): _description_
            blocks (list[int]): _description_

        Returns:
            dict[tuple[str,int],npt.NDArray] | None: _description_
        """
        if self.get_elem_var_names() is None or names_blocks is None:
            return None

        key_tag = 'vals_elem_var'

        vars = dict({})
        for ii,nn in enumerate(names_blocks):
            key = f'{key_tag}{ii+1:d}eb{nn[1]:d}'
            vars[nn] = self.get_var(key)

        return vars


    def get_all_elem_vars(self) -> dict[tuple[str,int], npt.NDArray] | None:
        """get_all_elem_vars _summary_

        Returns:
            dict[tuple[str,int], npt.NDArray] | None: _description_
        """

        return self.get_elem_vars(self.get_elem_var_names_and_blocks())


    def get_glob_var_names(self) -> npt.NDArray | None:
        """get_glob_var_names _summary_

        Returns:
            npt.NDArray | None: _description_
        """
        return self.get_names('name_glo_var')


    def get_glob_vars(self, names: npt.NDArray | None) -> dict[str, npt.NDArray] | None:
        """get_glob_vars _summary_

        Args:
            names (npt.NDArray | None): _description_

        Returns:
            dict[str, npt.NDArray] | None: _description_
        """
        if self.get_glob_var_names() is None or names is None:
            return None

        key = 'vals_glo_var'
        glob_vars = dict({})
        for ii,nn in enumerate(names): # type: ignore
            glob_vars[nn] = np.array(self._data.variables[key][:,ii])

        return glob_vars


    def get_all_glob_vars(self) -> dict[str, npt.NDArray] | None:
        """get_all_glob_vars _summary_

        Returns:
            dict[str, npt.NDArray]: _description_
        """

        return self.get_glob_vars(self.get_glob_var_names())


    def get_coords(self) -> npt.NDArray:
        """Gets the nodal coordinates in each spatial dimension setting any
        undefined dimensions to zeros.

        return np.array([])

        Raises:
            RuntimeError: no spatial dimensions found.

        Returns:
            np.array: returns the nodal coordinates as an array with shape
                (N,3) where N is the number of nodes and the three columns
                are the (x,y,z) spatial dimensions.
        """
        # If the problem is not 3D any of these could not exist
        x = self.get_var('coordx')
        y = self.get_var('coordy')
        z = self.get_var('coordz')

        # Problem has to be at least 1D in space if not raise an error
        num_coords = np.max(np.array([x.shape[0],y.shape[0],z.shape[0]]))
        if num_coords == 0:
            raise RuntimeError("No spatial coordinate dimensions detected, problem must be at least 1D.")

        # Any dimensions that do not exist are assumed to be zeros
        x = self._expand_coord(x,num_coords)
        y = self._expand_coord(y,num_coords)
        z = self._expand_coord(z,num_coords)

        self.coords = np.vstack((x,y,z)).T

        return self.coords


    def _expand_coord(self,coord: npt.NDArray, dim: int) -> npt.NDArray:
        """Helper function to create an array of zeros to pad any spatial
        dimensions that are not defined for the simulation.

        Args:
            coord (np.array): the coordinate array.
            dim (int): the size of the vector of zeros to creat if coord is
                empty.

        Returns:
            np.array: returns a vector of zeros with shape (dim,) if the
                input array is empty, otherwise return the input coord array.
        """
        if coord.shape[0] == 0:
            return np.zeros([dim,])

        return coord


    def get_time(self) -> npt.NDArray:
        """Get a vector of simulation time steps.

        Returns:
            np.array: returns an array with shape (T,) where T is the number
                of time steps and the values of the elements are the simulation
                time and each time step.
        """
        if 'time_whole' in self._data.variables:
            return np.array(self._data.variables['time_whole'])

        return np.array([])


    def print_vars(self) -> None:
        """Prints all variable strings in the exodus file to console.
        """
        for vv in self._data.variables:
            print(vv)

    def get_read_config(self) -> SimReadConfig:
        """get_read_config _summary_

        Returns:
            SimReadConfig: _description_
        """
        read_config = SimReadConfig()

        read_config.sidesets = self.get_sideset_names()
        read_config.node_vars = self.get_node_var_names()
        read_config.elem_vars = self.get_elem_var_names_and_blocks()
        read_config.glob_vars = self.get_glob_var_names()

        return read_config


    def read_sim_data(self,
                      read_config: SimReadConfig) -> SimData:
        """read_sim_data _summary_

        Args:
            read_config (SimReadConfig): _description_

        Returns:
            SimData: _description_
        """
        data = SimData()

        data.time = self.get_time()
        data.coords = self.get_coords()
        data.connect = self.get_connectivity()

        data.side_sets = self.get_sidesets(read_config.sidesets)
        data.node_vars = self.get_node_vars(read_config.node_vars)
        data.elem_vars = self.get_elem_vars(read_config.elem_vars)
        data.glob_vars = self.get_glob_vars(read_config.glob_vars)

        return data


    def read_all_sim_data(self) -> SimData:
        """read_all_sim_data _summary_

        Returns:
            SimData: _description_
        """
        data = SimData()

        data.time = self.get_time()
        data.coords = self.get_coords()
        data.connect = self.get_connectivity()
        data.side_sets = self.get_all_sidesets()
        data.node_vars = self.get_all_node_vars()
        data.elem_vars = self.get_all_elem_vars()
        data.glob_vars = self.get_all_glob_vars()

        return data

