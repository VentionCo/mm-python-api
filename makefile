# ----------------------------------------------------------------------------
# Get branch and release information.
CURRENT_BRANCH = $(shell git branch | grep \* | cut -d ' ' -f2)
VERSION = $(shell cat version.txt)
RELEASE_BRANCH = release/${VERSION}

.PHONY: develop release

develop:
	@echo "Switching the branch develop..."
	@git pull
	@git checkout develop
	@echo Done - mm-python-api

release:
	@echo "Switching to branch " ${RELASE_BRANCH}
	@git pull
	@git checkoput ${RELEASE_BRANCH}
	@echo Done - mm-python-api

