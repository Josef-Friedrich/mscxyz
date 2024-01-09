all: test autocomplete

test:
	poetry run tox

test_real_binary:
	pytest -m only _test_real-binary.py

install:
	poetry install

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

activate_venv:
	source .venv/bin/activate

pin_docs_requirements:
	pip-compile --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

autocomplete:
	musescore-manager --print-completion zsh > autocomplete.zsh
	musescore-manager --print-completion bash > autocomplete.bash
	musescore-manager --print-completion tcsh > autocomplete.tcsh

install_autocomplete: autocomplete
	cp autocomplete.zsh "$(HOME)/.zsh-completions/_musescore-manager"

.PHONY: test test_real_binary install install_editable update build publish format docs lint activate_venv pin_docs_requirements
