# Run all recipes
all: upgrade test format docs lint type_check autocomplete

# Execute the tests
test:
	uv run --isolated --python=3.10 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.11 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.12 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.13 pytest -m "not (slow or gui)"
	uv run --isolated --python=3.14 pytest -m "not (slow or gui)"

# Execute the quick tests
test_quick:
	uv run --isolated --python=3.12 pytest

# Install the dependencies (alias of upgrade)
install: upgrade

# Install the editable package based on the provided local file path
install_editable: install
	uv pip install --editable .

# Upgrade the dependencies
upgrade:
	uv sync --upgrade

# Upgrade the dependencies (alias of upgrade)
update: upgrade

# Build Python packages into source distributions and wheels
build:
	uv build

# Upload distributions to an index
publish:
	uv build
	uv publish

# Run ruff format
format:
	uv tool run ruff check --select I --fix .
	uv tool run ruff format

# Build the documentation
docs: docs_readme_patcher docs_sphinx

# Generate the README file using the readme-patcher
docs_readme_patcher:
	uv tool run --isolated --no-cache readme-patcher

# Generate the HTML documentation using Sphinx
docs_sphinx:
	rm -rf docs/_build
	uv tool run --isolated --from sphinx --with . --with sphinx_rtd_theme --with sphinx-argparse sphinx-build -W -q docs docs/_build
	xdg-open docs/_build/index.html

# Pin the requirements for readthedocs
pin_docs_requirements:
	rm -rf docs/requirements.txt
	uv tool run --from pip-tools pip-compile --strip-extras --output-file=docs/requirements.txt docs/requirements.in pyproject.toml

# Run ruff check
lint:
	uv tool run ruff check --fix

# Perform type checking using mypy
type_check:
	uv run mypy src/mscxyz tests

autocomplete:
	uv run musescore-manager --print-completion zsh > autocomplete.zsh
	uv run musescore-manager --print-completion bash > autocomplete.bash
	uv run musescore-manager --print-completion tcsh > autocomplete.tcsh

install_autocomplete: autocomplete
	cp autocomplete.zsh "$(HOME)/.zsh-completions/_musescore-manager"
