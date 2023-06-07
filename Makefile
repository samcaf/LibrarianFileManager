# Makefile for building and exporting LibrarianFileManager


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
.PHONY : all test venv clean_all clean_build clean_venv build export

# - - - - - - - - - - - - - - -
# Default
# - - - - - - - - - - - - - - -
# Go through full pipeline to make plots by default
test : clean_build build export_test
.DEFAULT_GOAL := test

# - - - - - - - - - - - - - - -
# All
# - - - - - - - - - - - - - - -
# Make all main functions
all: venv clean_all build export_prod


# =======================================================
# Building and exporting
# =======================================================

build:
	# =======================================================
	# Building project:
	# =======================================================
	# Please make sure you have updated the version number in
	# the `pyproject.toml` file
	python3 -m build
	@printf "\n"

export_test:
	# =======================================================
	# Exporting project to test.pypi.org:
	# =======================================================
	python3 -m twine upload --repository testpypi dist/*
	@printf "\n"

export_prod:
	# =======================================================
	# Exporting project to pypi.org:
	# =======================================================
	# python3 -m twine upload --repository pypi dist/*
	@printf "\n"


# =======================================================
# Setup
# =======================================================

# Telling Make to make a virtual environment
venv:
	# =======================================================
	# Setting up virtual environment:
	# =======================================================
	python3 -m venv venv
	. venv/bin/activate; pip3 install -r build_requirements.txt
	@printf "\n"


# =======================================================
# Cleaning
# =======================================================

# Telling Make to clean by removing all catalogs
clean_build:
	# =======================================================
	# Removing build directories:
	# =======================================================
	rm -r dist
	rm -r build
	@printf "\n"

# Telling Make to clean by removing the virtual environment
clean_venv:
	# =======================================================
	# Removing virtual environment:
	# =======================================================
	rm -r venv
	@printf "\n"

# Cleaning all additional files
clean_all: clean_venv clean_build
