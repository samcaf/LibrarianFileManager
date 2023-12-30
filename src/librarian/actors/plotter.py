"""This module contains the Plotter class, which is a base
class with methods for creating figures and for plotting data
from single or multiple files within a catalog, or between catalogs.
"""
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

    def __init__(self, metadata_defaults=None,
                 **kwargs):
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
        self.fig = None
        self.axes = None

        # Setting up custom color cycler
        color_cycler = kwargs.get('color_cycle', 'default')
        if color_cycler == 'default':
            color_cycler = cycler('color',
                                  ['cornflowerblue', 'lightcoral',
                                   'mediumorchid', 'mediumseagreen',
                                   'sandybrown'])
        elif color_cycler == 'pastel':
            color_cycler = cycler('color',
                                  ['#a4b6dd', '#d09292', '#c094cc',
                                   '#a2d0c0', '#c37892'])

        if color_cycler is not None:
            plt.rcParams["axes.prop_cycle"] = color_cycler

        # Get plot metadata from kwargs:
        _metadata_defaults = {'figsize': self._figsize,
                              'title': 'Plotter',
                              'xlabel': 'x',
                              'ylabel': 'y',
                              'xlim': None,
                              'ylim': None,
                              'x_scale': 'linear',
                              'y_scale': 'linear',
                              'ratio_plot': False,
                              'ylim_ratio': None,
                              'ylabel_ratio': 'Ratio',
                              'showdate': False,
                              'showlegend': True,
                             }
        if metadata_defaults is not None:
            _metadata_defaults.update(metadata_defaults)
        self.metadata = {key: kwargs.get(key, _metadata_defaults[key])
                         for key, default_value in
                         _metadata_defaults.items()}

        # Get plot style info for plotting with a local rc_context
        self.mpl_rc = {
            # Setting up for LaTeX-like text
            'text.usetex': kwargs.get('usetex', True),
            'font.family': kwargs.get('font.family', 'serif'),
            'font.serif': kwargs.get('font.serif',
                                     'Computer Modern Roman'),
            'font.monospace': kwargs.get('font.monospace',
                                     'Computer Modern Typewriter'),
            'text.latex.preamble': kwargs.get('latex.preamble',
                                     r'\usepackage{amsmath}'),
            # Other figure metadata options
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
            'legend.frameon': kwargs.get('legend.frameon', False),
            'legend.fontsize': kwargs.get('legend.fontsize',
                                           15),
            # Line options
            'lines.linewidth': kwargs.get('lines.linewidth',
                                          self._linewidth),
            'axes.prop_cycle': kwargs.get('axes.prop_cycle',
                                          cycler(
                                            'color',
                                            ['darkgreen', 'royalblue',
                                             'darkgoldenrod', 'darkred'])
                                          ),
        }

    def subplots(self, labeltext=None,
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
        # Setting up plot options
        full_kwargs = self.metadata.copy()
        full_kwargs.update(kwargs)
        kwargs = full_kwargs
        del full_kwargs

        ratio_plot = kwargs['ratio_plot']
        showdate = kwargs['showdate']

        # Get plt subplots
        gridspec_kw = {'height_ratios': (3.5, 1) if ratio_plot else (1,),
                       'hspace': 0.0}
        nsubplots = 2 if ratio_plot else 1
        fig, axes = plt.subplots(nsubplots, gridspec_kw=gridspec_kw,
                                 figsize=kwargs.get('figsize',
                                                    self.metadata['figsize']))
        if nsubplots == 1:
            axes = [axes]


        # - - - - - - - - - - - - - - - -
        # Axes Formatting
        # - - - - - - - - - - - - - - - -
        # Axes limits
        # xlim
        xlim = kwargs.get('xlim', self.metadata['xlim'])
        if hasattr(xlim, '__iter__') and \
                not isinstance(xlim, str):
            xlim = [None if isinstance(lim, str) else lim
                    for lim in xlim]
            if xlim == [None, None]:
                xlim = [None]
        else:
            xlim = [xlim]

        if xlim != [None]:
            _ = [ax.set_xlim(*xlim) for ax in axes]

        # ylim (axes[0])
        ylim = kwargs.get('ylim', self.metadata['ylim'])
        if hasattr(ylim, '__iter__') and \
                not isinstance(ylim, str):
            ylim = [None if isinstance(lim, str) else lim
                    for lim in ylim]
            if ylim == [None, None]:
                ylim = [None]
        else:
            ylim = [ylim]

        if ylim is not None:
            axes[0].set_ylim(*ylim)

        # ylim_ratio (axes[1], if it exists)
        if ratio_plot:
            if kwargs.get('ylim_ratio', self.metadata['ylim_ratio']) \
                    is not None:
                try:
                    axes[1].set_ylim(*kwargs.get('ylim_ratio',
                                                 self.metadata['ylim_ratio'])
                                     )
                except:
                    axes[1].set_ylim('auto')
            axes[1].set_yscale('log')

        # Axes labels
        axes[-1].set_xlabel(kwargs.get('xlabel', self.metadata['xlabel']))
        axes[0].set_ylabel(kwargs.get('ylabel', self.metadata['ylabel']),
                           labelpad=5)
        if ratio_plot:
            axes[1].set_ylabel(kwargs.get('ylabel_ratio',
                                          self.metadata['ylabel_ratio']),
                               labelpad=-10)

        # Tick settings
        for ax_instance in axes:
            ax_instance.minorticks_on()
            ax_instance.tick_params(top=True, right=True, bottom=True,
                                    left=True, direction='in',
                                    which='both')

        if ratio_plot:
            axes[0].tick_params(labelbottom=False)
            axes[1].tick_params(axis='y')

        # Extra plot information
        pad = .01

        if kwargs.get('x_scale', self.metadata['x_scale']) == 'log':
            [ax.set_xscale('log') for ax in axes]
        if kwargs.get('y_scale', self.metadata['y_scale']) == 'log':
            [ax.set_yscale('log') for ax in axes]

        # - - - - - - - - - - - - - - - -
        # Additional Formatting
        # - - - - - - - - - - - - - - - -
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

        self.fig = fig
        self.axes = axes
        return fig, axes

    def plot_data(self, data, **kwargs):
        """Plots data in a specified way."""
        # Plot Setup
        fig, axes = kwargs.get('fig', None), kwargs.get('axes', None)
        assert fig is not None, "Must provide a figure to plot on."
        assert axes is not None, "Must provide a set of axes to plot on."

        raise NotImplementedError("Plotter.plot_data() not implemented.")


    def check_conditions(self, data_label, params):
        """Check if the file_path meets the conditions to be
        acted upon.
        """
        return True


    def file_action(self, file_path,
                    local_rc=True,
                    **kwargs):
        """Defining the file action of the Reader to
        load data from files and plot.
        """
        # Load the data
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
        labels_params = catalog.data_labels_and_parameters()

        # Seeing if figure or axes are given
        fig, axes = kwargs.get('fig', None), kwargs.get('axes', None)
        assert not (fig is None) ^ (axes is None),\
            "Either both or neither of fig and axes must be given."
        if fig is None and axes is None:
            fig, axes = self.subplots()

        # Using default conditions if none are given
        if conditions is None:
            def conditions(data_label, params):
                return self.check_conditions(data_label, params)

        if fig_kwargs is None:
            def fig_kwargs(data_label, params):
                return {}

        # If we use a single rc_context for this entire catalog
        if local_rc:
            with mpl.rc_context(self.mpl_rc):
                for file_path, (data_label, params) in zip(file_paths,
                                                          labels_params):
                    if conditions(data_label, params):
                        tmp_kwargs = kwargs.copy()
                        tmp_kwargs.update(fig_kwargs(data_label, params))
                        self.file_action(file_path, local_rc=False,
                                         fig=fig, axes=axes,
                                         **tmp_kwargs)

        # Otherwise, each plot has its own rc_context
        else:
            for file_path, (data_label, params) in zip(file_paths,
                                                      labels_params):
                if conditions(data_label, params):
                    tmp_kwargs = kwargs.copy()
                    tmp_kwargs.update(fig_kwargs(data_label, params))
                    self.file_action(file_path, local_rc=True,
                                     fig=fig, axes=axes,
                                     **tmp_kwargs)

        if kwargs.get('showlegend', self.metadata['showlegend']):
            axes[0].legend()

        if kwargs.get('show', False):
            plt.show()


    def act_on_catalogs(self, catalogs,
                        local_rc=True, conditions=None,
                        fig_kwargs=None, **kwargs):
        """Perform the defined plotting action
        on all files within a list of catalogs.
        """
        # Using default conditions if none are given
        if conditions is None:
            def conditions(data_label, params):
                return self.check_conditions(data_label, params)

        if fig_kwargs is None:
            def fig_kwargs(data_label, params):
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
