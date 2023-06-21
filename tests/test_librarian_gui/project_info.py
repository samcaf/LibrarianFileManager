# =====================================
# Setup
# =====================================

# ---------------------------------
# Project Information
# ---------------------------------
PROJECT_DIRECTORY = "./catalogs"
PROJECT_METADATA = {'description':
                    'A test project for the Librarian File Manager'
                    }

# ---------------------------------
# Catalog Initialization Information
# ---------------------------------
# Names
CATALOG_NAMES = ['uniform_data', 'nonuniform_data', 'figures']

# More detailed information
CATALOG_METADATA = {}
CATALOG_METADATA['uniform_data'] = {
    'description': 'A catalog of uniformly distributed random data',
    'recognized_names': ['uniform_data'],
    'recognized_extensions': ['.npy'],
}
CATALOG_METADATA['nonuniform_data'] = {
    'description': 'A catalog of nonuniformly distributed random data',
    'recognized_names': ['nonuniform_data'],
    'recognized_extensions': ['.npy'],
}
CATALOG_METADATA['figures'] = {
    'description': 'A catalog of figures',
    'recognized_names': ['uniform_figure', 'nonuniform_figure',
                         'mixed_figure'],
    'recognized_extensions': ['.pdf'],
}

# More detailed information
CATALOG_PARAMETERS = {}

CATALOG_PARAMETERS['uniform_data'] = {
    'n_samples': 'int',
    'minimum': 'float',
    'maximum': 'float',
}
CATALOG_PARAMETERS['nonuniform_data'] = \
    CATALOG_PARAMETERS['uniform_data']

CATALOG_PARAMETERS['figures'] = None

# Adding it all together
LOADOUT = {
    'project directory': PROJECT_DIRECTORY,
    'project metadata': PROJECT_METADATA,
    'catalog names': CATALOG_NAMES,
    'catalog metadata': CATALOG_METADATA,
    'catalog parameters': CATALOG_PARAMETERS,
}
