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
├── frontend/            # Aplicação React
│   ├── public/          # Arquivos estáticos
│   ├── src/             # Código-fonte React
│   │   ├── App.js       # Componente principal
│   │   └── ...
│   ├── package.json     # Dependências do Node.js
│   └── .env             # Configurações de ambiente
│
├── start.bat            # Script de execução para Windows
├── start.sh             # Script de execução para Linux/Mac
├── requirements.txt     # Dependências Python
└── manual-setup.md      # Guia de configuração manual
```

## Como Executar

### Execução Automatizada (Recomendado)

Entre na pasta `app5` e execute:

#### Windows
```
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Execução Manual

Se tiver problemas com os scripts automatizados, consulte as instruções detalhadas em `manual-setup.md`.

## Acesso

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000

## Acesso de Outra Máquina

Para acessar a aplicação de outra máquina na mesma rede:

1. Use o endereço IP do computador que está executando os serviços
2. O backend estará disponível em: `http://[IP_DO_SERVIDOR]:8000`
3. O frontend estará disponível em: `http://[IP_DO_SERVIDOR]:3000`

## Funcionalidades

- Upload e visualização de PDFs
- Navegação entre páginas
- Adição de coordenadas em pontos específicos
- Visualização de coordenadas salvas
- Exportação de coordenadas para CSV
- Busca de coordenadas por nome ou fonte 