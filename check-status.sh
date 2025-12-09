#!/bin/bash
# Script para verificar status do sistema

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Verificando Status do Sistema"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📦 Containers:"
docker compose -f docker-compose.cpu-only.yml ps
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 Verificando Saúde dos Serviços"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# API
echo -n "API (porta 8000): "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ OK"
    curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "❌ FALHOU"
fi
echo ""

# PostgreSQL
echo -n "PostgreSQL (porta 5432): "
if docker compose -f docker-compose.cpu-only.yml exec -T db psql -U postgres -d audiomixer -c "SELECT 1" > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi
echo ""

# Redis
echo -n "Redis (porta 6379): "
if docker compose -f docker-compose.cpu-only.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi
echo ""

# MinIO
echo -n "MinIO (porta 9000): "
if curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FALHOU"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Últimas Linhas dos Logs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "API:"
docker compose -f docker-compose.cpu-only.yml logs --tail=5 api 2>&1 | grep -v "WARN"
echo ""

echo "Worker CPU:"
docker compose -f docker-compose.cpu-only.yml logs --tail=5 worker-cpu 2>&1 | grep -v "WARN"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 URLs Úteis"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "API Docs:       http://localhost:8000/docs"
echo "MinIO Console:  http://localhost:9001"
echo ""
