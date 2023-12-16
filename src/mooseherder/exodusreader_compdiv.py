import netCDF4 as nc
import numpy as np

class ExodusReader:
    """
    See netcdf schema defined in Appendix A here:
    https://www.osti.gov/servlets/purl/10102115
    """
    def __init__(self, filename):
        self._file = nc.Dataset(filename)

        if "name_nod_var" in self._file.variables:
            self.nodal_var_names = [name.data.view('S256').ravel()[0].decode()
                                    for name in self._file.variables["name_nod_var"]]
            self.nodal_data_map = {name: self._file.variables['vals_nod_var%d' % (i+1)]
                                   for i, name in enumerate(self.nodal_var_names)}

        if "name_elem_var" in self._file.variables:
            self.elem_var_names = [name.data.view('S256').ravel()[0].decode()
                                   for name in self._file.variables["name_elem_var"]]

        self.time_node = self._file.variables['time_whole']

    def __del__(self):
        self._file.close()

    def get_times(self):
        return self.time_node[:].data

    def get_nodal_variable(self, name):
        return self.nodal_data_map[name][:].data

    def get_elemental_variable(self, name, block):
        idx = self.elem_var_names.index(name)

        if isinstance(block, int):
            name = 'vals_elem_var%deb%d' % (idx + 1, block + 1)
            return self._file.variables[name][:].data
        else:
            raise RuntimeError("element block indexing by name not yet implemented, please use the integer index")

    def get_coords(self):
        x = self._file.variables['coordx'][:].data
        y = self._file.variables['coordy'][:].data
        z = self._file.variables['coordz'][:].data
        return np.vstack((x, y, z)).T