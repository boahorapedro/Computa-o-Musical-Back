.PHONY: help up down restart logs build clean init-db test

help: ## Mostra este help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Inicia todos os serviços
	docker compose up -d

down: ## Para todos os serviços
	docker compose down

restart: ## Reinicia todos os serviços
	docker compose restart

logs: ## Mostra logs de todos os serviços
	docker compose logs -f

logs-api: ## Mostra logs da API
	docker compose logs -f api

logs-worker-cpu: ## Mostra logs do worker CPU
	docker compose logs -f worker-cpu

logs-worker-gpu: ## Mostra logs do worker GPU
	docker compose logs -f worker-gpu

build: ## Build das imagens Docker
	docker compose build

clean: ## Remove containers, volumes e imagens
	docker compose down -v --rmi all

init-db: ## Inicializa o banco de dados
	docker compose exec api python init_db.py

shell-api: ## Acessa shell do container da API
	docker compose exec api bash

shell-worker: ## Acessa shell do worker CPU
	docker compose exec worker-cpu bash

shell-db: ## Acessa PostgreSQL
	docker compose exec db psql -U postgres -d audiomixer

ps: ## Lista status dos containers
	docker compose ps

test: ## Executa testes
	docker compose exec api pytest tests/ -v

install: ## Instala dependências localmente
	pip install -r requirements.txt

format: ## Formata código com black
	black src/

lint: ## Verifica código com flake8
	flake8 src/

health: ## Verifica saúde da API
	curl http://localhost:8000/health

docs: ## Abre documentação da API
	@echo "Abrindo http://localhost:8000/docs"
	@xdg-open http://localhost:8000/docs 2>/dev/null || open http://localhost:8000/docs 2>/dev/null || echo "Acesse manualmente: http://localhost:8000/docs"

minio: ## Abre console do MinIO
	@echo "Abrindo http://localhost:9001"
	@xdg-open http://localhost:9001 2>/dev/null || open http://localhost:9001 2>/dev/null || echo "Acesse manualmente: http://localhost:9001 (minioadmin/minioadmin)"
