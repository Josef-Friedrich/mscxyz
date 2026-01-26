all: test format docs lint type_check

test:
	uv run --isolated --python=3.10 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.11 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.12 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.13 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.14 pytest -m "not (slow or gui)"

test_quick:
	uv run --isolated --python=3.12 pytest

install: update

install_editable: install
	uv pip install --editable .

update:
	uv sync --upgrade

upgrade: update

build:
	uv build

publish:
	uv build
	uv publish

format:
	uv run ruff check --select I --fix .
	uv run ruff format

docs:
# 	uv run --isolated readme-patcher
	rm -rf docs/_build
	uv tool run --isolated --from sphinx --with . --with sphinx_rtd_theme sphinx-build -W -q docs docs/_build
	xdg-open docs/_build/index.html

pin_docs_requirements:
	rm -rf docs/requirements.txt
	uv run pip-compile --strip-extras --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

lint:
	uv run ruff check

type_check:
	uv run mypy src/mscxyz tests

autocomplete:
	uv run musescore-manager --print-completion zsh > autocomplete.zsh
	uv run musescore-manager --print-completion bash > autocomplete.bash
	uv run musescore-manager --print-completion tcsh > autocomplete.tcsh

install_autocomplete: autocomplete
	cp autocomplete.zsh "$(HOME)/.zsh-completions/_musescore-manager"

.PHONY: test install install_editable update upgrade build publish format docs lint pin_docs_requirements
