#!/bin/bash
# Script para iniciar o projeto sem GPU (CPU only)

echo "🛑 Parando containers antigos..."
docker compose down 2>/dev/null

echo ""
echo "🚀 Iniciando serviços (CPU only)..."
docker compose -f docker-compose.cpu-only.yml up -d

echo ""
echo "⏳ Aguardando inicialização dos serviços (30 segundos)..."
sleep 30

echo ""
echo "🗄️  Inicializando banco de dados..."
docker compose -f docker-compose.cpu-only.yml exec -T api python init_db.py

echo ""
echo "✅ Verificando saúde da API..."
curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health

echo ""
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Sistema iniciado com sucesso!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Documentação API: http://localhost:8000/docs"
echo "🗄️  MinIO Console:    http://localhost:9001"
echo "     Credenciais:     minioadmin / minioadmin"
echo ""
echo "📊 Para ver logs:"
echo "   docker compose -f docker-compose.cpu-only.yml logs -f"
echo ""
echo "🛑 Para parar:"
echo "   docker compose -f docker-compose.cpu-only.yml down"
echo ""
