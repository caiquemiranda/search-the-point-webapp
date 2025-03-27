#!/bin/bash

echo "Testando conexão entre frontend e backend..."

# Verifica se os contêineres estão rodando
echo "Verificando contêineres..."
docker ps | grep search-the-point-backend
backend_status=$?
docker ps | grep search-the-point-frontend
frontend_status=$?

if [ $backend_status -ne 0 ] || [ $frontend_status -ne 0 ]; then
  echo "Erro: Nem todos os contêineres estão em execução"
  exit 1
fi

echo "Ambos os contêineres estão rodando"

# Tenta acessar a API de saúde do backend a partir do contêiner frontend
echo "Tentando acessar backend a partir do frontend..."
docker exec search-the-point-frontend wget -O- -q backend:8000/health || echo "Falha ao usar wget, tentando com busybox wget..."

# Tenta com busybox wget se o wget normal falhar
if [ $? -ne 0 ]; then
  docker exec search-the-point-frontend busybox wget -O- -q backend:8000/health
fi

if [ $? -ne 0 ]; then
  echo "Falha na conexão: O frontend não consegue acessar o backend."
  echo "Verifique as configurações de rede e a variável REACT_APP_API_URL."
else
  echo "Conexão bem-sucedida! O frontend pode acessar o backend."
fi

# Verificando a configuração da API no frontend
echo "Verificando a configuração da API no frontend..."
docker exec search-the-point-frontend sh -c "grep -r 'REACT_APP_API_URL' /app/.env || echo \$REACT_APP_API_URL"

echo "Teste concluído." 