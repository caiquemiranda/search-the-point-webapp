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
├── docker-compose.yml   # Configuração Docker Compose
├── docker-start.bat     # Script para iniciar Docker (Windows)
├── docker-stop.bat      # Script para parar Docker (Windows)
├── docker-start.sh      # Script para iniciar Docker (Linux/Mac)
├── docker-stop.sh       # Script para parar Docker (Linux/Mac)
├── start.bat            # Script de execução para Windows
├── start.sh             # Script de execução para Linux/Mac
├── requirements.txt     # Dependências Python
└── manual-setup.md      # Guia de configuração manual
```

## Como Executar

### Usando Docker (Recomendado)

A maneira mais fácil de executar a aplicação é usando Docker, que não requer instalação de Python ou Node.js na máquina host.

#### Pré-requisitos
- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/) (geralmente já incluído no Docker Desktop)

#### Windows
```
docker-start.bat
```

#### Linux/Mac
```bash
chmod +x docker-start.sh
./docker-start.sh
```

Para parar os contêineres:
- Windows: `docker-stop.bat`
- Linux/Mac: `./docker-stop.sh`

### Execução Local

Se preferir executar diretamente no seu sistema:

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