# syntax=docker/dockerfile:1

ARG NODE_VERSION=22-alpine

# ---- dependencies (cached when package files unchanged) ----
FROM node:${NODE_VERSION} AS deps
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# ---- development ----
FROM node:${NODE_VERSION} AS development
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NODE_ENV=development

EXPOSE 4200

# --host: required for port publishing from host
# --poll: helps file watchers with Docker bind mounts (macOS/Windows)
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--poll", "2000"]
