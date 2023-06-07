from typing import TypedDict

from librarian.catalog import Catalog
from librarian.actors.writer import Writer
from librarian.plotters.histplotter import HistPlotter

# =====================================
# Setup
# =====================================

# ---------------------------------
# Template for parameters
# ---------------------------------
class DataParameters(TypedDict):
    """Parameters characterizing our test data."""
    n_samples: int
    minimum: int
    maximum: int

class PlotParameters(TypedDict):
    """Parameters characterizing our test plots."""
    n_samples: list
    minimum: int
    maximum: int

# ---------------------------------
# Catalogs
# ---------------------------------
uniform_catalog = Catalog('uniform_data',
                          'catalogs/uniform_data',
                          load='required')
nonuniform_catalog = Catalog('nonuniform_data',
                             'catalogs/nonuniform_data',
                             load='required')
figure_catalog = Catalog('figures',
                         'catalogs/figures',
                         load='required',
                         verbose=-1)

# ---------------------------------
# Writers
# ---------------------------------
data_writer: Writer = Writer('.npy')

# ---------------------------------
# Plotter
# ---------------------------------
plotter: HistPlotter = HistPlotter()
