#!/bin/bash

echo "===== CORREÇÃO DE URL PARA CODESPACE ====="
echo "Este script irá ajustar a configuração para o ambiente Codespace"

# Obter a URL pública do codespace para o backend
BACKEND_PORT=8000
CODESPACE_URL=$(curl -s http://localhost:8090/2>&1 | grep -o 'https://[^"]*' | head -1 | sed "s/8090/$BACKEND_PORT/")

if [ -z "$CODESPACE_URL" ]; then
    echo "Não foi possível determinar automaticamente a URL do Codespace"
    echo "Digite a URL pública do seu backend Codespace (exemplo: https://nome-codespace-xxxx-8000.preview.app.github.dev):"
    read -r CODESPACE_URL
fi

echo "URL do backend detectada: $CODESPACE_URL"

# Criar arquivo .env para o frontend
echo "Criando arquivo de ambiente para o frontend..."
cat > frontend/.env <<EOF
REACT_APP_API_URL=$CODESPACE_URL
EOF

# Recriar os contêineres com a nova configuração
echo "Recriando contêineres com a nova configuração..."
docker-compose down
docker-compose up -d

echo ""
echo "Configuração atualizada! A aplicação agora deve usar a URL pública do Codespace."
echo "Frontend: http://localhost:3000"
echo "Backend: $CODESPACE_URL"
echo ""
echo "Se continuar tendo problemas, execute o script debug-codespace.sh para diagnóstico detalhado." 