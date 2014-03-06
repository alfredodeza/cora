# Makefile for cora builds
#
MAKEFLAGS += -s
SHELL = bash

# You can set these variables from the command line.
SCRIPT_NAME   = cora
NAME          = cora
BUILDDIR      = bin

# Locations and files
BUILD_OUT     = $(BUILDDIR)/$(SCRIPT_NAME)

# Beautiful colours
NO_COLOR=\x1b[0m
OK_COLOR=\x1b[32;01m
GREEN = OK_COLOR
ERROR_COLOR=\x1b[31;01m
WARN_COLOR=\x1b[33;01m

OK_STRING=$(OK_COLOR)[OK]$(NO_COLOR)
ERROR_STRING=$(ERROR_COLOR)[ERRORS]$(NO_COLOR)
WARN_STRING=$(WARN_COLOR)[WARNINGS]$(NO_COLOR)

.PHONY: help clean compile init rmtmp

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  release    to make a cora release"
	@echo "  clean      remove build directory before creating release"

clean:
	-rm -rf $(BUILDDIR)/*

release: init rmtmp
	@echo
	echo -n "copying cora.sh file ..." && cp cora.sh $(BUILDDIR)/cora && echo -e "$(OK_STRING)";
	echo -n "add Python header to new cora file ..." && echo "python <<END" >> $(BUILDDIR)/cora && echo -e "$(OK_STRING)";
	echo -n "adding Python source to cora file ..." && tail -n +3 cora.py >> $(BUILDDIR)/cora && echo -e "$(OK_STRING)";
	echo -n "appending footer to new cora file ..." && echo "END" >> $(BUILDDIR)/cora && echo -e "$(OK_STRING)";
	echo -n "appending main functino to cora file ..." && echo "shell_cmd" >> $(BUILDDIR)/cora && echo -e "$(OK_STRING)";
	@echo
	@echo -e "$(OK_COLOR)Build finished. The cora executable is located in $(BUILD_OUT)$(NO_COLOR)"

rmtmp:
	@echo
	@echo removing temporary files...
	echo -n "removing pyc files... " && find . -type f -name "*.py[co]" -exec rm -f \{\} \; \
		&& echo -e "$(OK_STRING)"
	echo -n "removing __pycache__ files ... " && find . -type d -name "__pycache__" -exec rm -f \{\} \; \
		&& echo -e "$(OK_STRING)"
