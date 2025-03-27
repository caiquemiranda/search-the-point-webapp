# Backend da Aplicação Search The Point

Este é o backend da aplicação Search The Point, desenvolvido com FastAPI.

## Estrutura do Projeto

```
backend/
├── app/
│   ├── api/            # Rotas da API (não utilizadas no momento)
│   ├── core/           # Configurações e constantes
│   ├── db/             # Configuração do banco de dados
│   ├── models/         # Modelos Pydantic
│   ├── services/       # Serviços e lógica de negócios
│   └── main.py         # Arquivo principal da aplicação
├── requirements.txt    # Dependências do projeto
└── README.md          # Este arquivo
```

## Requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório
2. Navegue até o diretório do backend:
   ```bash
   cd backend
   ```
3. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Executando a Aplicação

Para iniciar o servidor de desenvolvimento:

```bash
uvicorn app.main:app --reload
```

A aplicação estará disponível em `http://localhost:8000`

## Documentação da API

A documentação da API está disponível em:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Funcionalidades

- Upload e processamento de arquivos PDF
- Conversão de PDF para imagens
- Gerenciamento de coordenadas
- Histórico de imagens processadas
- Exportação de coordenadas

## Docker

A aplicação também pode ser executada em contêineres Docker:

```bash
docker-compose up
```

Isto iniciará tanto o backend quanto o frontend em containers separados. 