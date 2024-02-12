all: test autocomplete

test:
	poetry run tox

test_quick:
	poetry run tox -e quick,format,docs,lint

test_gui:
	poetry run pytest -m "gui"

test_all:
	poetry run pytest

install: update

# https://github.com/python-poetry/poetry/issues/34#issuecomment-1054626460
install_editable:
	pip install -e .

update:
	poetry lock
	poetry install

build:
	poetry build

publish:
	poetry build
	poetry publish

format:
	poetry run tox -e format

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html > /dev/null 2>&1

lint:
	poetry run tox -e lint

pin_docs_requirements:
	pip-compile --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

autocomplete:
	poetry run musescore-manager --print-completion zsh > autocomplete.zsh
	poetry run musescore-manager --print-completion bash > autocomplete.bash
	poetry run musescore-manager --print-completion tcsh > autocomplete.tcsh

install_autocomplete: autocomplete
	cp autocomplete.zsh "$(HOME)/.zsh-completions/_musescore-manager"

.PHONY: test test_real_binary install install_editable update build publish format docs lint pin_docs_requirements
