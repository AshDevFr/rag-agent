# Self RAG

This project is an opinionated Self-RAG implementation used to search internal documentation first.

## env

Copy `.env.example` to `.env` and fill in the required variables

## development compose

`docker compose -f docker/dev/docker-compose.yml up`

## fetching data

`docker exec -it backend poetry run python fetch_and_ingest.py`
