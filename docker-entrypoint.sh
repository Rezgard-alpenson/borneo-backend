#!/bin/sh
set -e

echo ">>> Menjalankan migrasi database... <<<"
alembic upgrade head
echo ">>> Migrasi selesai! <<<"

exec "$@"
