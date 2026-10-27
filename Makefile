# Uses the `docker compose` plugin when present, otherwise standalone `docker-compose`.
COMPOSE ?= $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo docker-compose)
LLM_MODEL ?= qwen2.5-coder:7b

.DEFAULT_GOAL := help
.PHONY: help install up up-observability down logs model pipeline test test-py test-web lint eval

help: ## Show available targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-18s %s\n", $$1, $$2}'

install: ## Install Python (uv) and web (npm) dependencies
	uv sync
	cd web && npm ci

up: ## Start api, web and ollama with Docker Compose
	$(COMPOSE) up -d --build --wait api web ollama

up-observability: ## Start everything including Langfuse
	$(COMPOSE) --profile observability up -d --build --wait

down: ## Stop all services
	$(COMPOSE) --profile observability down

logs: ## Follow service logs
	$(COMPOSE) logs -f

model: ## Pull the default LLM into the ollama container
	$(COMPOSE) exec ollama ollama pull $(LLM_MODEL)

pipeline: ## Run ingestion + dbt build
	@echo "make pipeline is implemented in milestone 2" && exit 1

test: test-py test-web ## Run all unit tests

test-py:
	uv run pytest

test-web:
	cd web && npm test

lint: ## ruff + mypy + eslint + tsc
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy .
	cd web && npm run lint && npm run typecheck

eval: ## Run the eval benchmark
	@echo "make eval is implemented in milestone 7" && exit 1
