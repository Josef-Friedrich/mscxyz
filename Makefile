test:
	poetry run tox

test_real_binary:
	pytest tests/_test_real-binary.py

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
	xdg-open docs/_build/index.html > /dev/null 2>&1

activate_venv:
	source .venv/bin/activate

.PHONY: test install install_editable update build publish docs
