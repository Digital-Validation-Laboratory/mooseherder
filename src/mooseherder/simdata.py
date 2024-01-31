"""
===============================================================================
SimData Class

Authors: Lloyd Fletcher,
===============================================================================
"""
from dataclasses import dataclass
import numpy.typing as npt

@dataclass
class SimData:
    """ Data class for finite element simulation output.
    """

    time: npt.NDArray | None = None
    ''' Vector of time steps with dimensions [t].
        Defaults to None.
    '''

    coords: npt.NDArray | None = None
    ''' Array of nodal coordinates in N by 3 where N is the number of nodes
        columns are [x,y,z] coordinates and rows are the nth node.
        Defaults to None.
    '''

    connect: dict[str,npt.NDArray] | None = None
    ''' Element connectivity table:
        key = 'connectX' where X is the subdomain e.g. connect1
        Element table given as E by n_e rows where E is the number of elements
        in the given subdomain. n_e is the number of nodes per element.
        Defaults to None.
    '''

    side_sets: dict[tuple[str,str],npt.NDArray] | None = None
    ''' Sidesets by name and associated node and element numbers.
        key = (name, 'node' or 'elem') e.g. ('bottom','node') will return node
        numbers associated with associated with sideset called 'bottom' as a
        numpy array with n_s entries where n_s is the number of nodes in the
        sideset.
        Defaults to None.
    '''

    node_vars: dict[str,npt.NDArray] | None = None
    ''' Nodal variable by name.
        key = 'name' e.g. 'disp_x' or 'temp'
        Gives the nodal variable as a numpy array N by t where N is the number
        of nodes and t is the number of time steps. Note that element variables
        can be stored as nodal depending on output options or material output
        order selected.
        Defaults to None.
    '''

    elem_vars: dict[tuple[str,int],npt.NDArray] | None = None
    ''' Element variables by name and block.
        key = (name, block num)
        Defaults to None.
    '''

    glob_vars: dict[str,npt.NDArray] | None = None
    ''' Global variables by name. Global variable include postprocessors and
        extracted reactions at boundaries.
        key = name (as specified in input file), e.g. 'react_y'
        Gives a numpy array with t entries corresponding to the number of time
        steps in the simulation.
        Defaults to None.
    '''

