# Build stage
FROM node:22-alpine AS build

WORKDIR /webapp

COPY package*.json ./

RUN npm install
RUN npm i -g serve

COPY . .

ARG VITE_HTTPS_ENABLED
ARG VITE_API_PORT

ENV VITE_HTTPS_ENABLED=$VITE_HTTPS_ENABLED
ENV VITE_API_PORT=$VITE_API_PORT

RUN npm run build

EXPOSE 3000

CMD ["serve", "-s", "dist", "-l", "3000"]