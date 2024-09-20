"""Top-level package for MPShips."""

__author__ = """Ruoxi Yang"""
__email__ = 'yangroxie@gmail.com'
__version__ = '0.1.0'

from pathlib import Path
from mpships.materials_graph.materials_graph import MaterialsGraphAIO
from mpships.ELATE_Crystal.elate_dash import ELATE
from mpships.redox_thermo_csp.redox_thermo_csp import RedoxThermoCSPAIO


MODULE_PATH = str(Path(__file__).parents[0])
