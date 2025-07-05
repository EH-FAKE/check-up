FROM node:24.3.0-alpine

WORKDIR /web

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./

ENV PNPM_HOME=/pnpm-test/.pnpm
ENV PATH=$PATH:$PNPM_HOME

RUN pnpm install 

COPY . .

EXPOSE 5173

CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]