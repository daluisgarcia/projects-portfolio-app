# AGENT.md

## Project Context
**Project Name:** Projects Portfolio
**Description:** A complete Django web application that powers the personal portfolio. It manages projects, professional experiences, and a markdown blog. Renders server-side templates with Django class-based views — there is no REST API layer.

## Available skills
| Skill | Description | URL |
|-------|-------------|-----|
| `django` | Django framework for web development, including models, class-based views, templates, and admin interface. | [SKILL.md](skills/django/SKILL.md) |
| `caveman` | Ultra-compressed communication mode. Cuts token usage ~75% by speaking like caveman while keeping full technical accuracy. Supports intensity levels: lite, full (default), ultra, wenyan-lite, wenyan-full, wenyan-ultra. | [SKILL.md](.agents/skills/caveman/SKILL.md) |
| `python-performance-optimization` | Profile and optimize Python code using cProfile, memory profilers, and performance best practices (including N+1 query detection). | [SKILL.md](.agents/skills/python-performance-optimization/SKILL.md) |
| `python-testing-patterns` | Implement comprehensive testing strategies with pytest, fixtures, mocking, and test-driven development. | [SKILL.md](.agents/skills/python-testing-patterns/SKILL.md) |
| `systematic-debugging` | Systematic root cause investigation before proposing fixes. Four-phase process: root cause → pattern analysis → hypothesis → implementation. | [SKILL.md](.agents/skills/systematic-debugging/SKILL.md) |

## Auto-invoke Skills
When performing these actions, ALWAYS invoke the corresponding skill FIRST:
| Action | Skill |
|--------|-------|
| ALWAYS use this skill unless the user specifies otherwise | `caveman` |
| Working with Django models, class-based views, templates, or the admin | `django` |
| Encountering any bug, test failure, or unexpected behavior | `systematic-debugging` |
| Debugging slow code, profiling, optimizing bottlenecks, or fixing N+1 queries | `python-performance-optimization` |
| Writing Python tests, setting up test suites, or implementing TDD | `python-testing-patterns` |

## Technical Stack
- **Language:** Python 3.13
- **Framework:** Django 6.0+ (class-based views, server-rendered templates — **no DRF**)
- **Database:** PostgreSQL 17 with pgvector extension (containerized via Docker; `pgvector/pgvector:pg17` image); SQLite is the default in dev (no vector support)
- **Vector store:** `pgvector` Python package + postgres `vector` extension (384-dim blog embeddings)
- **Frontend:** Django templates + Tailwind CSS (CDN) + custom CSS/JS in `static/`
- **Blog rendering:** `markdown` library (extensions: `fenced_code`, `tables`, `nl2br`)
- **Containerization:** Docker & Docker Compose
- **Dependency Management:** `uv` (PEP 621 `pyproject.toml`)
- **WSGI Server:** Gunicorn (production / Docker)

