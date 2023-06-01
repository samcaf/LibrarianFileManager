import matplotlib.pyplot as plt

from librarian.actors.plotter import Plotter


class HistPlotter(Plotter):
    """Plotter class for plotting histograms."""
    def __init__(self, **kwargs):
        """Initializes the HistPlotter."""
        super().__init__(**kwargs)

        # Updating the histogram specific style
        self.style.update({
            'histtype': kwargs.get('histtype', 'step'),
            'density': kwargs.get('density', False),
        })

        # Define default bins
        self.bins = kwargs.get('bins', 25)

    def plot_data(self, data, **kwargs):
        """Plots data as a histogram."""
        bins = kwargs.pop('bins', self.bins)

        style = self.style.copy()
        style.update(kwargs)

        plt.hist(data, bins, **style)


class ErrorBarPlotter(Plotter):
    """Plotter class for plotting with errorbars."""
    def __init__(self, **kwargs):
        """Initializes the Plotter."""
        super().__init__(**kwargs)

        # Updating the histogram specific style
        self.style.update({
            'histtype': kwargs.get('histtype', 'step'),
            'density': kwargs.get('density', False),
        })

        # Define default bins
        self.bins = kwargs.get('bins', 25)


    def plot_data(self, data, **kwargs):
        """Plots data as a histogram."""
        bins = kwargs.pop('bins', self.bins)

        style = self.style.copy()
        style.update(kwargs)

        # TODO:
        # Get plottable values associated with the data and bins
