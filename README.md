# Search-The-Point Webapp

Esta aplicação permite visualizar documentos PDF, adicionar coordenadas em pontos específicos das páginas e exportar essas anotações.

## Estrutura do Projeto

O projeto está organizado em duas partes principais:

```
app5/
├── backend/             # Servidor FastAPI
│   ├── app.py           # API principal
│   ├── coordinates.db   # Banco de dados SQLite
│   ├── reset_db.py      # Script para resetar o banco de dados
│   └── uploads/         # Pasta para arquivos enviados
│
└── frontend/            # Aplicação React
    ├── public/          # Arquivos estáticos
    ├── src/             # Código-fonte React
    │   ├── App.js       # Componente principal
    │   └── ...
    ├── package.json     # Dependências do Node.js
    └── ...
```

## Requisitos

### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- PyMuPDF (fitz)
- SQLite3

### Frontend
- Node.js (14+)
- React
- npm ou yarn

## Como Executar

### Execução Automática (Recomendado)

#### Windows
```bash
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Execução Manual

#### Backend
```bash
cd app5/backend
pip install fastapi uvicorn python-multipart pymupdf
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd app5/frontend
npm install
npm start
```

## Acesso

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

## Acesso de Outra Máquina

Para acessar a aplicação de outra máquina na mesma rede:

1. Use o endereço IP do computador que está executando os serviços
2. O backend estará disponível em: `http://[IP_DO_SERVIDOR]:8000`
3. O frontend estará disponível em: `http://[IP_DO_SERVIDOR]:3000`

## Configuração Personalizada

Para definir um endereço de API personalizado para o frontend, crie um arquivo `.env` na pasta `app5/frontend` com o seguinte conteúdo:

```
REACT_APP_API_URL=http://seu-endereco-ip:8000
``` 