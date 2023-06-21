from librarian.librarian import Librarian

from project_info import PROJECT_DIRECTORY,\
    PROJECT_METADATA, CATALOG_DIRS,\
    CATALOG_METADATA, CATALOG_PARAMETERS


# Creating the Project with Librarian
if __name__ == "__main__":
    test_librarian = Librarian(PROJECT_DIRECTORY, PROJECT_METADATA,
                               CATALOG_DIRS, CATALOG_METADATA,
                               CATALOG_PARAMETERS)
    test_librarian.create_stacks()
