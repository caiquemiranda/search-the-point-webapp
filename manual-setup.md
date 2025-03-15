# Configuração Manual do Search-The-Point Webapp

Se você estiver enfrentando problemas com os scripts automatizados, siga este guia para configurar manualmente a aplicação.

## 1. Instalar o Python

### Windows
1. Baixe o Python do [site oficial](https://www.python.org/downloads/)
2. Durante a instalação, marque a opção "Add Python to PATH"
3. Verifique a instalação abrindo o Prompt de Comando e digitando:
   ```
   python --version
   ```

### Linux/Mac
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Mac (com Homebrew)
brew install python3
```

## 2. Instalar o Node.js

### Windows
1. Baixe o Node.js do [site oficial](https://nodejs.org/)
2. Execute o instalador com as opções padrão
3. Verifique a instalação abrindo o Prompt de Comando e digitando:
   ```
   node --version
   npm --version
   ```

### Linux/Mac
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs

# Mac (com Homebrew)
brew install node
```

## 3. Configurar o Backend

```bash
# Navegue até a pasta do backend
cd backend

# Instale as dependências do Python
pip install -r ../requirements.txt

# Inicie o servidor
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

## 4. Configurar o Frontend

Abra uma nova janela de terminal e execute:

```bash
# Navegue até a pasta do frontend
cd frontend

# Instale as dependências do Node.js
npm install

# Inicie o servidor de desenvolvimento
npm start
```

## 5. Acessar a Aplicação

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Solução de Problemas

### "Python não foi encontrado"
- Certifique-se de que o Python está instalado e adicionado ao PATH
- Tente usar `python3` em vez de `python` em sistemas Linux/Mac

### "npm não foi encontrado"
- Certifique-se de que o Node.js está instalado corretamente
- Reinicie o computador após a instalação para atualizar as variáveis de ambiente

### Erro de conexão com o backend
- Verifique se o backend está rodando (deve mostrar algo como "Uvicorn running on http://0.0.0.0:8000")
- Abra o arquivo `.env` na pasta `frontend` e ajuste o `REACT_APP_API_URL` se necessário 