test:
	poetry run tox

install:
	poetry install

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

docs:
	poetry run tox -e docs
	xdg-open docs/_build/index.html

.PHONY: test install install_editable update build publish docs
