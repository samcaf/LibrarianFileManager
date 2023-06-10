# Example Project with LibrarianFileManager

In this folder, I test the LibrarianFileManager (LFM) in a virtual environment.

## What's Inside?
The example project files (`test_librarian.py`, `test_writer.py`, `test_plotter.py`) demonstrate specific use cases of the LibrarianFileManager (LFM) package. The `project_info.py` and `catalog_info.py` files provide configuration settings and definitions for the project and its catalogs.

To run the example project, execute the desired test file (`test_librarian.py`, `test_writer.py`, `test_plotter.py`) in the project's root directory. Ensure that the LibrarianFileManager package is installed and the necessary dependencies are met.

Feel free to explore and modify the example project files to suit your specific project requirements.

### Quick Start with Make
Feel free to set up the virtual environment for the test project via
```
make setup
```

Then you can initialize the Librarian catalogs with
```
make librarian
```
which runs `python3 test_librarian.py` in the virtual environment.

The commands
```
make data
```
and
```
make plots
```
run `python3 test_writer` (which generates some test data in the form of random numbers) and `python3 test_plotter` (which plots the test data as histograms), respectively, in the virtual environment.

## Details:

### Example LFM Project Folder Structure

The example LFM project folder, `test_librarian`, contains the following files:

- `project_info.py`: Contains setup and project information, including project location, project metadata, catalog initialization information, catalog metadata, and catalog parameters.

- `catalog_info.py`: Defines catalogs, writers, and plotters used in the project. It includes the setup for catalog parameters, catalog objects, writer objects, and plotter objects.

- `test_librarian.py`: Demonstrates the creation of a project using the Librarian class. It initializes a Librarian object with project metadata, catalog directories, catalog metadata, and catalog parameters, and creates the file structure for the project.

- `test_writer.py`: Provides examples of generating and writing data to catalogs using the Writer class. It includes functions to write uniform and nonuniform data to respective catalogs.

- `test_plotter.py`: Demonstrates saving and cataloging plots using the Plotter class. It includes functions to save and catalog plots of uniform and nonuniform data, as well as mixed data from multiple catalogs.

### Workflow of a General Project

The LibrarianFileManager (LFM) package enables a streamlined workflow for managing projects and their associated data. Here's an overview of the workflow:

1. **Setup Project**: Modify `project_info.py` to configure project-specific information such as project location, project metadata, catalog initialization information, catalog metadata, and catalog parameters.

2. **Create Catalogs**: Define catalogs in `catalog_info.py` using the Catalog class. Specify the catalog names, directories, and loading requirements (the parameters used to describe the files in the catalog must also be specified, but are in `project_info.py` in this example).

3. **Manage Files**: Utilize the Writer class (`test_writer.py`) to generate and write data to the catalogs. Use the provided functions (`write_uniform_data` and `write_nonuniform_data`) as examples to customize data generation and writing for your project.

4. **Plot Data**: Use the Plotter class (`test_plotter.py`) to save and catalog plots of the data. Customize the provided functions (`save_uniform_plots`, `save_nonuniform_plots`, and `save_mixed_plots`) to suit your project's visualization needs.
