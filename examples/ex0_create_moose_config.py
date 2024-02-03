"""
==============================================================================
EXAMPLE 0: Create moose-config.json

Author: Lloyd Fletcher
==============================================================================
"""
from pathlib import Path
from mooseherder.mooseconfig import MooseConfig

USER_DIR = Path.home()


def main() -> None:
    """main: create moose config json
    """
    config = {'main_path': USER_DIR / 'moose',
            'app_path': USER_DIR / 'moose-workdir/proteus',
            'app_name': 'proteus-opt'}

    moose_config = MooseConfig(config)

    save_path = Path.cwd() / 'moose-config.json'
    moose_config.save_config(save_path)


if __name__ == "__main__":
    main()

