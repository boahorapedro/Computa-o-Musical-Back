# 🚀 Como Iniciar o Projeto

## ⚠️ Você não tem GPU NVIDIA?

Use a versão **CPU-only** do projeto. A separação de stems será feita pela CPU (mais lento, mas funcional).

## 📝 Passo a Passo

### Opção 1: Script Automático (Recomendado)

```bash
sudo ./start-cpu-only.sh
```

### Opção 2: Manual

```bash
# 1. Parar containers antigos
sudo docker compose down

# 2. Iniciar versão CPU-only
sudo docker compose -f docker-compose.cpu-only.yml up -d

# 3. Aguardar 30 segundos
sleep 30

# 4. Inicializar banco de dados
sudo docker compose -f docker-compose.cpu-only.yml exec api python init_db.py

# 5. Verificar saúde
curl http://localhost:8000/health
```

## ✅ Verificar se está funcionando

```bash
# Ver status dos containers
sudo docker compose -f docker-compose.cpu-only.yml ps

# Ver logs da API
sudo docker compose -f docker-compose.cpu-only.yml logs -f api

# Ver logs do worker
sudo docker compose -f docker-compose.cpu-only.yml logs -f worker-cpu
```

## 📚 Acessar a Aplicação

- **Documentação da API**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
  - Usuário: `minioadmin`
  - Senha: `minioadmin`

## 🛑 Parar o Projeto

```bash
sudo docker compose -f docker-compose.cpu-only.yml down
```

## 🐛 Problemas Comuns

### "permission denied while trying to connect to the Docker daemon socket"

**Solução**: Use `sudo` antes dos comandos docker:

```bash
sudo docker compose -f docker-compose.cpu-only.yml up -d
```

### "service api is not running"

**Solução**: Aguarde mais tempo ou veja os logs:

```bash
sudo docker compose -f docker-compose.cpu-only.yml logs api
```

### Porta já está em uso

**Solução**: Verifique se há outros serviços usando as portas 8000, 5432, 6379, 9000, 9001:

```bash
sudo netstat -tulpn | grep -E ':(8000|5432|6379|9000|9001)'
```

## 📊 Diferenças CPU-only vs GPU

| Recurso | CPU-only | GPU |
|---------|----------|-----|
| Separação de stems | ✅ (lento) | ✅ (rápido) |
| Análise de áudio | ✅ | ✅ |
| Síntese granular | ✅ | ✅ |
| Mixagem | ✅ | ✅ |
| Tempo de separação | ~10-20 min | ~1-2 min |

**Nota**: A separação de stems pela CPU é funcional, mas significativamente mais lenta. Para produção com alto volume, recomenda-se GPU NVIDIA.

## 🔧 Comandos Úteis

```bash
# Ver todos os containers
sudo docker compose -f docker-compose.cpu-only.yml ps

# Ver logs de todos os serviços
sudo docker compose -f docker-compose.cpu-only.yml logs -f

# Reiniciar apenas a API
sudo docker compose -f docker-compose.cpu-only.yml restart api

# Entrar no shell da API
sudo docker compose -f docker-compose.cpu-only.yml exec api bash

# Entrar no PostgreSQL
sudo docker compose -f docker-compose.cpu-only.yml exec db psql -U postgres -d audiomixer
```

## 📖 Próximos Passos

1. Acesse http://localhost:8000/docs
2. Teste o endpoint `/health`
3. Faça upload de uma música usando `/api/v1/upload/base-track`
4. Acompanhe o processamento
5. Leia o [README.md](README.md) completo para mais detalhes

---

**Divirta-se criando mixagens! 🎶**
