#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Usage: $0 [dev | prod] ..."
  exit 1
fi

if [ $# -ge 1 ]; then
  if [ "$1" = "dev" ]; then
    docker compose --env-file .env.dev -f compose-dev.yaml build
  elif [ "$1" = "prod" ]; then
    docker compose --env-file .env -f compose.yaml build
  fi
fi

