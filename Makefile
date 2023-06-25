venv_activate :=
system := $(shell uname -s)

# Set the virtual environment activation command based on the system type
ifeq ($(system),Darwin)  # Mac
	venv_activate := source venv/bin/activate
else ifeq ($(system),Linux)
	venv_activate := . venv/bin/activate
else
	$(error Unsupported operating system: $(system))
endif

setup:
	pip install pre-commit
	pre-commit install
	python -m venv venv
	$(venv_activate)

	pre-commit autoupdate

install:
	@ pip install --upgrade pip
	@ pip install -r requirements.txt

run:
	@python -m uvicorn app:app --port 1605

install-tests:
	@ python -m pip install -r requirements-test.txt

test:
	@pytest -p no:cacheprovider
	@echo "testing complete"

clean:
	@echo "cleaning"
	@find . -type d -name '.pytest_cache' -exec rm -rf {} +
	@find . -type d -name '.benchmarks' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +

.PHONY: run install clean setup test
