#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ ! -f .env.example ]]; then
  printf 'Missing .env.example in %s\n' "$ROOT_DIR" >&2
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  printf 'Docker is required but was not found in PATH.\n' >&2
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE=(docker compose)
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE=(docker-compose)
else
  printf 'Docker Compose is required. Install the Docker Compose plugin or docker-compose.\n' >&2
  exit 1
fi

if [[ $# -gt 1 ]]; then
  printf 'Usage: ./init.sh [postgres-host-port]\n' >&2
  exit 1
fi

set_env_value() {
  local key="$1"
  local value="$2"
  local tmp_file

  tmp_file="$(mktemp)"
  while IFS= read -r line || [[ -n "$line" ]]; do
    if [[ "$line" == "$key="* ]]; then
      printf '%s=%s\n' "$key" "$value"
    else
      printf '%s\n' "$line"
    fi
  done < .env > "$tmp_file"
  mv "$tmp_file" .env
}

printf 'Regenerating .env from .env.example...\n'
cp .env.example .env

if [[ $# -eq 1 ]]; then
  POSTGRES_HOST_PORT="$1"
fi

if [[ -n "${POSTGRES_HOST_PORT:-}" ]]; then
  printf 'Using PostgreSQL host port %s...\n' "$POSTGRES_HOST_PORT"
  set_env_value POSTGRES_HOST_PORT "$POSTGRES_HOST_PORT"
  set_env_value POSTGRES_PORT "$POSTGRES_HOST_PORT"
fi

printf 'Stopping existing containers and removing project volumes...\n'
"${COMPOSE[@]}" down --volumes --remove-orphans

printf 'Building and starting the application...\n'
"${COMPOSE[@]}" up --build
