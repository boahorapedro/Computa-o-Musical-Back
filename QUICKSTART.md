# 🚀 Guia de Início Rápido

## Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- (Opcional) GPU NVIDIA + nvidia-docker para separação de stems

## Instalação em 5 Passos

### 1. Clone e Configure

```bash
# Clone o repositório
git clone <repository-url>
cd audio-mixer-backend

# Copie o arquivo de ambiente
cp .env.example .env
```

### 2. Inicie os Serviços

```bash
# Com Make (recomendado)
make up

# Ou com Docker Compose
docker-compose up -d
```

### 3. Inicialize o Banco de Dados

```bash
# Aguarde ~30 segundos para o PostgreSQL iniciar, então:
make init-db

# Ou manualmente:
docker-compose exec api python init_db.py
```

### 4. Verifique a Instalação

```bash
# Verifique a saúde da API
make health

# Ou com curl
curl http://localhost:8000/health
```

**Resposta esperada**:
```json
{"status": "ok"}
```

### 5. Acesse a Documentação

Abra no navegador: http://localhost:8000/docs

Ou use: `make docs`

---

## 🎵 Exemplo Completo de Uso

### Passo 1: Upload de Música Base

**Via cURL**:
```bash
curl -X POST "http://localhost:8000/api/v1/upload/base-track" \
  -F "file=@sua-musica.mp3" \
  -F "project_name=Meu Remix"
```

**Via Python**:
```python
import requests

files = {"file": open("sua-musica.mp3", "rb")}
data = {"project_name": "Meu Remix"}

response = requests.post(
    "http://localhost:8000/api/v1/upload/base-track",
    files=files,
    data=data
)

project_id = response.json()["project_id"]
print(f"Projeto criado: {project_id}")
```

**Resposta**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Stem separation started"
}
```

### Passo 2: Monitorar Separação de Stems

```bash
# Substitua {project_id} pelo ID retornado
curl "http://localhost:8000/api/v1/projects/{project_id}/status"
```

**Enquanto processando**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "separating"
}
```

**Quando completo**:
```json
{
  "project_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "ready",
  "stems": {
    "vocals": true,
    "drums": true,
    "bass": true,
    "other": true
  }
}
```

### Passo 3: Upload de Sons de Estilo

```bash
curl -X POST "http://localhost:8000/api/v1/upload/style-sound" \
  -F "files=@bateria-trap.wav" \
  -F "files=@baixo-funk.wav"
```

**Resposta**:
```json
{
  "uploaded": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "bateria-trap.wav",
      "duplicate": false
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "name": "baixo-funk.wav",
      "duplicate": false
    }
  ]
}
```

### Passo 4: Criar Mixagem

```bash
curl -X POST "http://localhost:8000/api/v1/mix" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": {
      "drums": {
        "enabled": true,
        "style_sound_id": "660e8400-e29b-41d4-a716-446655440001",
        "volume": 1.0
      },
      "bass": {
        "enabled": true,
        "style_sound_id": "770e8400-e29b-41d4-a716-446655440002",
        "volume": 0.8
      },
      "other": {
        "enabled": false
      },
      "vocals": {
        "enabled": true,
        "volume": 1.2
      }
    },
    "settings": {
      "grain_duration_ms": 120,
      "use_pitch_mapping": true,
      "use_envelope": true
    }
  }'
```

**Resposta**:
```json
{
  "mix_id": "880e8400-e29b-41d4-a716-446655440003",
  "status": "queued",
  "message": "Mix started"
}
```

### Passo 5: Verificar Status da Mixagem

```bash
curl "http://localhost:8000/api/v1/mix/{mix_id}"
```

**Quando completo**:
```json
{
  "mix_id": "880e8400-e29b-41d4-a716-446655440003",
  "status": "complete",
  "config": {...},
  "created_at": "2025-01-15T10:30:00Z",
  "download_url": "http://localhost:9000/audio-storage/mixes/..."
}
```

### Passo 6: Download do Resultado

```bash
# Via redirect automático
curl -L "http://localhost:8000/api/v1/mix/{mix_id}/download" -o resultado.wav

# Ou use a download_url diretamente
curl -o resultado.wav "http://localhost:9000/audio-storage/mixes/..."
```

---

## 🛠️ Comandos Úteis

### Gerenciamento de Serviços

```bash
make up              # Inicia serviços
make down            # Para serviços
make restart         # Reinicia serviços
make ps              # Status dos containers
```

### Logs

```bash
make logs            # Todos os logs
make logs-api        # Logs da API
make logs-worker-cpu # Logs do worker CPU
make logs-worker-gpu # Logs do worker GPU
```

### Acesso aos Containers

```bash
make shell-api       # Shell do container da API
make shell-worker    # Shell do worker CPU
make shell-db        # PostgreSQL CLI
```

### Limpeza

```bash
make clean           # Remove tudo (containers, volumes, imagens)
```

---

## 🐛 Troubleshooting

### Erro: "Connection refused" ao acessar API

**Solução**: Aguarde ~30 segundos após `make up` para inicialização completa

```bash
# Verifique status
make ps

# Veja logs
make logs-api
```

### Erro: "Database does not exist"

**Solução**: Inicialize o banco de dados

```bash
make init-db
```

### Workers não processam tasks

**Solução**: Verifique logs e reinicie workers

```bash
make logs-worker-cpu
make logs-worker-gpu
make restart
```

### MinIO não acessível

**Solução**: Verifique se a porta 9000/9001 está livre

```bash
sudo netstat -tulpn | grep 9000
make minio  # Abre console (http://localhost:9001)
```

---

## 📊 Dashboards e Monitoramento

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Health Check | http://localhost:8000/health | - |

---

## 🧪 Testando Localmente (Sem Docker)

### 1. Instale Dependências

```bash
# Crie ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### 2. Configure Variáveis de Ambiente

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/audiomixer"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/1"
export MINIO_ENDPOINT="localhost:9000"
# ... outras variáveis
```

### 3. Inicie Serviços Individualmente

```bash
# Terminal 1: API
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Worker CPU
celery -A src.tasks.celery_app worker --loglevel=info

# Terminal 3: Worker GPU (se tiver GPU)
celery -A src.tasks.celery_app worker --loglevel=info -Q gpu --concurrency=1
```

---

## 📚 Próximos Passos

- Leia a [Arquitetura do Sistema](ARCHITECTURE.md)
- Explore a [Documentação da API](http://localhost:8000/docs)
- Veja exemplos em [examples/](examples/)
- Contribua com melhorias!

---

## 💡 Dicas

- Use WebSocket para notificações em tempo real
- Cache de grãos é persistente (não expira automaticamente)
- Mixagens podem ser recriadas sem reprocessar stems
- Demucs é CPU-intensivo sem GPU (~10x mais lento)

---

**Divirta-se criando mixagens incríveis! 🎶**
