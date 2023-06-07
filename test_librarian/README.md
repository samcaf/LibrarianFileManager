# Testing LibrarianFileManager

In this folder, I test the LibrarianFileManager (LFM) in a virtual environment.

## Setup
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
