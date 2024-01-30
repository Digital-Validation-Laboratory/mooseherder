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
from dataclasses import dataclass
from pathlib import Path
import netCDF4 as nc
import numpy as np
import numpy.typing as npt


@dataclass
class SimData:
    """ _summary_
    """
    time: npt.NDArray | None = None
    coords: npt.NDArray | None = None
    connect: dict[str,npt.NDArray] | None = None
    side_sets: dict[str,npt.NDArray] | None = None
    node_vars: dict[str,npt.NDArray] | None = None
    elem_vars: dict[tuple[str,int],npt.NDArray] | None = None
    glob_vars: dict[str,npt.NDArray] | None = None


class ExodusReader:
    """Class to read exodus files output by MOOSE using the netCDF package.
    """
    def __init__(self, exodus_file: Path):
        """Construct class by reading the exodus file using the netCDF package.
        Also reads the node and element variable names as well as the nodal
        variables.

        Args:
            exodus_file (Path): path to exodus file to be read.
        """
        if not exodus_file.is_file() and exodus_file.suffix != '.e':
            raise FileNotFoundError('Exodus file not found at specified path')

        self._exodus_path = exodus_file
        self._data = nc.Dataset(str(self._exodus_path)) # type: ignore


    def get_names(self, key: str | None) -> npt.NDArray | None:

        if key not in self._data.variables or key is None:
            return None

        return nc.chartostring(np.array(self._data.variables[key]))


    def get_var(self, key: str) -> npt.NDArray:

        if key not in self._data.variables:
            return np.array([])

        return np.array(self._data.variables[key]).T


    def get_connectivity_names(self) -> npt.NDArray:

        names = np.array([])
        for bb in range(self.get_num_elem_blocks()):
            key = f'connect{bb+1:d}'
            if key in self._data.variables:
                names = np.append(names,key)

        return names


    def get_connectivity(self) -> dict[str,npt.NDArray]:

        vars = dict({})
        for key in self.get_connectivity_names():
            vars[key] = self.get_var(key)

        return vars


    def get_sideset_names(self) -> npt.NDArray | None:

        return self.get_names('ss_names')


    def get_all_sidesets(self) -> dict[str, npt.NDArray] | None:

        key_tag = 'node_ns'

        vars = dict({})
        for ii,nn in enumerate(self.get_sideset_names()): # type: ignore
            key = key_tag+'{:d}'.format(ii+1)
            vars[nn] = self.get_var(key)

        return vars


    def get_node_var_names(self) -> npt.NDArray | None:

        return self.get_names('name_nod_var')


    def get_node_vars(self, names: npt.NDArray | None) -> dict[str,npt.NDArray] | None:

        if names is None:
            return None

        key_tag = 'vals_nod_var'
        vars = dict({})

        for ii,nn in enumerate(names): # type: ignore
            key = f'{key_tag}{ii+1:d}'
            vars[nn] = self.get_var(key)

        return vars


    def get_all_node_vars(self) -> dict[str, npt.NDArray] | None:

        return self.get_node_vars(self.get_node_var_names())


    def get_elem_var_names(self) -> npt.NDArray | None:

        return self.get_names('name_elem_var')


    def get_num_elem_blocks(self) -> int:

        return self.get_names('eb_names').shape[0] # type: ignore


    def get_elem_vars(self, names: npt.NDArray | None,
                      blocks: list[int]) -> dict[tuple[str,int],npt.NDArray] | None:

        if self.get_elem_var_names() is None or names is None:
            return None

        key_tag = 'vals_elem_var'

        vars = dict({})
        for ii,nn in enumerate(names):
            for bb in blocks:
                key = f'{key_tag}{ii+1:d}eb{bb:d}'
                vars[(nn,bb)] = self.get_var(key)

        return vars


    def get_all_elem_vars(self) -> dict[tuple[str,int], npt.NDArray] | None:

        blocks = [ii+1 for ii in range(self.get_num_elem_blocks())]
        return self.get_elem_vars(self.get_elem_var_names(),blocks)


    def get_all_glob_vars(self) -> dict[str, npt.NDArray]:

        name_key = 'name_glo_var'
        key = 'vals_glo_var'

        vars = dict({})
        for ii,nn in enumerate(self.get_names(name_key)): # type: ignore
            vars[nn] = np.array(self._data.variables[key][:,ii])

        return vars


    '''
    def get_elem_data(self, key: str, block: int) -> npt.NDArray:
        """Gets the simulation data at elements for the variable requested with
        'key'. Note that for tensor mechanics with material_output_order !=
        CONSTANT the element data will be interpolated to nodes

        Args:
            key (str): string identifier key for the element variables
            block (int): integer for the subdomain of the associated elements.

        Returns:
            np.array: returns an array with shape (T,E) where T is the number
                of time steps and E is the number of elements in the specified
                block. Returns an empty array if there are no element variables
                or if the requested key/block does not exist.
        """
        if self._elem_var_names.shape[0] == 0:
            return np.array([])

        ind = np.where(self._elem_var_names == key)[0][0]
        name = f'vals_elem_var{ind+1:d}eb{block:d}'

        if name in self._data.variables:
            return np.array(self._data.variables[name]).T

        return np.array([])
    '''

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


    def read_sim_data(self) -> SimData:

        data = SimData()

        data.time = self.get_time()
        data.coords = self.get_coords()
        data.connect = self.get_connectivity()
        data.side_sets = self.get_all_sidesets()
        data.node_vars = self.get_all_node_vars()
        data.elem_vars = self.get_all_elem_vars()
        data.glob_vars = self.get_all_glob_vars()

        return data
