# 🔧 Guia de Solução de Problemas

## ✅ Como Verificar se Está Funcionando

### 1. Verificar Status dos Containers

```bash
sudo docker compose -f docker-compose.cpu-only.yml ps
```

**Esperado**: Todos com status "Up"

```
NAME                  STATUS
musica-api-1          Up
musica-worker-cpu-1   Up
musica-db-1           Up
musica-redis-1        Up
musica-minio-1        Up
```

### 2. Verificar Saúde da API

```bash
curl http://localhost:8000/health
```

**Esperado**: `{"status":"ok"}`

### 3. Acessar Documentação

Abra no navegador: http://localhost:8000/docs

**Esperado**: Interface Swagger UI com todos os endpoints

## ❌ Problemas Comuns e Soluções

### Erro: "AccessDenied" do MinIO

**Sintoma**:
```xml
<Code>AccessDenied</Code>
<Message>Access Denied.</Message>
```

**Solução**: Isso é NORMAL! É apenas o navegador tentando acessar `/docs` do MinIO. Não afeta o funcionamento.

**Como ignorar**: Acesse diretamente http://localhost:8000/docs (da API, não do MinIO)

---

### Erro: "service api is not running"

**Sintoma**:
```
service "api" is not running
```

**Diagnóstico**:
```bash
# Ver logs da API
sudo docker compose -f docker-compose.cpu-only.yml logs api
```

**Soluções possíveis**:

1. **API não iniciou ainda**:
   ```bash
   # Aguarde 30 segundos e tente novamente
   sleep 30
   sudo docker compose -f docker-compose.cpu-only.yml exec api python init_db.py
   ```

2. **Erro na inicialização**:
   ```bash
   # Veja os logs para identificar o erro
   sudo docker compose -f docker-compose.cpu-only.yml logs api

   # Reinicie o container
   sudo docker compose -f docker-compose.cpu-only.yml restart api
   ```

3. **Dependência não satisfeita**:
   ```bash
   # Verifique se PostgreSQL está rodando
   sudo docker compose -f docker-compose.cpu-only.yml ps db

   # Se não estiver, inicie tudo novamente
   sudo docker compose -f docker-compose.cpu-only.yml down
   sudo docker compose -f docker-compose.cpu-only.yml up -d
   ```

---

### Erro: "Connection refused" ao acessar API

**Sintoma**:
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Diagnóstico**:
```bash
# Verificar se o container está rodando
sudo docker compose -f docker-compose.cpu-only.yml ps api

# Ver logs
sudo docker compose -f docker-compose.cpu-only.yml logs api
```

**Soluções**:

1. **Container não está rodando**:
   ```bash
   sudo docker compose -f docker-compose.cpu-only.yml up -d api
   ```

2. **Porta já está em uso**:
   ```bash
   # Verificar o que está usando a porta 8000
   sudo netstat -tulpn | grep 8000

   # Parar o processo ou mudar a porta no docker-compose.cpu-only.yml
   ```

---

### Erro: "database does not exist"

**Sintoma**:
```
asyncpg.exceptions.InvalidCatalogNameError: database "audiomixer" does not exist
```

**Solução**:
```bash
# Criar o banco manualmente
sudo docker compose -f docker-compose.cpu-only.yml exec db psql -U postgres -c "CREATE DATABASE audiomixer;"

# Ou reiniciar o PostgreSQL
sudo docker compose -f docker-compose.cpu-only.yml restart db
sleep 10
sudo docker compose -f docker-compose.cpu-only.yml exec api python init_db.py
```

---

### Erro: "tables don't exist"

**Sintoma**:
```
relation "projects" does not exist
```

**Solução**:
```bash
# Executar script de inicialização do banco
sudo docker compose -f docker-compose.cpu-only.yml exec api python init_db.py
```

---

### Worker CPU não está processando tasks

**Diagnóstico**:
```bash
# Ver logs do worker
sudo docker compose -f docker-compose.cpu-only.yml logs worker-cpu
```

**Soluções**:

1. **Worker não conectou ao Redis**:
   ```bash
   # Verificar Redis
   sudo docker compose -f docker-compose.cpu-only.yml exec redis redis-cli ping

   # Reiniciar worker
   sudo docker compose -f docker-compose.cpu-only.yml restart worker-cpu
   ```

2. **Erro de importação de módulos**:
   ```bash
   # Rebuild do container
   sudo docker compose -f docker-compose.cpu-only.yml build worker-cpu
   sudo docker compose -f docker-compose.cpu-only.yml up -d worker-cpu
   ```

---

### MinIO não está acessível

**Sintoma**:
```
Failed to connect to localhost port 9000
```

**Solução**:
```bash
# Verificar status
sudo docker compose -f docker-compose.cpu-only.yml ps minio

# Ver logs
sudo docker compose -f docker-compose.cpu-only.yml logs minio

# Reiniciar
sudo docker compose -f docker-compose.cpu-only.yml restart minio
```

---

## 🔍 Comandos de Diagnóstico

### Ver todos os logs

```bash
sudo docker compose -f docker-compose.cpu-only.yml logs -f
```

### Ver logs de um serviço específico

```bash
# API
sudo docker compose -f docker-compose.cpu-only.yml logs -f api

# Worker
sudo docker compose -f docker-compose.cpu-only.yml logs -f worker-cpu

# Banco de dados
sudo docker compose -f docker-compose.cpu-only.yml logs -f db
```

### Verificar uso de recursos

```bash
sudo docker stats
```

### Inspecionar container

```bash
sudo docker compose -f docker-compose.cpu-only.yml exec api bash
```

### Limpar tudo e reiniciar

```bash
# ⚠️ CUIDADO: Remove todos os dados!
sudo docker compose -f docker-compose.cpu-only.yml down -v
sudo docker compose -f docker-compose.cpu-only.yml up -d
sleep 30
sudo docker compose -f docker-compose.cpu-only.yml exec api python init_db.py
```

---

## 📊 Checklist de Saúde do Sistema

Execute este checklist para verificar se tudo está funcionando:

```bash
# 1. Containers rodando?
sudo docker compose -f docker-compose.cpu-only.yml ps

# 2. API respondendo?
curl http://localhost:8000/health

# 3. Banco de dados acessível?
sudo docker compose -f docker-compose.cpu-only.yml exec db psql -U postgres -d audiomixer -c "SELECT 1"

# 4. Redis respondendo?
sudo docker compose -f docker-compose.cpu-only.yml exec redis redis-cli ping

# 5. MinIO respondendo?
curl http://localhost:9000/minio/health/live

# 6. Documentação acessível?
curl -I http://localhost:8000/docs | head -n 1
```

Se todos os comandos acima funcionarem, o sistema está operacional! ✅

---

## 🆘 Ainda com Problemas?

1. Veja os logs completos: `sudo docker compose -f docker-compose.cpu-only.yml logs`
2. Verifique o arquivo [START_HERE.md](START_HERE.md)
3. Leia o [README.md](README.md) principal
4. Verifique as issues no repositório

---

## 📝 Informações de Debug Úteis

### Versões

```bash
# Docker
docker --version

# Docker Compose
docker compose version

# Python (dentro do container)
sudo docker compose -f docker-compose.cpu-only.yml exec api python --version
```

### Variáveis de Ambiente

```bash
# Ver variáveis da API
sudo docker compose -f docker-compose.cpu-only.yml exec api env | grep -E '(DATABASE|REDIS|MINIO|CELERY)'
```

### Portas em Uso

```bash
sudo netstat -tulpn | grep -E ':(8000|5432|6379|9000|9001)'
```

---

**Boa sorte! 🚀**
