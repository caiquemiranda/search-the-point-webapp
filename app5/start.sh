#!/bin/bash

echo "Iniciando Search-The-Point App..."

# Configurar o endereço IP do servidor
SERVER_IP="0.0.0.0"
BACKEND_PORT=8000
FRONTEND_PORT=3000

# Verificar qual comando Python está disponível
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "ERRO: Python não encontrado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Verificar se o Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "ERRO: Node.js não encontrado. Por favor, instale o Node.js antes de continuar."
    exit 1
fi

echo "Verificando dependências do Python..."
$PYTHON_CMD -m pip install fastapi uvicorn python-multipart pymupdf sqlalchemy pydantic -q

# Salvar o diretório atual para poder voltar a ele
CURRENT_DIR=$(pwd)

echo "Verificando dependências do Node.js..."
cd "$CURRENT_DIR/frontend"
if [ ! -d "node_modules" ]; then
    echo "Instalando pacotes npm (isso pode demorar um pouco)..."
    npm install
fi

echo "Iniciando o backend..."
cd "$CURRENT_DIR/backend" && $PYTHON_CMD -m uvicorn app:app --host $SERVER_IP --port $BACKEND_PORT --reload &
BACKEND_PID=$!

echo "Aguardando o backend iniciar..."
sleep 5

echo "Iniciando o frontend..."
cd "$CURRENT_DIR/frontend" && npm start &
FRONTEND_PID=$!

echo 
echo "Serviços iniciados:"
echo "- Backend: http://$SERVER_IP:$BACKEND_PORT"
echo "- Frontend: http://localhost:$FRONTEND_PORT"
echo
echo "Para acessar de outra máquina, use o endereço IP deste computador."
echo "Pressione Ctrl+C para encerrar todos os serviços..."

# Função para limpar processos ao encerrar
cleanup() {
    echo "Encerrando serviços..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit 0
}

# Capturar Ctrl+C para encerrar corretamente
trap cleanup SIGINT

# Manter o script em execução
wait 