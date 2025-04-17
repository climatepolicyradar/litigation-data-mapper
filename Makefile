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

move_workflows:
	mv workflows .github/workflows

init: move_workflows share_trunk

add_venv_key:
	@echo "Adding venv key to [tool.pyright] section in pyproject.toml"
	@awk 'BEGIN { in_section=0 } \
	/^\[tool.pyright\]/ { in_section=1 } \
	in_section && /^\[.*\]/ && !/^\[tool.pyright\]/ { in_section=0 } \
	{ print } \
	in_section && !/^\[.*\]/ { last_line=NR } \
	END { if (last_line) { for (i=1; i<=NR; i++) { if (i == last_line) { print "venv = \"litigation-data-mapper\"" } } } }' pyproject.toml > tmpfile && mv tmpfile pyproject.toml
	@echo "Added venv key to [tool.pyright] section in pyproject.toml"

setup_with_pyenv: add_venv_key initialise_git
	-pyenv virtualenv 3.10 litigation-data-mapper
	trunk actions run configure-pyright
	sed -i 's;secrets.GITHUB_TOKEN;$$\{\{secrets.GITHUB_TOKEN}\};g' .github/workflows/ci-cd.yml
	sed -i 's;env.VERSION;$$\{\{env.VERSION\}\};g' .github/workflows/ci-cd.yml
	sed -i 's;needs.git.outputs.upload_url;$${\{needs.git.outputs.upload_url\}\};g' .github/workflows/ci-cd.yml

setup: setup_with_pyenv
	pyenv activate litigation-data-mapper
	poetry install
	make share_trunk

install_git_hooks: install_trunk
	trunk init
	trunk actions run configure-pyright

check:
	trunk fmt
	trunk check

initialise_git:
	git config --global init.defaultBranch main
	git init

build:
	docker build --tag litigation-data-mapper --platform="linux/amd64" .
