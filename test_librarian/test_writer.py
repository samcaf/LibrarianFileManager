import numpy as np

from catalog_info import DataParameters, data_writer,\
    uniform_catalog, nonuniform_catalog

# ---------------------------------
# Generating and Writing
# ---------------------------------
def write_uniform_data(n_samples, minimum=0, maximum=1):
    """Write some uniform data to a catalog."""
    data = np.random.uniform(minimum, maximum, n_samples)
    parameters = DataParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)
    data_writer.write_and_catalog_data(uniform_catalog,
                                       data, 'uniform_data',
                                       parameters)


def write_nonuniform_data(n_samples, minimum=0, maximum=1):
    """Write some nonuniform data to a catalog."""
    data = np.random.normal(0, 1, n_samples)
    data = (np.arctan(data) + np.pi/2)/np.pi
    data = data * (maximum - minimum) + minimum
    parameters = DataParameters(n_samples=n_samples,
                                minimum=minimum, maximum=maximum)
    data_writer.write_and_catalog_data(nonuniform_catalog,
                                       data, 'nonuniform_data',
                                       parameters)


# =====================================
# Implementation
# =====================================

if __name__ == '__main__':
    for n in [100, 1000, 10000]:
        write_uniform_data(n)
        write_nonuniform_data(n)
        write_uniform_data(n, 0, 10)
        write_nonuniform_data(n, 0, 10)
