from librarian.librarian import Librarian

from project_info import PROJECT_LOCATION,\
    project_metadata, catalog_names, catalog_dirs,\
    catalog_metadata


# Creating the Project with Librarian
if __name__ == "__main__":
    test_librarian = Librarian(PROJECT_LOCATION, project_metadata,
                               catalog_dirs,  catalog_metadata)
    test_librarian.create_stacks()
