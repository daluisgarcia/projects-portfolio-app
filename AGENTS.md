# AGENT.md

## Project Context
**Project Name:** Projects Portfolio API
**Description:** A Django-based REST API that powers the portfolio website (daluisgarcia.github.io). It manages projects, technologies, and methodologies.

## Available skills
| Skill | Description | URL |
|-------|-------------|-----|
| `django` | Django framework for web development, including models, views, serializers, and admin interface. | [SKILL.md](skills/django/SKILL.md) |

## Auto-invoke Skills
When performing these actions, ALWAYS invoke the corresponding skill FIRST:
| Action | Skill |
|--------|-------|
| Adding DRF pagination or permissions | `django` |

## Technical Stack
- **Language:** Python 3.13
- **Frameworks:** Django 6.0+, Django Rest Framework (DRF) 3.16+
- **Database:** PostgreSQL 17 (Containerized)
- **Containerization:** Docker & Docker Compose
- **Dependency Management:** `uv` (for development), Docker for production.  `pyproject.toml` (PEP 621 standard)
- **WSGI Server:** Gunicorn (for production/docker)

## Project Structure
| Directory/File | Purpose |
|----------------|---------|
| `api/` | Django DRF views, serializers, and URLs |
| `app/` | Django Project configuration folder (`settings.py`, `urls.py`, `wsgi.py`) |
| `projects/` | Core Django app with models, admin, and business logic |
| `.dockerignore` | Docker ignore file to exclude unnecessary files from the Docker context |
| `.gitignore` | Git ignore file to exclude unnecessary files from version control |
| `.python-version` | Specifies the Python version for `uv` |
| `docker-compose.yml` | Docker Compose configuration for development and production |
| `Dockerfile` | Dockerfile for building the application image |
| `prepare-django-db.sh` | Shell script to prepare the Django database (migrations, collectstatic, superuser creation) when loading the container |
| `pyproject.toml` | Python project configuration and dependencies (PEP 621) |
| `README.md` | Project documentation and setup instructions |


### IGNORE THESE FILES (if exists)
| Directory/File | Reason to Ignore |
|----------------|------------------|
| `static/` | Contains collected static files, not relevant for development or code changes |
| `media/` | Contains uploaded media files, not relevant for development or code changes |
| `__pycache__/` | Python bytecode cache, not relevant for development or code changes |
| `.venv/` | Local virtual environment, not relevant for development or code changes |
| `postgresdata/` | Containerized database data, not relevant for development or code changes |
| `mysqldata/` | Containerized database data, not relevant for development or code changes |
| `uv.lock` | Lock file for `uv`, not relevant for development or code changes |

## Development Environment

### Running the Application
The project is designed to run via Docker Compose:
```bash
docker-compose up --build
```

### Database Setup
The database is initialized automatically via the `prepare-django-db.sh` script which:
1. Runs migrations (`migrate`)
2. Collects static files (`collectstatic`)
3. Creates a superuser if possible.

To access the database shell:
```bash
docker-compose exec app python manage.py dbshell
```

### Environment Variables
Configuration is handled via `django-environ`. A `.env` file is expected in the root directory (or environment variables set in `docker-compose.override.yml`).
Key variables:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_URL` (or split into `DATABASE_ENGINE`, `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`)
- `ALLOWED_HOSTS`
- `DJANGO_SUPERUSER_USERNAME` (for auto-creating superuser)
- `DJANGO_SUPERUSER_PASSWORD` (for auto-creating superuser)
- `DJANGO_SUPERUSER_EMAIL` (for auto-creating superuser)

## Common Tasks for Agents

### 1. Database Migrations
When modifying models in `projects/models.py`:
1. Create migration:
   ```bash
   docker-compose exec app python manage.py makemigrations
   ```
2. Apply migration:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

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

## Commit & Pull Request Guidelines

Follow conventional-commit style: `<type>(<scope>)/<ticket-number>: <description>`

**Types:** `feat`, `fix`, `docs`, `chore`, `perf`, `refactor`, `style`, `test`
**Scope:** `models`, `views`, `serializers`, `docker`, etc.
**Ticket Number:** ALWAYS ask for a ticket number from the project management tool (e.g., Jira, Trello) and include it in the commit message. DO NOT create commits without asking for a ticket number, the user will give you one or tell you it is not needed.

Before creating a PR:
1. Complete checklist in `.github/pull_request_template.md`
2. Run all relevant tests and linters
3. Link screenshots for UI changes