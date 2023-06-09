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
    """Saves and catalogs plots of uniform data."""
    if not isinstance(n_samples, list):
        n_samples = [n_samples]
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)

    def conditions(data_name, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    fig, _ = plotter.subplots()

    def fig_kwargs(data_name, parameters):
        return {'label': f'{data_name} {parameters["n_samples"]}'}

    plotter.act_on_catalog(uniform_catalog,
                           conditions=conditions,
                           fig_kwargs=fig_kwargs)

    figure_catalog.savefig(fig, f'uniform_{minimum}-{maximum}',
                            parameters,)

def save_nonuniform_plots(n_samples, minimum=0, maximum=1):
    """Saves and catalogs plots of nonuniform data."""
    if not isinstance(n_samples, list):
        n_samples = [n_samples]
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)

    def conditions(data_name, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    fig, _ = plotter.subplots()

    def fig_kwargs(data_name, parameters):
        return {'label': f'{data_name} {parameters["n_samples"]}'}

    plotter.act_on_catalog(nonuniform_catalog,
                           conditions=conditions,
                           fig_kwargs=fig_kwargs)

    figure_catalog.savefig(fig, f'nonuniform_{minimum}-{maximum}',
                            parameters,)


def save_mixed_plots(n_samples, minimum=0, maximum=1):
    """Saves and catalogs plots both types of data."""
    if not isinstance(n_samples, list):
        n_samples = [n_samples]
    parameters = PlotParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)

    def conditions(data_name, params):
        cond_met = int(params['n_samples']) in n_samples
        cond_met = cond_met and float(params['minimum']) == minimum
        cond_met = cond_met and float(params['maximum']) == maximum
        return cond_met

    fig, _ = plotter.subplots()

    def fig_kwargs(data_name, parameters):
        return {'label': f'{data_name} {parameters["n_samples"]}'}

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
