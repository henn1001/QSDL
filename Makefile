SHELL = /bin/bash

.ONESHELL:

.PHONY: help setup lint test build release clean install

.DEFAULT_GOAL = help

BUMP = patch

help:
	@echo "make setup"
	@echo "       prepare the python environment"
	@echo "make lint"
	@echo "       runs pylint"
	@echo "make test"
	@echo "       runs pytest with coverage report"
	@echo "make build"
	@echo "       builds wheel and sdist package"
	@echo "make release"
	@echo "       realeases the package by bumping the version"
	@echo "       optionaly variable BUMP=major|minor|patch"
	@echo "       defaults to patch"
	@echo "make clean"
	@echo "       cleans outputs and pycache"
	@echo "make install"
	@echo "       installs this package to current python environment"

setup:
	@echo "setup..."
	@poetry install

lint: 
	@echo "linting..."
	@poetry run pylint qsdl || true

test:
	@echo "building..."
	@poetry run pytest

build:
	@echo "building..."
	@poetry build

release: 
	@echo "releasing..."
	@poetry version ${BUMP}
	@export VERSION=$$(poetry version | grep -Po "(\d*\.\d*\.\d*)$$")
	@perl -pi -e 's/(__version__\s=\s"\d*\.\d*\.\d*")/__version__ = "$$ENV{VERSION}"/' qsdl/__init__.py
	@git add -A
	@git commit -m "bump version to $$VERSION"
	@git tag v$$VERSION

install:
	@echo "installing..."
	@pip install .

clean:
	@echo "cleaning..."
	@rm -rf .pytest_cache/
	@rm -rf srcgen/
	@rm -rf dist/
	@rm -rf .coverage
	@find qsdl | grep -E "(__pycache__$$)" | xargs rm -rf
	@find tests | grep -E "(__pycache__$$)" | xargs rm -rf