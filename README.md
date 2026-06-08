# Projects Portfolio

A complete Django web application that powers the personal portfolio. It renders server-side templates for a landing page, a projects gallery, a professional experiences timeline, and a markdown-powered blog. Built with Django class-based views, `select_related` / `prefetch_related` for query efficiency, and Tailwind CSS for the UI.

For design notes and architectural decisions, see [`DESIGN.md`](./DESIGN.md).

## Quick start

The whole project is driven by a single `Makefile`. Run `make help` to list all targets. The essentials:

```bash
make install   # one-time: install Python deps via uv
make up-bg     # start the stack in the background (postgres + django app)
make test      # run the full Django test suite
make logs      # tail logs (Ctrl-C to exit)
make down      # stop the stack (keeps data)
```

Visit http://localhost:8000 after `make up-bg`. Run `make help` any time to see the full target list.

## Features

- **Landing page** — Hero, pinned projects, and latest blog highlights.
- **Projects gallery** — Filterable by field, with media galleries, technologies, and methodology tags.
- **Experiences timeline** — Professional history with skill chips, accent styles, and a present/future date convention (`end_date` null renders as "Present").
- **Blog** — Markdown-rendered posts with categories, tags, related posts, featured posts, pagination, category filter, and an AJAX "load more" handler. Reading time is auto-computed from word count.
- **Vector embeddings** — `BlogPostEmbedding` stores 384-dim pgvector vectors of blog posts (default model `all-MiniLM-L6-v2`) for future semantic search / similarity queries. Postgres-only.
- **Django admin** — Full content management for all three apps.

## Tech Stack

- **Language:** Python 3.13
- **Framework:** Django 6.0+ (class-based views, server-rendered templates)
- **Database:** PostgreSQL 17 with pgvector extension (containerized; `pgvector/pgvector:pg17` image); SQLite is the default for local dev (no vector support)
- **Vector store:** `pgvector` Python package + postgres `vector` extension (384-dim blog embeddings)
- **Frontend:** Django templates + Tailwind CSS (CDN) + custom CSS/JS in `static/`
- **Blog rendering:** `markdown` library (with `fenced_code`, `tables`, `nl2br` extensions)
- **Dependency management:** `uv` (PEP 621 `pyproject.toml`)
- **WSGI server:** Gunicorn (production / Docker)
- **Containerization:** Docker & Docker Compose
- **Task runner:** `Makefile` — see `make help`

## Install dependencies

The Makefile wraps `uv sync`:

```bash
make install
```

To do it by hand (without the Makefile), use `uv sync` directly:

```bash
uv sync
```

## Run the project

The Makefile wraps `docker compose up`:

```bash
make up-bg      # detached (recommended)
# or
make up         # foreground with live log streaming
```

The Makefile uses `docker compose` v2 by default. To use the legacy v1 `docker-compose` binary instead, set `DC=docker-compose` (e.g. `DC=docker-compose make up-bg`).

If you are developing, you can use the following `docker-compose.override.yaml` content to allow hot reloading and avoid having to rebuild the image every time you make a change:

```yaml
services:
    app:
        volumes:
            - .:/app/
        environment:
            - DEBUG=True
            - SECRET_KEY=""
            - ALLOWED_HOSTS=*
            - DJANGO_SUPERUSER_PASSWORD=adminpassword
            - DJANGO_SUPERUSER_USERNAME=admin
            - DJANGO_SUPERUSER_EMAIL=admin@admin.com
```

## Project Structure

| Directory/File | Purpose |
|----------------|---------|
| `app/` | Django project config (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`) |
| `projects/` | Landing page + projects gallery: models, CBVs, admin, templates |
| `experiences/` | Professional experiences timeline: models, CBVs, admin, fixtures, templates |
| `blog/` | Markdown blog: models with auto-rendered HTML, paginated list CBV, detail CBV, admin, templates, plus `BlogPostEmbedding` for pgvector storage |
| `templates/` | Project-level templates (`base.html`, plus per-section subdirs: `projects/`, `experiences/`, `blog/`) |
| `static/` | Collected static files + custom CSS (`theme.css`, `base.css`, `icons.css`) and JS (`mobile-nav.js`, `tailwind-config.js`) |
| `media/` | User-uploaded media (project media files) |
| `DESIGN.md` | Design notes and architectural decisions |
| `Dockerfile` | Docker image for the Django app |
| `docker-compose.yaml` / `docker-compose.override.yaml` | Compose services (Postgres + Django app) |
| `prepare-django-db.sh` | Migrations + `collectstatic` + superuser bootstrap on container start |
| `pyproject.toml` | PEP 621 project config and dependencies |
| `Makefile` | Common dev/test task runner (`make help` to list all targets) |
| `README.md` | This file |

## Database

The `portfolio-db` service runs on the `pgvector/pgvector:pg17` image — same env vars (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) as plain postgres, plus the `vector` extension. The extension is enabled automatically by the `blog.0002_blogpostembedding` migration via `VectorExtension()`.

The database is initialized automatically by `prepare-django-db.sh`, which:
1. Runs migrations (`migrate`)
2. Collects static files (`collectstatic`)
3. Creates a superuser from env vars if possible

To open a database shell:

```bash
make dbshell
```

## Vector Embeddings

`BlogPostEmbedding` (`blog/models.py`) stores 384-dim pgvector vectors of blog posts for future semantic search / similarity queries.

- **Storage:** `VectorField(dimensions=384)` — sized for sentence-transformers `all-MiniLM-L6-v2` or compatible 384-dim embedders.
- **Relation:** `ForeignKey(BlogPost, on_delete=CASCADE, related_name="embeddings")` — deleting a post cascades to its embeddings.
- **Metadata:** `model_name` char field (default `"all-MiniLM-L6-v2"`) so multiple embedding models can coexist per post. `unique_together = (post, model_name)` allows swapping the embedding provider later without losing prior vectors.
- **Backend requirement:** postgres only — the `vector` column type and the extension are not available on SQLite. Run `make test-blog` against the docker stack to exercise the embedding model tests.
- **Not populated automatically** — embeddings must be inserted via Django admin, shell, management command, or external pipeline.

## Environment Variables

Configuration is handled via `django-environ`. A `.env` file is expected at the project root (or env vars set in `docker-compose.override.yaml`).

Key variables:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_ENGINE` (default: `sqlite3`), `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`
- `ALLOWED_HOSTS`
- `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_PASSWORD` / `DJANGO_SUPERUSER_EMAIL` (auto superuser creation)

## Design

For design decisions and architectural notes, see [`DESIGN.md`](./DESIGN.md).
