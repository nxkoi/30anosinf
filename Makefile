.PHONY: setup up down logs migrate test seed status verify build

# Se "permission denied" no docker.sock, abra um novo login ou use: sg docker -c 'make up'
COMPOSE=docker compose

setup:
	@test -f .env || cp .env.example .env
	@echo "Edite o .env (senhas e REVIEW_PASSWORD_HASH)."
	@echo "Gerar hash: docker run --rm caddy:2.9-alpine caddy hash-password --plaintext 'sua-senha'"
	@echo "No .env, escape cada \$$ do hash como \$$\$$ (docker compose)."

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d --build
	@$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(COMPOSE) exec api alembic upgrade head

seed:
	$(COMPOSE) exec api python -m scripts.seed

test:
	$(COMPOSE) exec api pytest -q /app/tests/api

status:
	$(COMPOSE) ps
	@curl -sf http://127.0.0.1/api/health | head -c 200; echo

verify:
	./scripts/verify.sh
