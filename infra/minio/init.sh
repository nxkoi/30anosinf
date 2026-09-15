#!/bin/sh
set -eu

echo "Waiting for MinIO..."
until mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1; do
  sleep 1
done

for bucket in submissions-quarantine originals derived approved-assets; do
  mc mb --ignore-existing "local/${bucket}"
  mc anonymous set none "local/${bucket}"
  echo "bucket ready: ${bucket}"
done

echo "MinIO init complete."
