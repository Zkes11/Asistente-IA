FROM node:22-alpine

WORKDIR /app

COPY package.json /app/package.json
COPY packages/contracts /app/packages/contracts
COPY packages/ui /app/packages/ui
COPY apps/web/package.json /app/apps/web/package.json

RUN npm install

COPY apps/web /app/apps/web

WORKDIR /app/apps/web
EXPOSE 3000
CMD ["npm", "run", "dev"]
