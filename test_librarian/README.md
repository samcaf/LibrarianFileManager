# Testing LibrarianFileManager

In this folder, I test the LibrarianFileManager (LFM) in a virtual environment.

## Setup

Run
```
pip install -i https://test.pypi.org/simple/ LibrarianFileManager==1.0.4
```
to install LFM.

Then, you can run
```
python3 test_librarian.py
```
to run a quick test of LFM by creating a set of catalogs in a `./catalogs/` directory.
This directory will also contain a README.md describing the contents of the catalogs folder.

You can also generate some test data by running
```
python3 test_writer.py
```
and plot it by running
```
python3 test_plotter.py
```
