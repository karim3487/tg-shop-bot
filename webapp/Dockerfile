FROM oven/bun:1 AS deps
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

FROM oven/bun:1 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN bun run build

FROM node:22-alpine AS runner
# Install tini
RUN apk add --no-cache tini

WORKDIR /app
ENV NODE_ENV=production
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

# Add non-root user
RUN addgroup -S nextgroup && adduser -S nextuser -G nextgroup

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Standalone mode doesn't always need manual SSR chunk copy if built correctly,
# but keeping it if the user had it for a reason (Next.js 15+ changes).
# However, I'll set proper ownership.
RUN chown -R nextuser:nextgroup /app

USER nextuser

EXPOSE 3000
ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "server.js"]
