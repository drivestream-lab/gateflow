.PHONY: setup check check-ci format format-check lint lint-check types layers test run run-api run-worker

setup:
	@bash scripts/setup_dev.sh

check: format lint types layers

check-ci: format-check lint-check types layers

format:
	.venv/bin/black --line-length 100 src/ tests/

format-check:
	.venv/bin/black --check --line-length 100 src/ tests/

lint:
	.venv/bin/ruff check --fix src/ tests/

lint-check:
	.venv/bin/ruff check src/ tests/

types:
	.venv/bin/pyright

layers:
	.venv/bin/lint-imports

test:
	.venv/bin/pytest tests/unit/ -v

# ADR-001: API + worker. Use this for local verify (wave-start needs a claimer).
run:
	@bash scripts/run_local.sh

run-api:
	.venv/bin/python -m src.main

run-worker:
	.venv/bin/python -m src.worker_main
