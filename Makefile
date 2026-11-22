SHELL := /usr/bin/env bash
UV ?= uv
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show the help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install project dependencies with uv
	$(UV) sync

.PHONY: format
format: ## Format code with ruff
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

.PHONY: lint
lint: ## Run linting checks (ruff)
	$(UV) run ruff check --output-format=concise .
	$(UV) run ruff format --check --diff .

.PHONY: type-check
type-check: ## Run type checking (mypy)
	$(UV) run mypy . --strict

.PHONY: unit
unit: ## Run unit tests with pytest
	$(UV) run pytest

.PHONY: package
package: ## Check package dependencies
	$(UV) pip check

.PHONY: pre
pre: ## Run pre-commit checks with prek
	$(UV) run prek run --all-files

.PHONY: docs
docs: ## Serve documentation locally
	$(UV) run mkdocs serve

.PHONY: test
test: lint type-check unit package ## Run all checks (lint, type-check, unit, package)
