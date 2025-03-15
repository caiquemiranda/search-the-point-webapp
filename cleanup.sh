#!/bin/bash

echo "Removendo aplicativos antigos..."

# Confirmar com o usuário
read -p "Tem certeza que deseja remover os aplicativos antigos (app1, app2, app3, app4)? (S/N): " CONFIRM

if [[ $CONFIRM != [Ss]* ]]; then
    echo "Operação cancelada pelo usuário."
    exit 0
fi

# Remover pastas antigas
if [ -d "app1" ]; then
    echo "Removendo app1..."
    rm -rf app1
fi

if [ -d "app2" ]; then
    echo "Removendo app2..."
    rm -rf app2
fi

if [ -d "app3" ]; then
    echo "Removendo app3..."
    rm -rf app3
fi

if [ -d "app4" ]; then
    echo "Removendo app4..."
    rm -rf app4
fi

# Remover pasta .streamlit se existir
if [ -d ".streamlit" ]; then
    echo "Removendo pasta .streamlit..."
    rm -rf .streamlit
fi

echo
echo "Limpeza concluída. Apenas o app5 permanece no projeto."
echo 