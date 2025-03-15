#!/bin/bash

echo "Iniciando Search-The-Point App com Docker..."

# Verificar se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "ERRO: Docker não encontrado. Por favor, instale o Docker antes de continuar."
    exit 1
fi

# Verificar qual comando do Docker Compose está disponível
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "ERRO: Docker Compose não encontrado. Por favor, instale o Docker Compose."
    exit 1
fi

echo "Iniciando os contêineres..."
$COMPOSE_CMD up --build -d

echo
echo "Serviços iniciados:"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo
echo "Para acessar de outra máquina, use o endereço IP deste computador."
echo "Para parar os serviços, execute ./docker-stop.sh"
echo
echo "Pressione Ctrl+C para sair dos logs"
$COMPOSE_CMD logs -f 