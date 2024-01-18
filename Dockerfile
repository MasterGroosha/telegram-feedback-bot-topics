FROM python:3.11-alpine

WORKDIR /app

RUN pip install --upgrade pip

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt --no-cache-dir

COPY ./bot ./bot
COPY ./alembic ./alembic
COPY alembic.ini .
COPY settings.prod.yml ./settings.yml

ENTRYPOINT ["python", "-m", "bot"]
