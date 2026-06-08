# Makefile — common dev/test tasks for the projects-portfolio Django app.
#
# Quick start:
#   make up-bg     # start the stack in the background
#   make test      # run the full Django test suite
#   make help      # show this help
#
# All stack commands use `docker compose` (v2). To use the legacy v1
# `docker-compose` binary instead, override on the command line:
#   make up DC=docker-compose
# Or set it persistently in your shell:
#   export DC=docker-compose

# --- Config -----------------------------------------------------------------

# Docker compose command. Override with `make up DC=docker-compose` if needed.
DC ?= docker compose

# --- Default target ---------------------------------------------------------

.DEFAULT_GOAL := help

# --- Help -------------------------------------------------------------------

.PHONY: help
help:  ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# --- Stack ------------------------------------------------------------------

.PHONY: up
up:  ## start the stack in the foreground (auto-builds if needed)
	$(DC) up --build

.PHONY: up-bg
up-bg:  ## start the stack in detached mode
	$(DC) up -d --build

.PHONY: down
down:  ## stop the stack (keeps volumes; safe for dev)
	$(DC) down

.PHONY: down-v
down-v:  ## stop the stack AND drop all volumes (resets postgres data)
	$(DC) down -v

.PHONY: stop
stop:  ## stop the stack but keep containers and volumes (for quick restart with `make up-bg`)
	$(DC) stop

.PHONY: logs
logs:  ## tail logs for all services (Ctrl-C to exit)
	$(DC) logs -f

.PHONY: ps
ps:  ## list running services
	$(DC) ps

# --- Django (run inside the app container) ---------------------------------

.PHONY: migrate
migrate:  ## apply pending migrations
	$(DC) exec app python manage.py migrate

.PHONY: makemigrations
makemigrations:  ## generate new migrations after model changes
	$(DC) exec app python manage.py makemigrations

.PHONY: test
test:  ## run the full Django test suite (requires `make up-bg` first)
	$(DC) exec app python manage.py test

.PHONY: test-blog
test-blog:  ## run the blog app tests
	$(DC) exec app python manage.py test blog

.PHONY: test-embeddings
test-embeddings:  ## run the postgres-only BlogPostEmbedding tests (verbose)
	$(DC) exec app python manage.py test blog.tests.BlogPostEmbeddingModelTests -v 2

.PHONY: test-local
test-local:  ## run tests against local SQLite (no docker; pgvector tests skip)
	uv run python manage.py test

.PHONY: superuser
superuser:  ## create a Django superuser (interactive)
	$(DC) exec app python manage.py createsuperuser

.PHONY: shell
shell:  ## open a Django shell inside the app container
	$(DC) exec app python manage.py shell

.PHONY: dbshell
dbshell:  ## open a postgres shell
	$(DC) exec app python manage.py dbshell

# --- Python deps (local) ----------------------------------------------------

.PHONY: install
install:  ## install local Python deps via uv (sync with pyproject.toml)
	uv sync

.PHONY: add
add:  ## add a new Python dep via uv (usage: `make add PKG=pgvector`)
	uv add $(PKG)

# --- Cleanup ----------------------------------------------------------------

.PHONY: clean
clean: down-v  ## stop stack, drop volumes, remove __pycache__ and .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache
