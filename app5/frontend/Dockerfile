FROM node:16-alpine

WORKDIR /app

# Instalar dependências
COPY package*.json ./
RUN npm ci

# Copiar o código da aplicação
COPY . .

# Porta para o servidor de desenvolvimento
EXPOSE 3000

# Comando para iniciar a aplicação
CMD ["npm", "start"] 