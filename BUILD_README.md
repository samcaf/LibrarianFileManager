# README for building the project

I'm writing this auxiliary README so it's harder to forget how to make this into a python package. I've automated everything in the `Makefile` here

This repository provides a Makefile that simplifies the process of building and uploading the LibrarianFileManager package. Follow the instructions below to build the package.

## Prerequisites

Before building the LibrarianFileManager package, ensure you have the following prerequisites installed:

- Python 3.x
- Make

## Pre-Build
Before building, I recommend checking out that the tests work with the local version of the code. There are two built in tests:

```
cd ./tests/test_librarian/
make test_local
```

and

```
cd ./tests/test_librarian_gui
make test_local
```

## Building Process

The LibrarianFileManager package can be built using the provided Makefile, which automates the build and upload steps. Follow the steps below to build the package:

1. **Set up the virtual environment**: Run the following command to set up a virtual environment and install the necessary dependencies:

   ```
   make venv
   ```

2. **Build the package**: Run the following command to build the LibrarianFileManager package:
    ```
    make build
    ```

3. **Upload the package**: To upload the package to the PyPI test repository, run the following command:
    ```
    make upload_test
    ```
    If you want to upload the package to the PyPI production repository, use the following command instead:
    ```
    make upload
    ```

That's it! You have successfully built and uploaded the LibrarianFileManager package using the provided Makefile.

## Summary

The provided Makefile simplifies the build process for the LibrarianFileManager package. By following the steps outlined in this document, you can easily set up a virtual environment, build the package, and upload it to PyPI or TestPyPI. Remember to ensure you have the necessary credentials and permissions to upload the package to PyPI.
