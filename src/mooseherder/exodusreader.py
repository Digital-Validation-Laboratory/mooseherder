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

Authors: Lloyd Fletcher
===============================================================================
"""

import netCDF4 as nc
import numpy as np

class ExodusReader:
    """Class to read exodus files output by MOOSE using netCDF package.
    """    
    def __init__(self,exodus_file: str):
        """Construct class by reading the exodus file using the netCDF package. 
        Also reads the node and element variable names as well as the nodal 
        variables. 

        Args:
            exodus_file (str): exodus file and path to read.
        """        
        self._data = nc.Dataset(exodus_file)
    
        self._node_var_names = self._get_names('name_nod_var')
        self._elem_var_names = self._get_names('name_elem_var')

        self._node_data = dict()
        for ii,nn in enumerate(self._node_var_names):
            key = 'vals_nod_var{:d}'.format(ii+1)
            self._node_data[nn] = np.array(self._data.variables[key]).T

    def __del__(self):
        """Safely close the exodus file.
        """        
        self._data.close()

    def _get_names(self,key: str) -> np.array:
        """Helper function for extracting the nodal/element variable names that
            are used as keys to get the associated data. For example: 'disp_x'
            and 'disp_y' for a 2D tensor mechanics problem.

        Args:
            key (str): identifier for the variable containing the variable 
                names.

        Returns:
            np.array: numpy array of strings with the variable names returns
                an empty numpy array if the key does not exist.
        """        
        if key in self._data.variables:
            return nc.chartostring(np.array(self._data.variables[key]))
        else: 
            return np.array([])
        
    def get_all_var_names(self):
        return list(self._data.variables)
    
    def get_node_var_names(self):
        return list(self._node_var_names)
    
    def get_elem_var_names(self):
        return list(self._elem_var_names)
        
    def get_var(self,key: str) -> np.array:
        """Gets a variable from the exodus file. If the variable does not exist
        returns an empty numpy array.

        Args:
            key (str): identifier for the variable

        Returns:
            np.array: value(s) of the variable as an array
        """
        if key in self._data.variables:
            return np.array(self._data.variables[key])
        else:
            return np.array([])

    def get_node_data(self,key: str) -> np.array:
        """Gets the simulation data at nodes for the variable requested with
        'key'. 

        Args:
            key (str): string identifier for the nodal variable. For example 
                'disp_x' for a tensor mechanics problem. Note that MOOSE might
                interpolate element variable to nodes for tensor mechanics 
                with material_output_order != CONSTANT. 

        Returns:
            np.array: returns an array with shape (T,N) where T is the number 
                of time steps and N is the number of nodes in the simulation.
        """      
        return self._node_data[key]
    
    def get_elem_data(self,key: str, block: int) -> np.array:
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
        name = 'vals_elem_var{:d}eb{:d}'.format(ind+1,block)

        if name in self._data.variables:
            return np.array(self._data.variables[name]).T
        else:
            return np.array([])
            
    def get_coords(self) -> np.array:
        """Gets the nodal coordinates in each spatial dimension setting any
        undefined dimensions to zeros.

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
    
    def _expand_coord(self,coord: np.array, dim: int) -> np.array:
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
        else:
            return coord
    
    def get_time(self) -> np.array:
        """Get a vector of simulation time steps.

        Returns:
            np.array: returns an array with shape (T,) where T is the number 
                of time steps and the values of the elements are the simulation
                time and each time step.
        """        
        if 'time_whole' in self._data.variables:
            return np.array(self._data.variables['time_whole'])
        else:
            return np.array([])
        
    def print_vars(self) -> None:
        """Prints all variable strings in the exodus file to console.
        """        
        for vv in self._data.variables:
            print(vv)
