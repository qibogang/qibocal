from .cli import command, compare, live_plot, upload

"""qibocal: Quantum Calibration Verification and Validation using Qibo."""
import importlib.metadata as im

__version__ = im.version(__package__)
