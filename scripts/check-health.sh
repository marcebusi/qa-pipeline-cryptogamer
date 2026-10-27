#!/bin/bash
# Verifica que el backend esté listo antes de correr los tests.
# Uso: ./scripts/check-health.sh http://localhost:3001 30

URL="${1:-http://localhost:3001}"
MAX_RETRIES="${2:-30}"
RETRY_INTERVAL=2

echo "⏳ Esperando que el backend esté disponible en $URL..."

for i in $(seq 1 $MAX_RETRIES); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL/api/products" 2>/dev/null)

  if [ "$STATUS" = "200" ]; then
    echo "✅ Backend disponible (intento $i) — HTTP $STATUS"
    exit 0
  fi

  echo "  Intento $i/$MAX_RETRIES — HTTP $STATUS (esperando ${RETRY_INTERVAL}s...)"
  sleep $RETRY_INTERVAL
done

echo "❌ Backend no disponible después de $MAX_RETRIES intentos"
exit 1
