# ----------------------------------------------------------------------------
# Get branch and release information.
CURRENT_BRANCH = $(shell git branch | grep \* | cut -d ' ' -f2)
VERSION = $(shell cat version.txt)
RELEASE_BRANCH = release/${VERSION}
CWD = $(shell pwd)
LIB_NAME = MachineMotion
P3_SITE = $(shell python3 -m site --user-site)
P2_SITE = $(shell python2 -m site --user-site)

.PHONY: all release install clean

all: install done

release: checkout-release done

# symlink to site packages.
install: clean
	ln -s $(CWD) $(P3_SITE)/$(LIB_NAME)
	ln -s $(CWD) $(P2_SITE)/$(LIB_NAME)

# clear old links.
clean:
	rm -f $(P3_SITE)/$(LIB_NAME)
	rm -f $(P2_SITE)/$(LIB_NAME)

# ----------------------------------------------------------------------------
# Branch management
checkout-release:
ifneq (${CURRENT_BRANCH},${RELEASE_BRANCH})
	@echo "Switching to branch ${RELASE_BRANCH}"
	@git pull
	@git checkout ${RELEASE_BRANCH}
	@echo Done - mm-python-api
endif

done:
	@echo Done - mm-python-api
