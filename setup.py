from ast import literal_eval
from pathlib import Path

from setuptools import setup

VERSIONFILE = Path(__file__).parent / "src" / "__version.py"
with open(VERSIONFILE, "rt") as f:
    version = literal_eval(f.readline().split("= ")[1])

# remainder of setup in setup.cfg
setup(version=version,
      package_dir={'minipdb': 'src'},
      pacakges = ['minipdb'],
      scripts=['bin/minipdb'])
