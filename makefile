# ----------------------------------------------------------------------------
# Get branch and release information.
CURRENT_BRANCH = $(shell git branch | grep \* | cut -d ' ' -f2)
VERSION = $(shell cat version.txt)
RELEASE_BRANCH = release/${VERSION}

.PHONY: all develop release

all: done
	
develop: checkout-develop done

release: checkout-release done

# ----------------------------------------------------------------------------
# Branch management
checkout-develop:
ifneq (${CURRENT_BRANCH},develop)
	@echo "Switching to branch develop..."
	@git pull
	@git checkout develop
	@echo Done - mm-python-api
endif

checkout-release:
ifneq (${CURRENT_BRANCH},${RELEASE_BRANCH})
	@echo "Switching to branch ${RELASE_BRANCH}"
	@git pull
	@git checkout ${RELEASE_BRANCH}
	@echo Done - mm-python-api
endif

done:
	@echo Done - mm-python-api

