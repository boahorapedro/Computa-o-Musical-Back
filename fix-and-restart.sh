#!/bin/bash
echo "🔧 Corrigindo e reiniciando serviços..."
echo ""

echo "1️⃣ Parando containers..."
docker compose -f docker-compose.cpu-only.yml down

echo ""
echo "2️⃣ Iniciando novamente..."
docker compose -f docker-compose.cpu-only.yml up -d

echo ""
echo "3️⃣ Aguardando inicialização (30s)..."
sleep 30

echo ""
echo "4️⃣ Verificando status..."
docker compose -f docker-compose.cpu-only.yml ps

echo ""
echo "5️⃣ Verificando logs da API..."
docker compose -f docker-compose.cpu-only.yml logs --tail=20 api

echo ""
echo "6️⃣ Testando saúde da API..."
curl -s http://localhost:8000/health || echo "❌ API não respondeu"

echo ""
echo "✅ Concluído! Acesse http://localhost:8000/docs"
