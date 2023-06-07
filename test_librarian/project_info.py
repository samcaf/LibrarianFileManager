# =====================================
# Setup
# =====================================

# ---------------------------------
# Project Information
# ---------------------------------
PROJECT_LOCATION = "./catalogs"
project_metadata = {'description':
                    'A test project for the Librarian File Manager'
                    }

# ---------------------------------
# Catalog Initialization Information
# ---------------------------------
# Names and locations
catalog_names = ['uniform_data', 'nonuniform_data', 'figures']
catalog_dirs = {name: f"{PROJECT_LOCATION}/{name}"
                for name in catalog_names}

# More detailed information
catalog_metadata = {}
catalog_metadata['uniform_data'] = {
    'description': 'A catalog of uniformly distributed random data',
    'recognized_names': ['uniform_data'],
    'recognized_extensions': ['.npy'],
}
catalog_metadata['nonuniform_data'] = {
    'description': 'A catalog of nonuniformly distributed random data',
    'recognized_names': ['nonuniform_data'],
    'recognized_extensions': ['.npy'],
}
catalog_metadata['figures'] = {
    'description': 'A catalog of figures',
    'recognized_names': ['uniform_figure', 'nonuniform_figure',
                         'mixed_figure'],
    'recognized_extensions': ['.pdf'],
}
