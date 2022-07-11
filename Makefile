all: test

build:
	rm -rf dist
	python3 setup.py sdist

doc:
	python setup.py build_sphinx

install:
	python setup.py install

develop:
	python setup.py develop

upload:
	pip3 install twine
	twine upload --skip-existing dist/*

readme:
	./_generate-readme.py

test:
	tox

.PHONY: all build doc install develop upload readme test
