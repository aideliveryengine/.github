#!/usr/bin/env bash
# Registra o modelo "qwen3-4b" no Ollama.
#
# Com internet normal, o caminho curto é:
#   docker compose -f infra/docker-compose.yml exec ollama ollama pull qwen3:4b-instruct-2507-q4_K_M
#   (e use LLM_MODELO=ollama:qwen3:4b-instruct-2507-q4_K_M)
#
# Este script é o caminho usado na gravação, onde só o Docker Hub estava liberado:
# baixa o GGUF publicado como artefato OCI em hub.docker.com/r/ai/qwen3 e importa no Ollama.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p modelos

REPO=ai/qwen3
TAG=4b-instruct-2507-q4_K_M
ARQ=modelos/Qwen3-4B-Instruct-2507-Q4_K_M.gguf

if [ ! -f "$ARQ" ]; then
  TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:$REPO:pull" \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["token"])')
  DIGEST=$(curl -s -H "Authorization: Bearer $TOKEN" \
    -H 'Accept: application/vnd.oci.image.manifest.v1+json' \
    "https://registry-1.docker.io/v2/$REPO/manifests/$TAG" \
    | python3 -c 'import json,sys;print(json.load(sys.stdin)["layers"][0]["digest"])')
  curl -L -H "Authorization: Bearer $TOKEN" -o "$ARQ" "https://registry-1.docker.io/v2/$REPO/blobs/$DIGEST"
fi

echo "FROM /models/$(basename "$ARQ")" > modelos/Modelfile
docker compose -f docker-compose.yml exec ollama ollama create qwen3-4b -f /models/Modelfile
