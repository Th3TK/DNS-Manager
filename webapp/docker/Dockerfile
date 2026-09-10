# Build stage
FROM node:22-alpine AS build

WORKDIR /webapp

COPY package*.json ./

RUN npm install
RUN npm i -g serve

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]