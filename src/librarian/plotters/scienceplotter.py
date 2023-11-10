"""This module contains the SciencePlotter class,
which is a subclass of the Plotter class designed
to produce plots which take in a set of parameters
describing cataloged data and output plots which
show certain parameters varied in each plot and
certain parameters held fixed.
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import rc

import itertools

from librarian.actors.plotter import Plotter

# Logging
import logging
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())

# =====================================
# Additional Analysis Utilities
# =====================================
def reusable_iterable(val):
    """Makes the input into an iterable even if it is
    not a list, tuple, or other iterable (excluding strings)."""
    if hasattr(val, '__iter__') and not isinstance(val, str):
        return [v for v in val]
    return [val]


def distinct_parameters(parameters):
    """Returns an iterable of all of the ``distinct'' parameters
    within parameters, where distinct means that any list-valued
    value in the original list is turned into a list of dicts,
    (i.e. the list is unpacked ``functorially'' into the dicts).
    """
    # Getting the values of the parameters
    values = map(reusable_iterable, parameters.values())

    # so that we can use itertools.product:
    distinct_values = itertools.product(*values)

    # Now we can return a list of dicts:
    return [dict(zip(parameters.keys(), vals))
            for vals in distinct_values]


def distinct_parameter_values(parameters):
    """Creates an iterable of only the values of the parameters
    in the given parameter dict, so that we can iterate over
    distinct values of the parameters.

    The list analog to the dictionary-valued function
    ``distinct_parameters'' above.
    """
    # Getting the values of the parameters
    values = map(reusable_iterable, parameters.values())
    # Returning a list so we have a re-usable iterable
    return reusable_iterable(itertools.product(*values))


# =====================================
# Additional Plotting Utilities
# =====================================

def stamp(left_x, top_y, axes,
          delta_y=0.075,
          textops_update=None,
          **kwargs):
    """Adds a stamp to figures"""
    # Text options
    textops = {'horizontalalignment': 'left',
               'verticalalignment': 'center',
               'fontsize': 8.5,
               'transform': axes.transAxes}
    if isinstance(textops_update, dict):
        textops.update(textops_update)

    # Add text line by line
    for i in range(len(kwargs)):
        y_val = top_y - i*delta_y
        text = kwargs.get('line_' + str(i))
        if text is not None:
            axes.text(left_x, y_val, text,
                    **textops)

def valid_stamp_loc(stamp_loc):
    """Ensures that the stamp_loc given to stamp is valid,
    and raises errors otherwise"""
    if isinstance(stamp_loc, tuple):
        if len(stamp_loc) != 2:
            raise ValueError("If stamp_loc is given as a tuple, it "
                             "must have length 2 (x, y), but "
                             f"stamp_loc = {stamp_loc}")
        return True
    elif stamp_loc is None:
        return True
    return False


# =====================================
# ###########################################
# Main Functionality: SciencePlotter Class
# ###########################################
# =====================================

# TODO: Right now, act_on_catalogs accepts a single dict, whose values
# TODO:     may be lists, as the set of parameters to plot.
# TODO: I would also like to be able to give a list of dicts, each of
# TODO:     which has a single key-value pair, as the set of parameters
# TODO:     (even better would be that each dict in the list could have
# TODO:      lists as values themselves...)


class SciencePlotter(Plotter):
    """Plotter class for plotting sets of data across multiple plots,
    with certain parameters held fixed within each plot, and certain
    parameters varied.

    This is still an abstract class, and usable subclasses must
    implement the `plot_data` method.
    """
    def __init__(self, metadata_defaults=None,
                 varied_parameters=None,
                 accepted_data_labels=None,
                 require_all_files=True,
                 **kwargs):
        """Initializes the SciencePlotter."""
        kwargs['title'] = kwargs.get('title', 'SciencePlot')

        rc('text', usetex=True)
        if metadata_defaults is None:
            metadata_defaults = {}
        if metadata_defaults.get('showlegend', None) is None:
            metadata_defaults['showlegend'] = False

        # - - - - - - - - - - - - - - - - -
        # Basic setup
        # - - - - - - - - - - - - - - - - -
        self.varied_parameters = varied_parameters
        self.accepted_data_labels = accepted_data_labels
        self.require_all_files = require_all_files

        super().__init__(metadata_defaults, **kwargs)


    # =====================================
    # Conditions for Plotting
    # =====================================
    def check_conditions(self, data_label, params):
        """Check if the file_path meets the conditions to be
        acted upon.

        Could be implemented by subclasses for more stringent plots.
        """
        return True


    def consider_dataset(self, data_label,
                         plot_parameters,
                         dataset_parameters):
        """Conditions for a dataset to be considered:
        - It must have an accepted data_label
        - It must have the given parameters as a subset
          of its parameters
        """
        valid_data_label = self.accepted_data_labels is None \
            or data_label in self.accepted_data_labels

        valid_plot_parameters = \
            set(plot_parameters.items()).issubset(
                set(dataset_parameters.items()))

        return valid_data_label and valid_plot_parameters


    def good_dataset(self, data_label,
                     plot_parameters,
                     dataset_parameters,
                     extra_conditions=None):
        """Conditions for a dataset to be plotted"""
        valid_dataset = self.consider_dataset(data_label,
                                              plot_parameters,
                                              dataset_parameters) \
            and self.check_conditions(data_label,
                                      dataset_parameters)

        if extra_conditions is None:
            return valid_dataset
        return valid_dataset and extra_conditions(data_label,
                                                  plot_parameters,
                                                  dataset_parameters)


    # =====================================
    # Setting up for parameter iteration
    # =====================================
    def varied_parameters_iterable(self, parameters):
        """Returns an iterable of the varied parameters."""
        varied_parameters = {param: parameters[param]
                             for param in self.varied_parameters}

        return distinct_parameter_values(varied_parameters)


    def fixed_parameters(self, parameters):
        """Returns a dictionary of the fixed parameters."""
        return {param: parameters[param]
                for param in parameters
                if param not in self.varied_parameters}


    def fixed_parameters_iterable(self, parameters):
        """Returns an iterable of the fixed parameters."""
        fixed_parameters = {param: parameters[param]
                    for param in self.fixed_parameters(parameters)}
        return distinct_parameter_values(fixed_parameters)


    # =====================================
    # Pre-plotting
    # =====================================
    def prepare_figure(self, fig, axes,
                       parameters: dict,
                       varied_parameter_names: list):
        """Prepares axes for plotting.
        Useful e.g. for setting up color cycles.
        """
        pass


    # =====================================
    # Post-processing
    # =====================================
    def stamp_axes(self, stamp_loc: tuple, axes,
                   fixed_param_values: dict):
        """Adds a stamp to the given axes associated
        with the parameters that are fixed for the plot
        on those axes.
        """
        # Location of the stamp
        if stamp_loc is None:
            stamp_loc = (0.5, 0.95)

        # Text for the stamp
        stamp_text = {
            f'line_{iparam}': f"{param} = {val}"
                for iparam, (param, val)
                in enumerate(fixed_param_values.items())
            }
        stamp_text.update({'textops_update':
                          {'fontsize': 11,
                           'horizontalalignment': 'center'}
                           })
        if isinstance(axes, list):
            stamp(*stamp_loc, axes[0], **stamp_text)
        else:
            stamp(*stamp_loc, axes, **stamp_text)


    def process_figure(self, fig, axes,
                       fixed_param_values,
                       **kwargs):
        """Processes the figure after plotting
        all relevant data.
        """
        stamp_loc = kwargs.get('stamp_loc', None)
        legend_loc = kwargs.get('legend_loc', 'best')

        if not valid_stamp_loc(stamp_loc):
            try:
                stamp_loc = stamp_loc(fixed_param_values)
                assert valid_stamp_loc(stamp_loc)
            except TypeError as err:
                raise TypeError("stamp_loc must be None, "
                                "a tuple, or a function") from err

        self.stamp_axes(stamp_loc, axes, fixed_param_values)

        if kwargs.get('showlegend', self.metadata['showlegend']):
            axes[0].legend(loc=legend_loc)


    # =====================================
    # Main Functionality: Plotting
    # =====================================
    def act_on_catalogs(self, catalogs,
                        parameters,
                        local_rc=True,
                        conditions=None,
                        fig_kwargs=None,
                        **kwargs):
        """Plots datasets from the given catalogs across
        several figures, holding certain parameters fixed
        within each plot and varied others.
        """
        # ---------------------------------
        # Plot options
        # ---------------------------------
        if fig_kwargs is None:
            def fig_kwargs(data_label, params):
                return {}

        stamp_loc = kwargs.pop('stamp_loc', None)
        if stamp_loc is None:
            def stamp_loc(fixed_param_values):
                return None

        fig_catalog = kwargs.pop('fig_catalog', None)
        figure_label = kwargs.pop('figure_label', None)
        if fig_catalog is None:
            assert figure_label is not None, \
                "Must provide figure_label to save to figure catalog."

        reporter = kwargs.pop('reporter', None)
        if reporter is not None:
            assert fig_catalog is not None, \
                "Must provide fig_catalog in order to make reports."

        # ---------------------------------
        # Preparation for parameter checking
        # ---------------------------------
        # Preparing to check for files which are in
        # the given parameters but not in one of the
        # given catalogs
        found_missing_file = False

        # Also, we will continue searching for files with the
        # given parameters even if we find one missing file, to
        # provide information about all missing files to the user.
        # However, we may not continue plotting the associated datasets,
        # to save time
        continue_plotting = True

        # - - - - - - - - - - - - - - - - -
        # Separating parameters
        # - - - - - - - - - - - - - - - - -
        fixed_param_names = self.fixed_parameters(parameters).keys()
        fixed_param_iter = self.fixed_parameters_iterable(parameters)

        varied_param_names = self.varied_parameters
        varied_param_iter = self.varied_parameters_iterable(parameters)

        LOGGER.info("\n# =======================================")
        LOGGER.info("# Creating plots:")
        LOGGER.info("# =======================================")
        LOGGER.info("# Parameters: (some fixed w/in plots, some varied)")
        LOGGER.info("# ---------------------------------------")
        for key, val in parameters.items():
            LOGGER.info(f"#\t- {key}: {val} "
                +("(varied)" if key in varied_param_names
                  else "(fixed)"))
        LOGGER.info("# ---------------------------------------")
        LOGGER.info("# =======================================\n")

        # ---------------------------------
        # Loop over individual figures (fixed params sets)
        # ---------------------------------
        LOGGER.debug("Looping over figures:")
        for fixed_param_set in fixed_param_iter:
            # Setting up for each individual plot,
            fig, axes = self.subplots()

            # With a set of FIXED PARAMETERS
            # for this figure, called fixed_fig_params
            fixed_fig_params = dict(zip(fixed_param_names,
                                        fixed_param_set))
            LOGGER.debug("# ---------------------------------------")
            LOGGER.debug(f"\t* New figure with\n\t{fixed_fig_params = }")

            self.prepare_figure(fig, axes,
                                parameters,
                                varied_param_names)

            LOGGER.debug("\tLooping over datasets for the figure:")
            LOGGER.debug(f"\t({varied_param_names = })")
            with mpl.rc_context(self.mpl_rc):
                # - - - - - - - - - - - - - - - - -
                # Looping over parameters for each dataset
                # - - - - - - - - - - - - - - - - -
                for varied_param_set in varied_param_iter:
                    # Finding the varied parameters for this dataset
                    dataset_varied_params = dict(zip(varied_param_names,
                                                     varied_param_set))
                    LOGGER.debug("\t\t* New dataset with\n"
                                f"\t\t{dataset_varied_params = }")

                    # and _all_ parameters associated with this dataset
                    dataset_params = {**fixed_fig_params,
                                      **dataset_varied_params}
                    LOGGER.log(5, f"\t\t-{dataset_params = }")

                    # - - - - - - - - - - - - - - - - -
                    # Adding datasets from each catalog
                    # - - - - - - - - - - - - - - - - -
                    for catalog in catalogs:
                        file_paths = catalog.get_files()
                        labels_params = catalog.data_labels_and_parameters()

                        # Finding if the desired dataset exists in
                        # the catalog
                        found_dataset = False
                        for file_path, (data_label, params) in \
                                zip(file_paths, labels_params):
                            # Configuring parameters for fair comparison
                            params = catalog.configure_parameters(params)
                            dataset_params = catalog.configure_parameters(
                                                            dataset_params)

                            # Checking if the file has the desired parameters
                            consider_dataset = self.consider_dataset(
                                                    data_label,
                                                    dataset_params, params)
                            if consider_dataset:
                                # If the desired dataset exists,
                                found_dataset = True
                                good_dataset = self.good_dataset(
                                                    data_label,
                                                    dataset_params, params,
                                                    extra_conditions=conditions)
                                if good_dataset and continue_plotting:
                                    # and also satisfies given conditions,
                                    # set up kwargs for the plot,
                                    tmp_kwargs = kwargs.copy()
                                    tmp_kwargs.update(
                                        fig_kwargs(data_label, params)
                                    )
                                    # and then plot it!
                                    self.file_action(file_path,
                                                     local_rc=False,
                                                     fig=fig, axes=axes,
                                                     parameters=dataset_params,
                                                     **tmp_kwargs)

                        if not found_dataset:
                            # If the desired dataset does not exist in
                            # the catalog, warn the user
                            found_missing_file = True
                            LOGGER.warn('No file with parameters\n\t'
                                  f'{dataset_params}\n'
                                  'and data_label in\n\t'
                                  f'{self.accepted_data_labels}\n'
                                  'found in catalog '
                                  f'{catalog.name()}.\n')
                            if self.require_all_files and continue_plotting:
                                continue_plotting = False
                                LOGGER.warn('No longer plotting '
                                      '(but still searching to ensure '
                                      'all other files are present).\n')
                                plt.close(fig)

            # - - - - - - - - - - - - - - - - -
            # Figure post-processing
            # - - - - - - - - - - - - - - - - -
            LOGGER.debug("\t# - - - - - - - - - - - - - - - - - ")
            LOGGER.debug("\tPlotting for this figure complete")
            if continue_plotting:
                LOGGER.debug("\tProcessing figure:")
                LOGGER.debug(f"\t{fixed_fig_params = }\n")
                self.process_figure(fig, axes, fixed_fig_params)

                # Saving figure
                if fig_catalog is not None:
                    LOGGER.debug(f"\tSaving figure to {fig_catalog.name()}"
                                 " with parameters:")
                    # Setting up a dictionary of parameters for the
                    # figure, which includes both the fixed
                    # parameters -- with single values --
                    # and the varied parameters -- with lists of values
                    fig_params = fixed_fig_params.copy()
                    fig_params.update(
                        ( (key, parameters[key])
                           for key in varied_param_names
                         )
                    )

                    fig_params.update(self.metadata)
                    LOGGER.debug(f"\t- {fig_params = }")

                    fig_catalog.savefig(fig,
                                figure_label,
                                fig_params,
                                nested_folder=figure_label)

                # Reporting on figure
                if reporter is not None:
                    LOGGER.debug("\t- Reporting figure to "
                                 f"{reporter}")
                    reporter.report_data_from_catalog(fig_catalog,
                                                      figure_label,
                                                      fig_params)
            LOGGER.debug("# ---------------------------------------\n")

        # ---------------------------------
        # Finalizing
        # ---------------------------------
        if found_missing_file and self.require_all_files:
            raise FileNotFoundError('Not all files found in catalog '
                                    ' (you should see some warnings '
                                    'above). Stopping...\n'
                                    '(if you would like to continue '
                                    'plotting anyway, please set '
                                    'require_all_files=False)')



    def act_on_catalog(self, catalog,
                        parameters,
                        local_rc=True,
                        conditions=None,
                        fig_kwargs=None,
                        **kwargs):
        """Plots from only a single catalog."""
        self.act_on_catalogs([catalog], parameters, local_rc,
                             conditions, fig_kwargs,
                             **kwargs)


    def legend_prescription(self, params):
        """Generates a legend entry for the dataset
        corresponding to the given parameters.
        """
        params = {key: val for key, val in params.items()
                  if key in self.varied_parameters}

        # By default, legend entry prints any varied parameters
        if len(params) == 0:
            return None

        self.metadata['showlegend'] = True
        legend_entry = ', '.join([f'{key}={val}'
                                  for key, val in params.items()])
        return legend_entry


    def plot_data(self, data, **kwargs):
        """Plots data in a specified way.
        Example beginning of an implementation below.
        """
        # Plot Setup
        fig, axes = kwargs.get('fig', None), kwargs.get('axes', None)
        assert fig is not None, "Must provide a figure to plot on."
        assert axes is not None, "Must provide a set of axes to plot on."

        # Getting parameters from kwargs
        # (useful if plot style should be parameter-dependent)
        try:
            parameters = kwargs.pop('parameters')
        except KeyError as err:
            raise KeyError("Must provide parameters to plot.") from err

        # Setting up for legend
        legend_prescription = kwargs.pop('legend_prescription',
                                         self.legend_prescription)
        legend_entry = legend_prescription(parameters)

        raise NotImplementedError("Plotter.plot_data() not implemented.")
