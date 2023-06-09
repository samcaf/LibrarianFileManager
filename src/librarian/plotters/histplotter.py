"""This module contains the HistPlotter class,
which is a subclass of the Plotter class designed
to produce histograms from data.
"""

import matplotlib.pyplot as plt

from librarian.actors.plotter import Plotter


class HistPlotter(Plotter):
    """Plotter class for plotting histograms."""
    def __init__(self, **kwargs):
        """Initializes the HistPlotter."""
        kwargs['title'] = kwargs.get('title', 'Histogram')
        super().__init__(**kwargs)

        # Updating the histogram specific style
        self.style = {
            'histtype': kwargs.get('histtype', 'step'),
            'density': kwargs.get('density', False),
            'lw': self.mpl_rc['lines.linewidth'],
        }

        # Define default bins
        self.bins = kwargs.get('bins', 25)

    def plot_data(self, data, **kwargs):
        """Plots data as a histogram."""
        bins = kwargs.pop('bins', self.bins)

        style = self.style.copy()
        style.update(kwargs)

        plt.hist(data, bins, **style)
