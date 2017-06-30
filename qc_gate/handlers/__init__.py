
from os.path import dirname, basename, isfile
import glob

# Make sure all modules from this directory can be loaded
# by from qc_gate.handers import *

modules = glob.glob(dirname(__file__)+"/*.py")
names_of_modules = []
for f in modules:
    file_name = basename(f)
    if isfile(f) and not (file_name == "__init__.py"):
        names_of_modules.append(basename(f).replace(".py", ""))

print(names_of_modules)
#__all__ = names_of_modules
