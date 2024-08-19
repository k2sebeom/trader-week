# Define variables
PYTHON := python

# Define directories
SRC_DIR := api app core main.py dev.py
TEST_DIR := tests

# Define linting tools
FLAKE8 := flake8
BLACK := black
MYPY := mypy

# Define testing tool
PYTEST := python -m pytest

# Run tests
test:
	$(PYTEST) $(TEST_DIR)

# Lint code using flake8
lint-flake8:
	$(FLAKE8) $(SRC_DIR) $(TEST_DIR)
# Lint code using mypy
lint-mypy:
	$(MYPY) $(SRC_DIR) $(TEST_DIR)

# Format code using black
format:
	$(BLACK) $(SRC_DIR) $(TEST_DIR)

# Check code formatting using black
check-format:
	$(BLACK) --check $(SRC_DIR) $(TEST_DIR)

# Combine linting and formatting
lint: lint-flake8 lint-mypy check-format

# Combine all checks
check: lint test

.PHONY: test lint-flake8 format check-format lint check
