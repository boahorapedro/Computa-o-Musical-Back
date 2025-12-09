# Audio Mixer Backend

Backend de mixagem de áudio com síntese granular, separação de stems e processamento assíncrono.

## 🎯 Funcionalidades

- **Separação de stems** usando Demucs (htdemucs_ft)
- **Análise de áudio** com detecção de onsets e pitch (librosa)
- **Síntese granular** com mapeamento de pitch
- **Mixagem personalizada** via API REST
- **Processamento assíncrono** com Celery workers
- **Armazenamento S3-compatible** com MinIO
- **WebSocket** para notificações em tempo real

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FastAPI (API)                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ /upload  │  │/projects │  │ /library │  │   /mix   │  │   /ws    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │ PostgreSQL  │     │    Redis    │     │    MinIO    │
        │ (metadados) │     │(cache/queue)│     │  (storage)  │
        └─────────────┘     └─────────────┘     └─────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CELERY WORKERS                                   │
│  ┌─────────────────────┐          ┌─────────────────────────────────┐  │
│  │    GPU Worker       │          │         CPU Workers             │  │
│  │  (Separação Demucs) │          │  (Análise + Síntese + Mix)      │  │
│  └─────────────────────┘          └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## 📦 Stack Tecnológica

| Componente | Tecnologia | Função |
|------------|------------|--------|
| API | FastAPI | Endpoints REST assíncronos |
| Task Queue | Celery + Redis | Processamento assíncrono |
| Database | PostgreSQL | Metadados de projetos |
| Cache | Redis | Cache de análises e grãos |
| Storage | MinIO | Armazenamento de áudio |
| Audio Processing | librosa, numpy, soundfile | Processamento de áudio |
| Stem Separation | Demucs | Separação state-of-art |

## 🚀 Início Rápido

### Pré-requisitos

- Docker & Docker Compose
- (Opcional) GPU NVIDIA com drivers + nvidia-docker para separação de stems

### Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd audio-mixer-backend
```

2. Crie arquivo `.env` a partir do exemplo:
```bash
cp .env.example .env
```

3. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

4. Aguarde a inicialização dos serviços:
```bash
docker-compose logs -f api
```

5. Acesse a API:
- API: http://localhost:8000
- Documentação interativa: http://localhost:8000/docs
- MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

### Verificação de Saúde

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "ok"}
```

## 📚 Endpoints da API

### Upload

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/upload/base-track` | Upload de música base |
| POST | `/api/v1/upload/style-sound` | Upload de sons de estilo |

### Projetos

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/projects` | Listar todos os projetos |
| GET | `/api/v1/projects/{id}` | Detalhes do projeto |
| GET | `/api/v1/projects/{id}/status` | Status de separação |
| DELETE | `/api/v1/projects/{id}` | Remover projeto |

### Biblioteca de Sons

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/library` | Listar biblioteca |
| GET | `/api/v1/library/{id}` | Detalhes do som |
| DELETE | `/api/v1/library/{id}` | Remover som |

### Mixagem

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/mix` | Criar nova mixagem |
| GET | `/api/v1/mix/{id}` | Status da mixagem |
| GET | `/api/v1/mix/{id}/download` | Download do resultado |

### WebSocket

| Tipo | Endpoint | Descrição |
|------|----------|-----------|
| WS | `/ws/project/{id}` | Notificações do projeto |
| WS | `/ws/mix/{id}` | Notificações da mixagem |

## 🔄 Fluxo de Uso

### 1. Upload de Música Base

```bash
curl -X POST "http://localhost:8000/api/v1/upload/base-track" \
  -F "file=@musica.mp3" \
  -F "project_name=Meu Projeto"
```

Resposta:
```json
{
  "project_id": "uuid-do-projeto",
  "status": "queued",
  "message": "Stem separation started"
}
```

### 2. Acompanhar Status da Separação

```bash
curl "http://localhost:8000/api/v1/projects/{project_id}/status"
```

Resposta (quando completo):
```json
{
  "project_id": "uuid-do-projeto",
  "status": "ready",
  "stems": {
    "vocals": true,
    "drums": true,
    "bass": true,
    "other": true
  }
}
```

### 3. Upload de Sons de Estilo

