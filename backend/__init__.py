""" This code imports everything from /classes and /utils to use for stuff like `backend.utils.text_manipulation """

import pkgutil
import os
import importlib

# Get the directory that this __init__.py file is in
current_dir = os.path.dirname(os.path.realpath(__file__))

# Iterate over all Python files in this directory (excluding this __init__.py file)
for (_, module_name, _) in pkgutil.iter_modules([current_dir]):
    # Avoid reloading this __init__.py file
    if module_name == "__init__":
        continue
    # Dynamically import the module
    importlib.import_module("." + module_name, package=__name__)