FROM python:3.12

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip

# Install poetry
RUN pip install poetry

COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-root --only main --no-interaction --no-ansi

RUN mkdir -p web/dist