## Project Structure
| Directory/File | Purpose |
|----------------|---------|
| `app/` | Django project configuration (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`) |
| `projects/` | Landing page + projects gallery: models, CBVs, admin, templates |
| `experiences/` | Professional experiences timeline: models, CBVs, admin, templates |
| `blog/` | Markdown blog: models with auto-rendered HTML, paginated list CBV, detail CBV, admin, templates; `BlogPostEmbedding` for pgvector storage |
| `templates/` | Project-level templates (`base.html`, plus per-section subdirs: `projects/`, `experiences/`, `blog/`) |
| `static/` | Collected static files + custom CSS (`theme.css`, `base.css`, `icons.css`) and JS (`mobile-nav.js`, `tailwind-config.js`) |
| `media/` | User-uploaded media (project media files) |
| `DESIGN.md` | Design notes and architectural decisions |
| `.dockerignore` / `.gitignore` | Ignore rules for Docker / Git |
| `.python-version` | Python version for `uv` |
| `docker-compose.yaml` / `docker-compose.override.yaml` | Compose services (Postgres + Django app) |
| `Dockerfile` | Image build for the Django app |
| `prepare-django-db.sh` | Migrations + `collectstatic` + superuser bootstrap on container start |
| `pyproject.toml` | PEP 621 project config and dependencies |
| `README.md` | Project documentation and setup instructions |


### IGNORE THESE FILES (if exists)
| Directory/File | Reason to Ignore |
|----------------|------------------|
| `static/` | Contains collected static files, not relevant for development or code changes |
| `media/` | Contains uploaded media files, not relevant for development or code changes |
| `db.sqlite` | Local SQLite database file, not relevant for development or code changes |
| `__pycache__/` | Python bytecode cache, not relevant for development or code changes |
| `.venv/` | Local virtual environment, not relevant for development or code changes |
| `postgresdata/` | Containerized database data, not relevant for development or code changes |
| `mysqldata/` | Containerized database data, not relevant for development or code changes |
| `uv.lock` | Lock file for `uv`, not relevant for development or code changes |

## URL Routes
| Path | View | Purpose |
|------|------|---------|
| `/` | `LandingView` | Landing page (hero, pinned projects, latest blog highlights) |
| `/projects/` | `ProjectsView` | Projects gallery |
| `/experiences/` | `ExperienceListView` | Professional experiences timeline |
| `/blog/` | `BlogListView` | Blog index (paginated bento grid, category filter, AJAX load-more) |
| `/blog/<slug>/` | `BlogPostDetailView` | Single blog post |
| `/admin/` | Django admin | Content management (including `BlogPostEmbedding`) |

## Vector Embeddings

`BlogPostEmbedding` (`blog/models.py`) stores pgvector embeddings of blog posts for future semantic search / similarity queries.

- **Storage:** `VectorField(dimensions=384)` — sized for sentence-transformers `all-MiniLM-L6-v2` or compatible 384-dim embedders.
- **Relation:** `ForeignKey(BlogPost, on_delete=CASCADE, related_name="embeddings")` — deleting a post cascades to its embeddings.
- **Metadata:** `model_name` char field (default `"all-MiniLM-L6-v2"`) so multiple embedding models can coexist per post.
- **Constraint:** `unique_together = (post, model_name)` — same post + same model is unique; same post with different models is allowed. Lets you swap embedding providers without losing prior vectors.
- **Extension:** The `vector` postgres extension is enabled by `blog/migrations/0002_blogpostembedding.py` via `VectorExtension()`.
- **Backend requirement:** postgres only. The `BlogPostEmbeddingModelTests` test class is `@skipUnless(connection.vendor == "postgresql", ...)`-guarded and skips on SQLite. The `BlogPostEmbeddingAdminTests` class (admin-registration only) runs on any backend.
- **Not populated automatically** — embeddings must be inserted via Django admin, shell, management command, or external pipeline.

To run the postgres-only embedding tests:

```bash
docker-compose up --build -d
docker-compose exec app python manage.py test blog.tests.BlogPostEmbeddingModelTests -v 2
```

When adding similarity-search views or HNSW/IVFFlat indexes on the `embedding` column, follow the existing `select_related` / `prefetch_related` conventions in the views. Defer adding indexes until row count justifies the build cost (rule of thumb: >1k rows).

## Performance & Query Patterns
- Use `select_related` for ForeignKey access and `prefetch_related` for M2M / reverse FK in CBV `get_context_data` to avoid N+1 queries.
- Existing examples: `blog/views.py` (category FK + tags M2M + related_posts M2M) and `experiences/views.py` (skills M2M).
- New list CBVs should follow the same pattern. When in doubt, invoke the `python-performance-optimization` skill.

## Development Environment

### Running the Application
The project is designed to run via Docker Compose:
```bash
docker-compose up --build
```

### Database Setup
The database is initialized automatically via `prepare-django-db.sh` which:
1. Runs migrations (`migrate`)
2. Collects static files (`collectstatic`)
3. Creates a superuser from env vars if possible

To load the initial experiences fixture:
```bash
docker-compose exec app python manage.py loaddata experiences.fixtures.initial_experiences
```

To access the database shell:
```bash
docker-compose exec app python manage.py dbshell
```

### Environment Variables
Configuration is handled via `django-environ`. A `.env` file is expected in the root directory (or environment variables set in `docker-compose.override.yml`).
Key variables:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_ENGINE` (default: `sqlite3`), `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`
- `ALLOWED_HOSTS`
- `DJANGO_SUPERUSER_USERNAME` (for auto-creating superuser)
- `DJANGO_SUPERUSER_PASSWORD` (for auto-creating superuser)
- `DJANGO_SUPERUSER_EMAIL` (for auto-creating superuser)

## Common Tasks for Agents

### 1. Database Migrations
When modifying models in `projects/models.py`, `experiences/models.py`, or `blog/models.py`:
1. Create migration:
   ```bash
   docker-compose exec app python manage.py makemigrations
   ```
2. Apply migration:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

Note: the `blog.0002_blogpostembedding` migration runs `VectorExtension()` to enable the `vector` extension on postgres. The extension is enabled automatically on the postgres container — no manual `CREATE EXTENSION` is needed.

### 2. Running Tests
Run standard Django tests:
```bash
docker-compose exec app python manage.py test
```

### 3. Adding Dependencies
As we are using `uv` for dependency management, to add a new package:
```bash
uv add <package-name>
```
Then rebuild the Docker image to include the new dependency:
```bash
docker-compose up --build
```

### 4. Customizing Templates
- Project-level templates live in `templates/` (with `base.html` and per-section subdirs: `projects/`, `experiences/`, `blog/`).
- Per-app overrides go in `<app>/templates/<app>/...`.
- Tailwind is loaded via CDN in `base.html`; custom utilities are defined in `static/js/tailwind-config.js` and the theme lives in `static/css/theme.css`.

## Commit & Pull Request Guidelines

Follow conventional-commit style: `<type>(<scope>)/<ticket-number>: <description>`

**Types:** `feat`, `fix`, `docs`, `chore`, `perf`, `refactor`, `style`, `test`
**Scope:** `models`, `views`, `templates`, `static`, `docker`, etc.
**Ticket Number:** ALWAYS ask for a ticket number from the project management tool (e.g., Jira, Trello) and include it in the commit message. DO NOT create commits without asking for a ticket number, the user will give you one or tell you it is not needed.

Before creating a PR:
1. Complete checklist in `.github/pull_request_template.md`
2. Run all relevant tests and linters
3. Link screenshots for UI changes
