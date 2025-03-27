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
docker exec search-the-point-frontend curl -s backend:8000/health

if [ $? -eq 0 ]; then
  echo "Conexão bem-sucedida! O frontend pode acessar o backend."
else
  echo "Falha na conexão: O frontend não consegue acessar o backend."
  echo "Verifique as configurações de rede e a variável REACT_APP_API_URL."
fi

# Verificar a variável de ambiente no frontend
echo "Verificando a configuração da API no frontend..."
docker exec search-the-point-frontend sh -c "echo \$REACT_APP_API_URL"

echo "Teste concluído." 