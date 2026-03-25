.PHONY: up down build restart logs build-webapp zrok-reserve zrok-web zrok-api zrok-media help

# --- Docker Commands ---

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

restart:
	docker compose restart

logs:
	docker compose logs -f

# Specific fix for Next.js build args
build-webapp:
	docker compose build webapp
	docker compose up -d webapp

# --- Zrok Tunnel Commands ---

zrok-reserve:
	zrok reserve public --unique-name myweb26 http://localhost:3000
	zrok reserve public --unique-name myapi26 http://localhost:8000
	zrok reserve public --unique-name mymedia26 http://localhost:9000

# These block the terminal, run in separate windows
zrok-web:
	zrok share reserved myweb26

zrok-api:
	zrok share reserved myapi26

zrok-media:
	zrok share reserved mymedia26

# --- Help ---

help:
	@echo "Usage:"
	@echo "  make up             - Start containers"
	@echo "  make down           - Stop containers"
	@echo "  make build          - Build all containers"
	@echo "  make build-webapp   - Rebuild Next.js app with current env vars (CORS/API fix)"
	@echo "  make logs           - Show logs"
	@echo ""
	@echo "  make zrok-reserve   - One-time reservation of unique names"
	@echo "  make zrok-web       - Share WebApp tunnel (blocks terminal)"
	@echo "  make zrok-api       - Share API tunnel (blocks terminal)"
	@echo "  make zrok-media     - Share Media tunnel (blocks terminal)"
