#!/usr/bin/make

include .env

help:
	@echo "make"
	@echo "    install"
	@echo "        Install all packages of project locally."
	@echo "    install-venv"
	@echo "        Create virtual environment and install all packages of project locally."
	@echo "    run-dev"
	@echo "        Run development docker compose."
	@echo "    stop-dev"
	@echo "        Stop development docker compose."
	@echo "    run-prod"
	@echo "        Run production docker compose."
	@echo "    stop-prod"
	@echo "        Run production docker compose."
	@echo "    revision"
	@echo "        Add new database migration using alembic."
	@echo "    upgrade"
	@echo "        This helps to upgrade pending migrations."	
	@echo "    downgrade"
	@echo "        Undo latest alembic migration."
	@echo "    formatter"
	@echo "        Apply black formatting to code."

install-venv:
	python3 -m venv venv
	source /venv/bin/activate
	pip install -r src/requirements.txt

install:
	pip install -r src/requirements.txt

run-dev:
	sudo docker-compose -f docker-compose-dev.yml up --build

stop-dev:
	sudo docker-compose -f docker-compose-dev.yml down

run-prod:
	sudo docker-compose up --build

stop-prod:
	sudo docker-compose down

formatter:
	black .

upgrade:
	sudo docker-compose run fastapi_server alembic upgrade head

downgrade:
	sudo docker-compose run fastapi_server alembic downgrade -1

revision:	
	sudo docker-compose run fastapi_server alembic revision --autogenerate -m "$(msg)"