# Experience Fixtures

## What's in here

- `initial_experiences.json` — three example experience rows matching the
  static mockup at `templates-example/experiences.html`:
    1. "Data Science & ML Engineer" @ Neural Nexus Systems, Jan 2022 → Present (PRIMARY accent)
    2. "Senior Backend Developer" @ CloudArch Solutions, Mar 2019 → Dec 2022 (TERTIARY accent)
    3. "Software Developer" @ InnoBase Tech, Jan 2017 → Dec 2019 (OUTLINE accent)

  Each row references 4-5 `projects.Technology` rows by **natural key** (the
  Technology's `name` field, looked up via `Technology.natural_key()`).

## ⚠️ Load ORDER is critical

`loaddata` resolves M2M references using `natural_key()` lookups. The
referenced `Technology` rows must exist **before** you load this fixture.

### Recommended load sequence (fresh install)

```bash
# 1. Create Technology rows (one-time setup). Use admin at /admin/projects/technology/add/
#    or seed via a separate fixture. Required names (from the mockup):
#
#    PyTorch, Python, Kubernetes, TensorFlow, SQL,        # for role 1
#    Go, Ruby, Kafka, Redis, AWS,                          # for role 2
#    REST APIs, SQL Server, Java, Docker                   # for role 3
#
# 2. Load the experiences:
.venv/bin/python manage.py loaddata initial_experiences
```

### If a Technology is missing

If you run `loaddata` without all referenced `Technology` rows present, the
loader will raise a `DeserializationError` listing the missing name and
abort. The only safe workaround is to create the missing `Technology`
row in admin first and re-run.

**Note**: Django's `--ignorenonexistent` flag only suppresses errors for
*missing models/tables* (models not in `INSTALLED_APPS`), not for missing
*instances* of existing models. So `--ignorenonexistent` does NOT rescue
you from a missing `Technology` row — the natural-key lookup will still
raise. Create the Technology first, then load.

  ```bash
  # 1. Create missing Technology rows in /admin/projects/technology/add/
  # 2. Then:
  .venv/bin/python manage.py loaddata initial_experiences
  ```

## NEVER auto-load in production

`prepare-django-db.sh` is intentionally NOT modified to load this fixture.
Loading demo data into a production database would clobber owner-entered
content. Run `loaddata` manually, only in dev/staging.

## Editing the fixture

Re-export via:
```bash
.venv/bin/python manage.py dumpdata experiences.Experience --indent 2 --natural-foreign --natural-primary > experiences/fixtures/initial_experiences.json
```

The `--natural-foreign` flag ensures M2M skill references serialize as
`[["<Technology name>"]]` (using `natural_key()`) rather than as primary keys.
