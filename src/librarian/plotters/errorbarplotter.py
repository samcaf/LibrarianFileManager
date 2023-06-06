import matplotlib.pyplot as plt

from librarian.actors.plotter import Plotter


class ErrorBarPlotter(Plotter):
    """Plotter class for plotting with errorbars."""
    def __init__(self, **kwargs):
        """Initializes the Plotter."""
        super().__init__(**kwargs)

        self.style = {}

        # Define default bins
        self.bins = kwargs.get('bins', 25)


    def plot_data(self, data, **kwargs):
        """Plots data as a histogram."""
        bins = kwargs.pop('bins', self.bins)

        style = self.style.copy()
        style.update(kwargs)

        # TODO:
        # Get plottable values associated with the data and bins