```bash
curl -X POST "http://localhost:8000/api/v1/upload/style-sound" \
  -F "files=@bateria_trap.wav" \
  -F "files=@baixo_funk.wav"
```

### 4. Criar Mixagem

```bash
curl -X POST "http://localhost:8000/api/v1/mix" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid-do-projeto",
    "config": {
      "drums": {
        "enabled": true,
        "style_sound_id": "uuid-do-som-bateria",
        "volume": 1.0
      },
      "bass": {
        "enabled": true,
        "style_sound_id": "uuid-do-som-baixo",
        "volume": 0.8
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

### 5. Download da Mixagem

```bash
curl "http://localhost:8000/api/v1/mix/{mix_id}/download" -L -o resultado.wav
```

## 🛠️ Comandos Úteis

### Verificar Logs

```bash
# API
docker-compose logs -f api

# Worker CPU
docker-compose logs -f worker-cpu

# Worker GPU
docker-compose logs -f worker-gpu

# Todos os serviços
docker-compose logs -f
```

### Reiniciar Serviços

```bash
# Reiniciar tudo
docker-compose restart

# Reiniciar apenas API
docker-compose restart api

# Reiniciar workers
docker-compose restart worker-cpu worker-gpu
```

### Parar e Remover Containers

```bash
docker-compose down

# Remover também volumes (CUIDADO: apaga dados!)
docker-compose down -v
```

### Acessar Shell de um Container

```bash
# API
docker-compose exec api bash

# Worker CPU
docker-compose exec worker-cpu bash

# Banco de dados
docker-compose exec db psql -U postgres -d audiomixer
```

## 📂 Estrutura do Projeto

```
audio-mixer-backend/
├── docker/
│   ├── api/Dockerfile
│   ├── worker-cpu/Dockerfile
│   └── worker-gpu/Dockerfile
├── src/
│   ├── api/              # Endpoints REST
│   ├── config/           # Configurações
│   ├── db/               # Models e repositories
│   ├── services/         # Lógica de processamento
│   ├── storage/          # Cliente MinIO
│   ├── cache/            # Cliente Redis
│   ├── tasks/            # Tasks Celery
│   └── main.py           # Entry point
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## ⚙️ Configuração

Todas as configurações estão no arquivo `.env`:

```env
# API
APP_NAME=Audio Mixer API
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/audiomixer

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Audio Processing
DEFAULT_SAMPLE_RATE=44100
GRAIN_DURATION_MS=120
USE_PITCH_MAPPING=True

# Demucs
DEMUCS_MODEL=htdemucs_ft
```

## 🐛 Troubleshooting

### Worker GPU não está funcionando

Verifique se o NVIDIA Container Toolkit está instalado:
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Erro de conexão com MinIO

Verifique se o bucket foi criado:
```bash
docker-compose exec minio mc ls local/
```

### Task Celery travada

Reinicie os workers:
```bash
docker-compose restart worker-cpu worker-gpu
```

### Banco de dados não inicializa

Recrie o volume:
```bash
docker-compose down -v
docker-compose up -d
```

## 📊 Monitoramento

### Flower (Celery monitoring)

Para adicionar Flower ao `docker-compose.yml`:

```yaml
flower:
  image: mher/flower
  command: celery --broker=redis://redis:6379/1 flower --port=5555
  ports:
    - "5555:5555"
  depends_on:
    - redis
```

Acesse em: http://localhost:5555

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-asyncio httpx

# Executar testes
pytest tests/
```

## 📈 Performance

### Otimizações Recomendadas

1. **Concorrência de Workers**: Ajuste `--concurrency` baseado no número de CPUs
2. **Cache Redis**: Configure TTL adequado para grãos e análises
3. **MinIO**: Use SSD para melhor I/O
4. **PostgreSQL**: Configure pool de conexões adequadamente

## 🔒 Segurança

### Produção

- [ ] Altere credenciais padrão do MinIO
- [ ] Configure HTTPS/TLS
- [ ] Implemente autenticação na API
- [ ] Restrinja CORS origins
- [ ] Configure rate limiting
- [ ] Use secrets manager para credenciais

## 📝 Licença

[Especifique sua licença aqui]

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📧 Contato

[Suas informações de contato]

---

Desenvolvido seguindo o plano de arquitetura de backend de mixagem de áudio com síntese granular.
