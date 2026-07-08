FROM node:24-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["sh", "-c", "printf 'window.__PET_PLANET_CONFIG__ = { API_BASE_URL: \"%s\" };\\n' \"${FRONTEND_API_BASE_URL:-}\" > /usr/share/nginx/html/config.js && nginx -g 'daemon off;'"]
