FROM node:24.3.0-alpine AS builder

RUN npm install -g pnpm

WORKDIR /web

ENV PNPM_HOME=/pnpm
ENV PATH=$PATH:$PNPM_HOME

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

FROM node:24.3.0-alpine AS runtime

RUN npm install -g pnpm

WORKDIR /web

ENV PNPM_HOME=/pnpm
ENV PATH=$PATH:$PNPM_HOME

COPY --from=builder /web/node_modules ./node_modules
COPY --from=builder /web/package.json /web/pnpm-lock.yaml ./

COPY . .

RUN chown -R node:node /web
USER node

EXPOSE 5173

CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]