#!/bin/bash

echo "===== VERIFICANDO ACESSO AO BACKEND NO CODESPACE ====="

# Detectar nome do Codespace e construir URL
HOSTNAME=$(curl -s http://localhost:3000 2>&1 | grep -o 'automatic-space-engine[^"]*\.app\.github\.dev' | head -1)
if [ -z "$HOSTNAME" ]; then
  echo "Não foi possível detectar hostname do Codespace."
  exit 1
fi

BACKEND_URL=$(echo $HOSTNAME | sed 's/-3000/-8000/')
BACKEND_URL="https://$BACKEND_URL"

echo "URL do backend detectada: $BACKEND_URL"

# Verificar se o endpoint /health está respondendo
echo "Verificando endpoint de saúde..."
HEALTH_CHECK=$(curl -s "$BACKEND_URL/health" || echo "Falha")

if [[ "$HEALTH_CHECK" == *"online"* ]]; then
  echo "✅ Backend respondendo em $BACKEND_URL"
  echo "Resposta: $HEALTH_CHECK"
else
  echo "❌ Backend não está respondendo em $BACKEND_URL"
  
  # Verificar configuração CORS no backend
  echo "Verificando configuração CORS no backend..."
  docker exec search-the-point-backend grep -r "CORS" /app --include="*.py"
  
  echo "Configuração do backend:"
  docker exec search-the-point-backend cat /app/app/main.py | grep -A 10 CORSMiddleware
fi

# Verificando porta exposta no Codespace
echo "Verificando se a porta 8000 está exposta no Codespace..."
curl -s https://$HOSTNAME:8000/ > /dev/null
if [ $? -eq 0 ]; then
  echo "✅ Porta 8000 está exposta e respondendo"
else
  echo "❌ Porta 8000 não está respondendo"
  echo "Tente expor a porta 8000 no Codespace manualmente."
fi

# Instruções finais
echo ""
echo "Para corrigir problemas de CORS e comunicação:"
echo "1. Certifique-se de que a porta 8000 esteja exposta no Codespace"
echo "2. Reinicie os contêineres: docker-compose down && docker-compose up -d"
echo "3. Recarregue a página do frontend" 