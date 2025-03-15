#!/bin/bash

echo "Reconstruindo contêineres do Search-The-Point App..."

# Verificar qual comando do Docker Compose está disponível
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "ERRO: Docker Compose não encontrado."
    exit 1
fi

echo "Parando contêineres existentes..."
$COMPOSE_CMD down

echo "Removendo imagens antigas..."
$COMPOSE_CMD rm -f

echo "Reconstruindo imagens..."
$COMPOSE_CMD build --no-cache

echo "Iniciando os contêineres..."
$COMPOSE_CMD up -d

echo
echo "Serviços reiniciados:"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo
echo "Para acessar de outra máquina, use o endereço IP deste computador."
echo "Para ver os logs, execute: $COMPOSE_CMD logs -f"
echo 