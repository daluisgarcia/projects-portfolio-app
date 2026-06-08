FROM python:3.13-slim as builder

ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random

RUN apt-get update && \ 
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir . gunicorn

COPY . /app/

RUN chmod +x /app/prepare-django-db.sh

ENTRYPOINT ["sh", "/app/prepare-django-db.sh"]

CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]
