install_trunk:
	$(eval trunk_installed=$(shell trunk --version > /dev/null 2>&1 ; echo $$? ))
ifneq (${trunk_installed},0)
	$(eval OS_NAME=$(shell uname -s | tr A-Z a-z))
	curl https://get.trunk.io -fsSL | bash
endif

uninstall_trunk:
	sudo rm -if `which trunk`
	rm -ifr ${HOME}/.cache/trunk

share_trunk:
	trunk init

setup:
	uv sync

replace_repo_name:
	sed -i 's/REPO_NAME_PLACEHOLDER/litigation-data-mapper/g' .github/workflows/ci-cd.yml

initial_setup: initialise_git replace_repo_name setup_with_uv
	make share_trunk

install_git_hooks: install_trunk
	trunk init

check:
	trunk fmt
	trunk check

initialise_git:
	git config --global init.defaultBranch main
	git init

build:
	docker build --tag litigation-data-mapper --platform="linux/amd64" .
