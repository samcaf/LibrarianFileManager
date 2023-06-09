"""This module contains the Plotter class, which is a base
class with methods for creating figures and for plotting data
from single or multiple files within a catalog, or between catalogs.
"""

import warnings
from datetime import date

import matplotlib as mpl
import matplotlib.pyplot as plt
from cycler import cycler

from librarian.actors.reader import Reader


# =====================================
# Abstract Classes
# =====================================

class Plotter(Reader):
    """Plotter class for plotting data contained in Librarian
    files/catalogs.
    """
    # ---------------------------------------------------
    # Formatting:
    # ---------------------------------------------------
    # Font sizes
    _small_size = 10
    _medium_size = 12
    _bigger_size = 14
    _large_size = 16

    # Plot styles: lines, markers, etc.
    _linewidth = 2
    _linestyle = '-'  # solid lines
    # (modstyle)
    # _linestyle = None
    _markersize = 2
    _capsizes = 2
    _capthick = 1.5

    # Figure size
    _fig_width = 6.4
    _fig_height = 4.8
    _figsize = (_fig_width, _fig_height)


    def __init__(self, **kwargs):
        """Initializes the plotter, including the axis information
        and style of the plots.

        Possible Parameters
        ----------

        Figure Parameters
        ----------
        xlabel : str
            xlabel of the plot.
        ylabel : str
            ylabel of the plot.
        title : str
            title of the plot.
        showdate : bool
            If True, adds a date to the upper right of the plot.
        xlim : tuple
            The x limits of the plot.
        ylim : tuple
            The y limits of the plot.
        ylim_ratio : tuple
            The y limits of the ratio subplot.
        ratio_plot : bool
            Determines whether there is an additional subplot
            for ratio plotting.
        ylabel_ratio : str
            ylabel of the ratio subplot, if it exists.

        Style Parameters
        ----------
        font.size : int
            default text sizes
        figure.titlesize : int
            fontsize of the figure title
        axes.titlesize : int
            fontsize of the axes title
        axes.labelsize : int
            fontsize of the x and y labels
        xtick.labelsize : int
            fontsize of the x tick labels
        ytick.labelsize : int
            fontsize of the y tick labels
        legend.fontsize : int
            fontsize of the legend
        lines.linewidth : int
            default plot linewidth
        axes.prop_cycle : cycler
            default color cycle

        Returns
        -------
        None
        """
        # Get plot metadata from kwargs:
        self.metadata = {
            'figsize': kwargs.get('figsize', self._figsize),
            'title': kwargs.get('title', 'Plotter'),
            'xlabel': kwargs.get('xlabel', 'x'),
            'ylabel': kwargs.get('ylabel', 'y'),
            'ylabel_ratio': kwargs.get('ylabel_ratio', 'Ratio'),
            'xlim': kwargs.get('xlim', None),
            'ylim': kwargs.get('ylim', None),
            'ylim_ratio': kwargs.get('ylim_ratio', None),
        }

        # Get plot style info for plotting with a local rc_context
        self.mpl_rc = {
            'font.size': kwargs.get('font.size', self._medium_size),
            'figure.titlesize': kwargs.get('axes.titlesize',
                                           self._large_size),
            'axes.titlesize': kwargs.get('axes.titlesize',
                                         self._bigger_size),
            'axes.labelsize': kwargs.get('axes.labelsize',
                                         self._medium_size),
            'xtick.labelsize': kwargs.get('xtick.labelsize',
                                          self._small_size),
            'ytick.labelsize': kwargs.get('ytick.labelsize',
                                          self._small_size),
            'legend.fontsize': kwargs.get('legend.fontsize',
                                          self._medium_size),
            'lines.linewidth': kwargs.get('lines.linewidth',
                                          self._linewidth),
            'axes.prop_cycle': kwargs.get('axes.prop_cycle',
                                          cycler(
                                            'color',
                                            ['darkgreen', 'royalblue',
                                             'darkgoldenrod', 'darkred'])
                                          ),
        }


    def subplots(self, ratio_plot=False,
                 showdate=False, labeltext=None,
                 **kwargs):
        """Creates a figure and associated axes using default or
        given parameters during initialization.

        Can be used to produce a figure with a ratio subplot.

        New Parameters
        ----------
        ratio_plot : bool
            Determines whether there is an additional subplot
            for ratio plotting.
        showdate : bool
            If True, adds a date to the upper right of the plot.
        labeltext : str
            Text to be added to the plot as an additional label.

        Returns
        -------
        Figure, axes.Axes
            The figure and axes/subplots specified by the
            above parameters.
        """
        # Get plt subplots
        gridspec_kw = {'height_ratios': (3.5, 1) if ratio_plot else (1,),
                       'hspace': 0.0}
        nsubplots = 2 if ratio_plot else 1
        fig, axes = plt.subplots(nsubplots, gridspec_kw=gridspec_kw,
                     figsize=kwargs.get('figsize', self.metadata['figsize']))
        if nsubplots == 1:
            axes = [axes]

        # axes limits
        if kwargs.get('xlim', self.metadata['xlim']) is not None:
            axes[0].set_xlim(*kwargs.get('xlim', self.metadata['xlim']))
        if kwargs.get('ylim', self.metadata['ylim']) is not None:\
            axes[0].set_ylim(*kwargs.get('ylim', self.metadata['ylim']))
        if ratio_plot:
            if kwargs.get('ylim_ratio', self.metadata['ylim_ratio']) is not None:
                axes[1].set_ylim(*kwargs.get('ylim_ratio',
                                             self.metadata['ylim_ratio'])
                                 )
            axes[1].set_yscale('log')

        # axes labels
        axes[-1].set_xlabel(kwargs.get('xlabel', self.metadata['xlabel']))
        axes[0].set_ylabel(kwargs.get('ylabel', self.metadata['ylabel']), labelpad=5)
        if ratio_plot:
            axes[1].set_ylabel(kwargs.get('ylabel_ratio',
                                          self.metadata['ylabel_ratio']),
                               labelpad=-10)

        # tick settings
        for ax_instance in axes:
            ax_instance.minorticks_on()
            ax_instance.tick_params(top=True, right=True, bottom=True,
                           left=True, direction='in', which='both')

        if ratio_plot:
            axes[0].tick_params(labelbottom=False)
            axes[1].tick_params(axis='y')

        # Extra plot information
        pad = .01

        if showdate:
            # Including date
            axes[0].text(
                x=1,
                y=1.005+pad,
                s=date.today().strftime("%m/%d/%y"),
                transform=axes[0].transAxes,
                ha="right",
                va="bottom",
                fontsize=self._medium_size * 0.95,
                fontweight="normal"
            )

        if labeltext is not None:
            # Extra primary label
            axes[0].text(
                x=-0.1,
                y=1.005+pad,
                s=labeltext,
                transform=axes[0].transAxes,
                ha="left",
                va="bottom",
                fontsize=self._medium_size * 1.5,
                fontweight="bold",
                fontname="DIN Condensed"
            )

        if kwargs.get('title', self.metadata['title']) is not None:
            # Main title
            axes[0].text(
                x=.12,
                y=1.005+pad,
                s=kwargs.get('title', self.metadata['title']),
                transform=axes[0].transAxes,
                ha="left",
                va="bottom",
                fontsize=self._medium_size * 1.5,
                fontstyle="italic",
                fontname="Arial"
            )

        plt.tight_layout()

        return fig, axes


    def plot_data(self, data, **kwargs):
        """Plots data in a specified way."""
        raise NotImplementedError("Plotter.plot_data() not implemented.")



    def check_conditions(self, data_name, params):
        """Check if the file_path meets the conditions to be
        acted upon.
        """
        return True


    def file_action(self, file_path,
                    local_rc=True, conditions=None,
                    **kwargs):
        """Defining the file action of the Reader to
        load data from files and plot.
        """
        # Otherwise, load the data
        data = self.load_data(file_path)

        # If we use a single rc_context for this catalog
        # plot within that context
        if local_rc:
            with mpl.rc_context(self.mpl_rc):
                self.plot_data(data, **kwargs)
        # Otherwise, simply plot without an rc_context
        else:
            self.plot_data(data, **kwargs)


    def act_on_catalog(self, catalog,
                       local_rc=True, conditions=None,
                       fig_kwargs=None, **kwargs):
        """Perform the defined plotting action
        on all files within the catalog.
        """
        file_paths = catalog.get_files()
        data_params = catalog.get_data_params()

        # Using default conditions if none are given
        if conditions is None:
            def conditions(data_name, params):
                return self.check_conditions(data_name, params)

        if fig_kwargs is None:
            def fig_kwargs(data_name, params):
                return {}


        # If we use a single rc_context for this entire catalog
        if local_rc:
            with mpl.rc_context(self.mpl_rc):
                for file_path, (data_name, params) in zip(file_paths,
                                                          data_params):
                    if conditions(data_name, params):
                        tmp_kwargs = kwargs.copy()
                        tmp_kwargs.update(fig_kwargs(data_name, params))
                        self.file_action(file_path, local_rc=False,
                                         **tmp_kwargs)

        # Otherwise, each plot has its own rc_context
        else:
            for file_path, (data_name, params) in zip(file_paths,
                                                      data_params):
                if conditions(data_name, params):
                    tmp_kwargs = kwargs.copy()
                    tmp_kwargs.update(fig_kwargs(data_name, params))
                    self.file_action(file_path, local_rc=True,
                                     **tmp_kwargs)


    def act_on_catalogs(self, catalogs,
                        local_rc=True, conditions=None,
                        fig_kwargs=None, **kwargs):
        """Perform the defined plotting action
        on all files within a list of catalogs.
        """
        # Using default conditions if none are given
        if conditions is None:
            def conditions(data_name, params):
                return self.check_conditions(data_name, params)

        if fig_kwargs is None:
            def fig_kwargs(data_name, params):
                return {}

        # If we use a single rc_context for this entire set of catalogs
        if local_rc:
            with mpl.rc_context(self.mpl_rc):
                for catalog in catalogs:
                    self.act_on_catalog(catalog, local_rc=False,
                                        conditions=conditions,
                                        fig_kwargs=fig_kwargs,
                                        **kwargs)

        # Otherwise, each individual plot has its own rc_context
        else:
            for catalog in catalogs:
                self.act_on_catalog(catalog, local_rc=False,
                                    conditions=conditions,
                                    fig_kwargs=fig_kwargs,
                                    **kwargs)
