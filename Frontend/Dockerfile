FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm ci

ARG VITE_BACKEND_HOST
ARG VITE_BACKEND_PORT
ARG VITE_GITHUB_CLIENT_ID

ENV VITE_BACKEND_HOST=localhost
ENV VITE_BACKEND_PORT=80
ENV VITE_GITHUB_CLIENT_ID=Ov23li0EFVhcbeGoyQvF

COPY . .
RUN npm run build

FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]