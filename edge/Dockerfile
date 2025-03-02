FROM node:18-alpine

WORKDIR /usr/edge

COPY package*.json ./

RUN npm install

COPY . .

CMD ["node", "dist/server.js"]
