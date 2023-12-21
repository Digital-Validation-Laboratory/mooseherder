"""
===============================================================================
EXODUS READER
Used to read output *.e from MOOSE simulations.

There are several different cases that lead to different MOOSE output formats.

1) Outputs can have 2 or 3 spatial dimensions for nodal DOFs
    (e.g. disp_x, disp_y and possibly disp_z)
2) Element output may or may not be present (e.g. stress/strain)
    2.1) Element outputs might appear as nodal variables if
         material_output_order = SECOND
4) Sub-domains may or may not be present but see 2.1 above for exception

Authors: Lloyd Fletcher
===============================================================================
"""

import time
import netCDF4 as nc
import numpy as np
from pprint import pprint

class ExodusReader:
    def __init__(self,exodus_file: str):
        """_summary_

        Args:
            exodus_file (str): _description_
        """        
        self._data = nc.Dataset(exodus_file)
    
        self.node_var_names = self._get_names('name_nod_var')
        self.elem_var_names = self._get_names('name_elem_var')

        self.node_data = dict()
        for ii,nn in enumerate(self.node_var_names):
            key = 'vals_nod_var{:d}'.format(ii+1)
            self.node_data[nn] = np.array(self._data.variables[key])

        if self.elem_var_names.shape[0] != 0:
            pass

    def __del__(self):
        self._data.close()

    def _get_names(self,key: str) -> np.array:
        """_summary_

        Args:
            key (str): _description_

        Returns:
            np.array: _description_
        """        
        if key in self._data.variables:
            return nc.chartostring(np.array(self._data.variables[key]))
        else: 
            return np.array([])
        
    def get_var(self,key: str) -> np.array:
        return np.array(self._data.variables[key])
        
    def get_node_data(self,key: str) -> np.array:
        """_summary_

        Args:
            key (str): _description_

        Returns:
            np.array: _description_
        """      
        return self.node_data[key]
    
    def get_elem_data(self,key: str,block: int,) -> np.array:
        """_summary_

        Args:
            key (str): _description_
            block (int): _description_

        Returns:
            np.array: _description_
        """
        if self.elem_var_names.shape[0] == 0:
            return np.array([])
                
        ind = np.where(self.elem_var_names == key)[0][0]
        name = 'vals_elem_var{:d}eb{:d}'.format(ind+1,block)
        return np.array(self._data.variables[name])
            
    def get_coords(self) -> np.array:
        """_summary_

        Raises:
            RuntimeError: _description_

        Returns:
            np.array: _description_
        """        
        # If the problem is not 3D any of these could not exist
        x = self._check_coord('coordx')
        y = self._check_coord('coordy')
        z = self._check_coord('coordz')

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
        
    def _check_coord(self,key: str) -> np.array:
        """_summary_

        Args:
            key (str): _description_

        Returns:
            np.array: _description_
        """        
        if key in self._data.variables:
            coord = np.array(self._data.variables[key])
        else:
            coord = np.array([])

        return coord
    
    def _expand_coord(self,coord: np.array, dim: int) -> np.array:
        """_summary_

        Args:
            coord (np.array): _description_
            dim (int): _description_

        Returns:
            np.array: _description_
        """        
        if coord.shape[0] == 0:
            return np.zeros([dim,])
        else:
            return coord
    
    def get_time(self) -> np.array:
        if 'time_whole' in self._data.variables:
            return np.array(self._data.variables['time_whole'])
        else:
            return np.array([])
        
    def print_vars(self) -> None:
        for vv in self._data.variables:
            pprint(vv)
