# MOOSEHerder
A `mooseherder` for calling multiple MOOSE simulations in parallel from python with configurable parallelisation options. Includes functionality to read and edit MOOSE/gmsh input scripts as well as reading the associated output of the simulation in parallel.

The main use cases for `mooseherder` include running parametric sweeps of small to medium size simulations for mesh convergence analysis; fitting surrogate/reduced order models; and optimisation problems.

## Installation
### Virtual Environment

We recommend installing `mooseherder` in a virtual environment using `venv` or `mooseherder` can be installed into an existing environment of your choice. To create a specific virtual environment for `mooseherder` use:

```
python3 -m venv herder-env
source herder-env/bin/activate
```

### Standard Installation from PyPI

You can install from PyPI:

```
pip install mooseherder
```

### Developer Installation

Clone `mooseherder` to your local system and `cd` to the root directory of `mooseherder`. Ensure you virtual environment is activated and run from the `mooseherder` root directory:

```
pip install -e .
```

### MOOSE App

`mooseherder` has been developed and tested using the `proteus` MOOSE app which can be found here: https://github.com/aurora-multiphysics/proteus. Follow the build instructions found on this page to install `proteus`.

## Getting Started

The examples folder includes a sequence of examples using `mooseherder` to run the MOOSE tensor mechanics module with and without coupling to gmsh.

## Contributors

- Lloyd Fletcher, UK Atomic Energy Authority, (TheScepticalRabbit)
- Rory Spencer, UK Atomic Energy Authority, (fusmatrs)
- Luke Humphrey, UK Atomic Energy Authority, (lukethehuman)