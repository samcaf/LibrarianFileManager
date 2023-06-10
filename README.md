# LibrarianFileManager (LFM)

A Librarian for managing your files. General purpose file management tools for initializing, keeping track of, and interacting with file structures e.g. for cataloging data, plotting of figures, etc.).

Also located at
https://pypi.org/project/LibrarianFileManager/


## Features

- **Project Management**: Easily create and manage projects with associated metadata.
- **Catalog Creation**: Create catalogs within the project, each with its own folder and metadata.
- **File Structure Management**: Add, remove, and update files within the file structure.
- **Metadata Management**: Set and retrieve metadata for both projects and catalogs.
- **Data Manipulation and Analysis**: Read, manipulate, and analyze data within or across catalogs, with arbitrary user constraints on the data to analyze.

## Installation
Set up LFM with pip via
```
pip install LibrarianFileManager
```

## Introduction: Workflow of a General Project

The LibrarianFileManager (LFM) package provides a streamlined workflow for managing projects and their associated data. Here's an overview of how the classes (Librarian, Catalog, Actor) and their relationships enable a more efficient workflow:

1. **Create a Project**: Initialize a Librarian object to represent your project. Set project-level metadata such as author, date, and any other relevant information.

2. **Create Catalogs**: Use the Librarian object to create catalogs within the project. Each catalog represents a specific collection of data and has its own folder and metadata. Define the catalog's purpose, description, and any other relevant metadata.

3. **Manage Files**: Add, remove, and update files within the file structure of each catalog. Use the Librarian object to perform these file management operations. Assign metadata to files to provide additional context and information.

4. **Perform Actions**: Utilize the Actor subclasses (Reader, Writer, Plotter, and other custom actors) to perform actions on the files. The Reader class enables reading data from files, the Writer class facilitates writing data to files, and the Plotter class assists in visualizing data. Customize the actors based on your project's specific requirements.


## Usage by Example: The `test_librarian` Example LFM Project

The `test_librarian` example project demonstrates how to utilize the LibrarianFileManager (LFM) package to manage a project's data and file structure efficiently. It showcases the key components and workflow steps outlined in the previous section.

- **Project Setup**: The `project_info.py` file contains the necessary setup and project information, such as the project location, project metadata, and catalog details.

- **Catalog Initialization**: The `catalog_info.py` file defines the catalogs used in the project, along with their associated metadata, writers, and plotters.

- **Creating the Project**: The `test_librarian.py` file showcases the creation of a project using the Librarian class. It initializes a Librarian object with the project metadata, catalog directories, catalog metadata, and catalog parameters. This step establishes the file structure and sets the stage for data management.

- **Data Generation and Writing**: The `test_writer.py` file provides examples of generating and writing data to catalogs using the Writer class. It includes functions to write both uniform and nonuniform data to their respective catalogs.

- **Plotting and Visualization**: The `test_plotter.py` file demonstrates how to save and catalog plots using the Plotter class. It includes functions to save and catalog plots of uniform, nonuniform, and mixed data from multiple catalogs.

The `test_librarian` example project exemplifies the philosophy behind the LibrarianFileManager package's workflow. By providing clear organization, data management capabilities, and efficient workflows, the package enables users to streamline their projects and focus on their data analysis and research tasks.
