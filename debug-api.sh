#!/bin/bash
echo "🔍 Debugando API - Últimos logs de erro"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📋 Logs completos da API:"
docker compose -f docker-compose.cpu-only.yml logs api --tail=50

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Logs do Worker CPU:"
docker compose -f docker-compose.cpu-only.yml logs worker-cpu --tail=20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Testando conexões:"
echo ""

echo -n "PostgreSQL: "
docker compose -f docker-compose.cpu-only.yml exec -T db psql -U postgres -d audiomixer -c "SELECT 1" > /dev/null 2>&1 && echo "✅ OK" || echo "❌ FALHOU"

echo -n "Redis: "
docker compose -f docker-compose.cpu-only.yml exec -T redis redis-cli ping > /dev/null 2>&1 && echo "✅ OK" || echo "❌ FALHOU"

echo -n "MinIO: "
curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1 && echo "✅ OK" || echo "❌ FALHOU"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
