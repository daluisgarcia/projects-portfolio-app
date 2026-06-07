# Projects Portfolio

A complete Django web application that powers the personal portfolio. It renders server-side templates for a landing page, a projects gallery, a professional experiences timeline, and a markdown-powered blog. Built with Django class-based views, `select_related` / `prefetch_related` for query efficiency, and Tailwind CSS for the UI.

For design notes and architectural decisions, see [`DESIGN.md`](./DESIGN.md).

## Features

- **Landing page** — Hero, pinned projects, and latest blog highlights.
- **Projects gallery** — Filterable by field, with media galleries, technologies, and methodology tags.
- **Experiences timeline** — Professional history with skill chips, accent styles, and a present/future date convention (`end_date` null renders as "Present").
- **Blog** — Markdown-rendered posts with categories, tags, related posts, featured posts, pagination, category filter, and an AJAX "load more" handler. Reading time is auto-computed from word count.
- **Django admin** — Full content management for all three apps.

## Tech Stack

- **Language:** Python 3.13
- **Framework:** Django 6.0+ (class-based views, server-rendered templates)
- **Database:** PostgreSQL 17 (containerized); SQLite is the default for local dev
- **Frontend:** Django templates + Tailwind CSS (CDN) + custom CSS/JS in `static/`
- **Blog rendering:** `markdown` library (with `fenced_code`, `tables`, `nl2br` extensions)
- **Dependency management:** `uv` (PEP 621 `pyproject.toml`)
- **WSGI server:** Gunicorn (production / Docker)
- **Containerization:** Docker & Docker Compose

## Install dependencies

```bash
uv sync
```

## Run the project

```bash
docker-compose up --build
```

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
| `blog/` | Markdown blog: models with auto-rendered HTML, paginated list CBV, detail CBV, admin, templates |
| `templates/` | Project-level templates (`base.html`, plus per-section subdirs: `projects/`, `experiences/`, `blog/`) |
| `static/` | Collected static files + custom CSS (`theme.css`, `base.css`, `icons.css`) and JS (`mobile-nav.js`, `tailwind-config.js`) |
| `media/` | User-uploaded media (project media files) |
| `DESIGN.md` | Design notes and architectural decisions |
| `Dockerfile` | Docker image for the Django app |
| `docker-compose.yaml` / `docker-compose.override.yaml` | Compose services (Postgres + Django app) |
| `prepare-django-db.sh` | Migrations + `collectstatic` + superuser bootstrap on container start |
| `pyproject.toml` | PEP 621 project config and dependencies |
| `README.md` | This file |

## Database

The database is initialized automatically by `prepare-django-db.sh`, which:
1. Runs migrations (`migrate`)
2. Collects static files (`collectstatic`)
3. Creates a superuser from env vars if possible

To load the initial experiences fixture:

```bash
docker-compose exec app python manage.py loaddata experiences.fixtures.initial_experiences
```

To open a database shell:

```bash
docker-compose exec app python manage.py dbshell
```

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
