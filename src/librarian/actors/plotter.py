import matplotlib as mpl
from cycler import cycler

from librarian.actors.reader import Reader


# =====================================
# Abstract Classes
# =====================================

class Plotter(Reader):
    """Plotter class for plotting data contained in Librarian
    files/catalogs.
    """
    def __init__(self, **kwargs):
        # Get plot metadata from kwargs:
        self.metadata = {
            'title': kwargs.get('title', 'Histogram'),
            'xlabel': kwargs.get('xlabel', 'x'),
            'ylabel': kwargs.get('ylabel', 'y'),
            'xlim': kwargs.get('xlim', None),
            'ylim': kwargs.get('ylim', None),
        }

        # Get plot style info
        self.style = {
            'lw': kwargs.get('lw', 2),
            'fontsize': kwargs.get('fontsize', 14),
        }

        # Get cycle info
        self.cycle_colors = cycler(
            color=kwargs.get(
                'catalog_cycle_colors',
                ['darkgreen', 'royalblue', 'darkgoldenrod', 'darkred']
            )
        )

        # Setting up a local rc
        self.mpl_rc = {'lines.linewidth': self.style['lw'],
                       'labels.fontsize': self.style['fontsize']
                       }
        if self.cycle_colors is not None:
            self.mpl_rc['axes.prop_cycle'] = self.cycle_colors


    def plot_data(self, data, **kwargs):
        """Plots data."""
        raise NotImplementedError("Plotter.plot_data() not implemented.")


    def file_action(self, file_path, **kwargs):
        """Defining the file action of the Reader to
        load data from files."""
        data = self.load_data(file_path)
        self.plot_data(data, **kwargs)


    def act_on_catalog(self, catalog, **kwargs):
        """Perform the defined action on all files within the catalog."""
        file_paths = catalog.get_files()

        with mpl.rc_context(self.mpl_rc):
            for file_path in file_paths:
                self.file_action(file_path, **kwargs)


class MultiPlotter(Plotter):
    """Plotter class for plotting data across an entire catalog."""
    def plot_datasets(self, datasets, **kwargs):
        """Plots data contained in catalogs."""
        raise NotImplementedError("MultiPlotter.plot_datasets() not implemented.")


    def file_action(self, file_path, **kwargs):
        """MultiPlotter is not designed to act on a single file."""
        raise NotImplementedError("MultiPlotter is not designed to"
                                  " act on a single file.")

    def act_on_catalog(self, catalog, **kwargs):
        """MultiPlotter is designed to act on a catalog."""
        self.plot_datasets(catalog.datasets, **kwargs)
