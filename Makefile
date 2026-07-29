.PHONY: install validate test lint check

install:
	python -m pip install --no-build-isolation -e '.[dev]'

validate:
	python -m validator.validate

test:
	python -m pytest

lint:
	python -m ruff check validator tests

check: validate test lint
