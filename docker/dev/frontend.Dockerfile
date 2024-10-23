FROM node:20-alpine

RUN apk update && \
  apk upgrade --no-cache && \
  apk add --no-cache build-base

WORKDIR /app

COPY web/package.json web/package-lock.json /app/

RUN npm install
