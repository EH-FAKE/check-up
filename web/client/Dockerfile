FROM node:18-alpine as builder

WORKDIR /web

COPY package.json

RUN pnpm install 

COPY . .

EXPOSE 5173

CMD ["pnpm", "run", "dev"]