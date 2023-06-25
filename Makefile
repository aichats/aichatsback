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
	pip install virtualenv
	python -m venv venv
	$(venv_activate)
	pip install -r requirements-test.txt

#pre-commits:
#	pip install pre-commit
#	pre-commit install
#	pre-commit autoupdate

install:
	@ pip install --upgrade pip
	@ pip install -r requirements.txt

run:
	@python -m uvicorn app:app --port 80

dev:
	@python -m uvicorn app:app --reload --port 1605

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

docker:
	@echo "docker building"
	docker build . -t aichats
	docker run -p 80:1605  aichat

compose:
	docker-compose up --build --force-recreate


deploy:
	docker build -t laciferin/aichats .
	docker login -u laciferin
	docker push laciferin/aichats:latest


env:
	@[ -f .env ] && echo ".env file already exists. Appending"
	grep -v '^#' .env.example | cut -d '=' -f 1 | xargs -I {} bash -c 'echo "$1=${!1}"' _ {} >> .env

.PHONY: run install clean setup test run env deploy compose docker dev
