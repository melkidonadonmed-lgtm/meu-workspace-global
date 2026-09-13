#!/usr/bin/env bash
# Script auxiliar de setup inicial
set -e

echo "==> Configurando ambiente do projeto..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> .env criado a partir de .env.example"
fi

echo "==> Setup concluído!"
