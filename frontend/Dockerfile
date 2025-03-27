FROM node:16-alpine

# Instalar ferramentas para diagnóstico de rede
RUN apk add --no-cache curl

WORKDIR /app

# Instalar dependências
COPY package*.json ./
RUN npm ci
RUN npm install openseadragon --save

# Copiar o código da aplicação
COPY . .

# Corrigir permissões
RUN mkdir -p node_modules/.cache && chmod -R 777 node_modules/.cache

# Porta para o servidor de desenvolvimento
EXPOSE 3000

# Comando para iniciar a aplicação
CMD ["npm", "start"] 