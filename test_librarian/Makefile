# Makefile for a LibrarianFileManager test project

#===========================================
# Include the configuration.
#===========================================
-include Makefile.inc
# Includes compiler information and library names


#===========================================
# Rules for building files
#===========================================

#------------------------------------
# Main Functions
#------------------------------------

# - - - - - - - - - - - - - - -
# Rules:
# - - - - - - - - - - - - - - -
# Possible make targets (to be make with ```make [xxx]```)
.PHONY : reset default librarian data plots setup venv update clean_all clean_venv clean_catalogs

# - - - - - - - - - - - - - - -
# Default
# - - - - - - - - - - - - - - -
# Go through full pipeline to make plots by default
default : librarian data plots
.DEFAULT_GOAL := default

# - - - - - - - - - - - - - - -
# All
# - - - - - - - - - - - - - - -
# Make all main functions
reset: clean_all setup librarian data plots


# =======================================================
# LibrarianFileManager Code:
# =======================================================

# Telling Make to run librarian code
librarian:
	# =======================================================
	# Setting up project with a Librarian:
	# =======================================================
	. venv/bin/activate; python3 test_librarian.py
	@printf "\n"

# Telling Make to run writer code
data:
	# =======================================================
	# Creating random data and saving with a Writer
	# =======================================================
	. venv/bin/activate; python3 test_writer.py
	@printf "\n"

# Telling Make to run plotter code
plots:
	# =======================================================
	# Preparing plots with a Plotter
	# =======================================================
	. venv/bin/activate; python3 test_plotter.py
	open catalogs/figures/


# =======================================================
# Setup
# =======================================================

# Telling Make to make a virtual environment
venv:
	# =======================================================
	# Setting up virtual environment:
	# =======================================================
	python3 -m venv venv
	. venv/bin/activate; pip3 install -r requirements.txt
	@printf "\n"

# Telling Make to update by installing the latest version
# of LibrarianFileManager in the virtual environment
update:
	# =======================================================
	# Updating LibrarianFileManager in virtual environment:
	# =======================================================
	. venv/bin/activate; pip3 install --upgrade LibrarianFileManager
	@printf "\n"

# The full setup involves making a venv and installing LFM
setup: venv update


# =======================================================
# Cleaning
# =======================================================

# Telling Make to clean by removing all catalogs
clean_catalogs:
	# =======================================================
	# Removing the test project catalogs:
	# =======================================================
	rm -r catalogs
	@printf "\n"

# Telling Make to clean by removing the virtual environment
clean_venv:
	# =======================================================
	# Removing the test project virtual environment:
	# =======================================================
	rm -r venv
	@printf "\n"

# Cleaning all additional files
clean_all: clean_venv clean_catalogs
