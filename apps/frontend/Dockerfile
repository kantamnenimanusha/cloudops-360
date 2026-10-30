FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm install --no-audit --no-fund

FROM deps AS test
COPY . .
RUN npm test

FROM deps AS build
COPY . .
RUN npm run build

FROM nginx/nginx-unprivileged:1.30.6-alpine3.24-slim AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
