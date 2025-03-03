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

add_venv_key:
	@echo "Adding venv key to [tool.pyright] section in pyproject.toml"
	@awk 'BEGIN { in_section=0 } \
	/^\[tool.pyright\]/ { in_section=1 } \
	in_section && /^\[.*\]/ && !/^\[tool.pyright\]/ { in_section=0 } \
	{ print } \
	in_section && !/^\[.*\]/ { last_line=NR } \
	END { if (last_line) { for (i=1; i<=NR; i++) { if (i == last_line) { print "venv = \"data-mapper\"" } } } }' pyproject.toml > tmpfile && mv tmpfile pyproject.toml
	@echo "Added venv key to [tool.pyright] section in pyproject.toml"

setup_with_pyenv: add_venv_key
	pyenv virtualenv 3.10 data-mapper
	trunk actions run configure-pyright
	pyenv activate data-mapper
	poetry install

check:
	trunk fmt
	trunk check

