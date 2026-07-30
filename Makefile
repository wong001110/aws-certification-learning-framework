.PHONY: install validate freshness test lint check

install:
	python -m pip install --no-build-isolation -e '.[dev]'

validate:
	python -m validator.validate

freshness:
	python -m validator source-freshness --fail-on-stale

test:
	python -m pytest

lint:
	python -m ruff check validator tests

check: validate freshness test lint
