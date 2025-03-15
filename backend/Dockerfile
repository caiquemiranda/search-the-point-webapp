FROM python:3.9-slim

WORKDIR /app

# Instalar dependências (requirements.txt será montado via volume no docker-compose)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Porta para a API
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 