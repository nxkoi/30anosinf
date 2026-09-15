FROM node:22-alpine AS build
WORKDIR /app
ARG PUBLIC_API_BASE=/api
ENV PUBLIC_API_BASE=$PUBLIC_API_BASE
COPY package.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM alpine:3.21
COPY --from=build /app/dist /dist
CMD ["sh", "-c", "rm -rf /out/* /out/.[!.]* 2>/dev/null; cp -a /dist/. /out/ && echo site-copied"]
