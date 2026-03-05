# Projects portfolio backend

This project is a REST API that allows to manage projects and their images. The project is developed with Django and Django Rest Framework. This API is being consumed by the [daluisgarcia.github.io](https://github.com/daluisgarcia/daluisgarcia.github.io) repository.

## Install dependencies

To install the dependencies, you can use the following command to install the dependencies in a virtual environment:
```bash
uv sync
```

## Run the project
 
To run the project, you can use the following command:
```bash
docker-compose up --build
```
If you are developing, you can use the following `docker-compose.override.yaml` file content to allow hot reloading and avoid having to rebuild the image every time you make a change:

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
