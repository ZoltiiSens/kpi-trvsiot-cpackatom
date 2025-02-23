FROM node:18-alpine

WORKDIR /usr/edge

COPY package*.json ./

RUN npm install

RUN npm run build

COPY . .

CMD ["node", "dist/server.js"]
