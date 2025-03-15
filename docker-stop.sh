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
echo "Removendo contêineres parados..."
docker container prune -f

echo
echo "Removendo imagens não utilizadas..."
docker image prune -af

echo
echo "Limpando o cache do sistema Docker..."
docker system prune -f --volumes

echo
echo "Serviços parados e sistema limpo com sucesso."
echo "Todas as imagens, contêineres e cache foram removidos."
echo
echo "Para iniciar novamente, use ./docker-start.sh ou ./docker-rebuild.sh"
echo 