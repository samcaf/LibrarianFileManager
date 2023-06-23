# Makefile for testing LibrarianFileManager


#===========================================
# Rules for testing
#===========================================

#------------------------------------
# Main Functions
#------------------------------------

# - - - - - - - - - - - - - - -
# Rules:
# - - - - - - - - - - - - - - -
# Possible make targets (to be make with ```make [xxx]```)
.PHONY : test_all test_lfm test_lfm_gui

# - - - - - - - - - - - - - - -
# Default
# - - - - - - - - - - - - - - -
# Go through full pipeline to make plots by default
test_all : test_lfm test_lfm_gui
.DEFAULT_GOAL := test_all


test_lfm:
	@echo "Testing LibrarianFileManager"
	cd test_librarian && $(MAKE) venv && $(MAKE) test_local && $(MAKE) clean_all

test_lfm_gui:
	@echo "Testing LibrarianFileManager GUI"
	cd test_librarian_gui && $(MAKE) venv && $(MAKE) test_local && $(MAKE) clean_all
