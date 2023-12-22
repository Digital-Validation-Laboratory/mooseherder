"""
===============================================================================
Generic Input Modifier Class

Authors: Lloyd Fletcher, Rory Spencer
===============================================================================
"""

class InputModifier:
    """
    Class to modify variables in generic text-based input files.

    Once variables have been modified by the user by passing in a dictionary of 
    new variables the MOOSE input can be written to file.

    Variable definition blocks should begin #comment character#* and end 
    #comment character#**, e.g. //_* and //** for gmsh
    """
    def __init__(self, input_file: str, comment_char='#', end_char=''):
        """ Initialise the class by reading in the input file. Find and read 
        any variables that are at the top of the file. Default comment_char
        and end_char are set based on reading MOOSE *.i files.

        Args:
            input_file (string): Path to the input text file.
            comment_char (string): character(s) describing what a comment look
                like in the file. 
            end_char (string): character (if any) that ends a line, i.e. ; 
        """
        self._vars = dict()
        self._input_file = input_file

        with open(self._input_file,'r') as in_file:
            self._input_lines = in_file.readlines()

        self._comment_char = comment_char
        self._end_char = end_char
        self.find_vars()
        self.read_vars()
        
    def read_vars(self) -> None:
        """ Reads the variables in the file 
        """
        for ii,ss in enumerate(self._input_lines[self._var_start+1:self._var_end]):
            ss = ss.strip()
            ss = ss.replace(' ','') 
            ss = ss.replace(self._end_char,'') 
            ss = ss.split(self._comment_char)[0]  # Remove trailing comments should they exist
            if ss:
                # Anything left with an equals sign is a variable
                if ss.find('=') >= 0:
                    self._vars[ss.split('=', 1)[0]] = float(ss.split('=', 1)[1])


    def find_vars(self) -> None:
        """ Find what lines the variables are defined on.
        """
        self._var_start = 0
        self._var_end = -1
        start_string = self._comment_char+'_*'
        end_string = self._comment_char+'**'
    
        for index,line in enumerate(self._input_lines):
            if start_string in line:
                self._var_start = index
            if end_string in line:
                self._var_end = index
                break

    def update_vars(self,new_vars: dict) -> None:
        """Updates the dict of varaibles

        Args:
            new_vars (dict): New values for the variables. Must have the same 
                keys as variables found in the input file.

        Raises:
            KeyError: Keys don't match between existing and updated dicts.
        """
        if self._vars.keys() == new_vars.keys():
            self._vars = new_vars
        else:
            raise KeyError('Dictionary keys of input variables for not match those founde in the input file.')


    def write_file(self,wfile: str) -> None:
        """Write the input file.

        Args:
            wfile (str): Path to where the file should be written.
        """
        
        # Prep the values to write
        keys = list(self._vars.keys())
        values = list(self._vars.values())

        #Write file
        with open(wfile,'w') as out_file:
            for index,line in enumerate(self._input_lines):
                #If it's in the variables block, overwrite
                if index > self._var_start and index < self._var_end:
                    current_var = index-self._var_start-1
                    try:
                        write_string = '{} = {}{}\n'.format(keys[current_var],values[current_var],self._end_char)
                        out_file.write(write_string)
                    except(IndexError):
                        # TODO: Probably should avoid printing to console inside a class
                        #print('All available parameters written. Check for commented out parameters in the input.')
                        pass
                    continue
                else:
                    out_file.write(line)

    def get_vars(self) -> dict:
        """Gets the variables found in the file.

        Returns:
            dict: keys are variable strings and values are variable values.
        """        
        return self._vars
    
    def get_var_keys(self) -> list(str()):
        """Gets a list of variable names found in the input file.

        Returns:
            list(str()): list of variables name as strings
        """        
        return list(self._vars.keys())
    
    def get_input_file(self) -> str:
        """Gets the path and input file name.

        Returns:
            str: path and input file name.
        """        
        return self._input_file

        

