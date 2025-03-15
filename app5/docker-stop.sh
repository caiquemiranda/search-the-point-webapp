#!/bin/bash

echo "Parando Search-The-Point App..."

# Verificar qual comando do Docker Compose está disponível
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "ERRO: Docker Compose não encontrado."
    exit 1
fi

echo "Parando os contêineres..."
$COMPOSE_CMD down

echo
echo "Serviços parados com sucesso."
echo 