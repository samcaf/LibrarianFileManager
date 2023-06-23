import numpy as np

from catalog_info import PlotParameters,\
    plotter, figure_catalog,\
    uniform_catalog, nonuniform_catalog


# =====================================
# Setup
# =====================================

# ---------------------------------
# Catalogs and Writers
# ---------------------------------

# ---------------------------------
# Generating and Writing
# ---------------------------------
def save_uniform_plots(n_samples, minimum=0, maximum=1):
    """Saves and catalogs plots of uniform data.
    This is the most detailed example plot function
    I give in this file.

    In particular, it checks if the figure is already in
    the figure_catalog before creating a new figure.
    """
    if not isinstance(n_samples, list):
        n_samples = [n_samples]

    # Checking existence of figure with the given parameters
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum,
                                maximum=maximum)

    for _, params in figure_catalog.data_labels_and_parameters():
        params = PlotParameters(**{
            'n_samples': [int(n) for n in
                          params['n_samples'].\
                          lstrip('[').\
                          rstrip(']').\
                          split(', ')
                          ],
            'minimum': float(params['minimum']),
            'maximum': float(params['maximum'])
        })
        if params == parameters:
            print("Figure already exists.")
            return

    # Creating figure
    fig, _ = plotter.subplots()

    # Setting up metadata for the plots
    # to be contained within the figure
    def fig_kwargs(data_label, parameters):
        return {'label': f'{data_label} {parameters["n_samples"]}'}

    # Setting conditions for which data to plot
    def conditions(data_label, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    # Plotting all data which satisfies the conditions
    plotter.act_on_catalog(uniform_catalog,
                           conditions=conditions,
                           fig_kwargs=fig_kwargs)

    # Saving figure
    figure_catalog.savefig(fig, f'uniform_{minimum}-{maximum}',
                            parameters,)

def save_nonuniform_plots(n_samples, minimum=0, maximum=1):
    """Saves and catalogs plots of nonuniform data."""
    if not isinstance(n_samples, list):
        n_samples = [n_samples]
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)

    def conditions(data_label, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    fig, _ = plotter.subplots()

    def fig_kwargs(data_label, parameters):
        return {'label': f'{data_label} {parameters["n_samples"]}'}

    plotter.act_on_catalog(nonuniform_catalog,
                           conditions=conditions,
                           fig_kwargs=fig_kwargs)

    # Saving figure
    figure_catalog.savefig(fig, f'nonuniform_{minimum}-{maximum}',
                            parameters,)


def save_mixed_plots(n_samples, minimum=0, maximum=1):
    """Saves and catalogs plots both types of data."""
    if not isinstance(n_samples, list):
        n_samples = [n_samples]
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)

    def conditions(data_label, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    fig, _ = plotter.subplots()

    def fig_kwargs(data_label, parameters):
        return {'label': f'{data_label} {parameters["n_samples"]}'}

    plotter.act_on_catalogs([uniform_catalog, nonuniform_catalog],
                           conditions=conditions,
                           fig_kwargs=fig_kwargs)

    figure_catalog.savefig(fig, f'mixed_{minimum}-{maximum}',
                           parameters, file_extension='.pdf')


# =====================================
# Implementation
# =====================================

if __name__ == '__main__':
    for n in [[100], [100, 1000, 10000]]:
        save_uniform_plots(n)
        save_uniform_plots(n, 0, 10)
        save_nonuniform_plots(n)
        save_nonuniform_plots(n, 0, 10)
        save_mixed_plots(n)
        save_mixed_plots(n, 0, 10)
