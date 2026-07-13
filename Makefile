SHELL := /bin/sh

install:
	cd apps/web && npm install
	cd apps/api && python -m pip install -e .[dev]

dev:
	docker compose up --build

up:
	docker compose up -d --build

down:
	docker compose down -v

lint:
	cd apps/web && npm run lint
	cd apps/api && ruff check app tests

typecheck:
	cd apps/web && npm run typecheck
	cd apps/api && mypy app

test:
	cd apps/api && pytest
	cd apps/web && npm run test

migrate:
	cd apps/api && alembic upgrade head

seed:
	cd apps/api && python -m app.scripts.seed_demo

train:
	cd apps/api && python ../../intelligence/training/train_models.py

evaluate:
	cd apps/api && python ../../intelligence/training/evaluate_models.py

e2e:
	cd apps/web && npm run test:e2e

build:
	cd apps/web && npm run build
