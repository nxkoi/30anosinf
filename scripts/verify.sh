#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

source .env 2>/dev/null || true
BASE="${VERIFY_BASE:-http://127.0.0.1}"
USER="${REVIEW_USERNAME:-revisao}"
PASS="${REVIEW_PASSWORD:-revisao-trocar}"

echo "== compose ps =="
docker compose ps

echo "== health =="
curl -sf "$BASE/api/health" | tee /tmp/health.json
echo

echo "== site home =="
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/")
test "$code" = "200"

echo "== review protected =="
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/revisao/")
test "$code" = "401"

echo "== review with auth =="
code=$(curl -s -o /dev/null -w "%{http_code}" -u "$USER:$PASS" "$BASE/revisao/")
test "$code" = "200"

echo "== postgres =="
docker compose exec -T postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"

echo "== redis =="
docker compose exec -T redis redis-cli ping | grep -q PONG

echo "== minio buckets =="
docker compose run --rm --entrypoint /bin/sh minio-init -c \
  "mc alias set local http://minio:9000 \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" && mc ls local" | tee /tmp/mc-ls.txt
grep -q submissions-quarantine /tmp/mc-ls.txt
grep -q originals /tmp/mc-ls.txt
grep -q derived /tmp/mc-ls.txt
grep -q approved-assets /tmp/mc-ls.txt

echo "== api review unauthorized =="
code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/review/submissions")
test "$code" = "401"

echo "VERIFY OK"
