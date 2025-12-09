# Arquitetura do Sistema - Audio Mixer Backend

## 📋 Visão Geral

Sistema de backend para mixagem de áudio com síntese granular, implementado seguindo arquitetura de microserviços com processamento assíncrono.

## 🎯 Decisões Arquiteturais

### 1. Separação de Responsabilidades

#### API Layer (FastAPI)
- **Responsabilidade**: Receber requisições HTTP, validar entrada, orquestrar tasks
- **Justificativa**: FastAPI oferece async nativo, validação automática via Pydantic, documentação OpenAPI
- **Padrão**: REST + WebSocket para notificações em tempo real

#### Task Queue (Celery)
- **Responsabilidade**: Processamento assíncrono de tarefas longas
- **Justificativa**: Desacoplar processamento pesado da API, permitir retry e monitoramento
- **Workers**:
  - **GPU Worker**: Separação de stems com Demucs (alta demanda de GPU)
  - **CPU Workers**: Análise, síntese granular e mixagem (paralelizável)

#### Storage (MinIO)
- **Responsabilidade**: Armazenamento de arquivos de áudio
- **Justificativa**: S3-compatible, permite migração fácil para AWS/GCP/Azure
- **Organização**:
  ```
  audio-storage/
  ├── uploads/base/{project_id}/        # Músicas originais
  ├── uploads/styles/{style_id}/        # Sons de estilo
  ├── stems/{project_id}/               # Stems separados
  └── mixes/{mix_id}/                   # Mixagens finalizadas
  ```

#### Database (PostgreSQL)
- **Responsabilidade**: Metadados, estados, relacionamentos
- **Justificativa**: ACID, suporte a JSON, excelente para metadados
- **Schemas**: Ver [src/db/models.py](src/db/models.py)

#### Cache (Redis)
- **Responsabilidade**: Cache de análises e bibliotecas de grãos
- **Justificativa**: Performance, evita reprocessamento, TTL automático
- **Estruturas**:
  - `analysis:{project_id}` → Análise de onsets/pitch
  - `grains:{style_sound_id}` → Biblioteca de grãos processados

---

## 🔄 Fluxo de Dados

### 1. Upload e Separação de Stems

```
Cliente
  │
  ├─── POST /upload/base-track
  │
  ▼
FastAPI
  │
  ├─── Valida arquivo
  ├─── Upload para MinIO (uploads/base/{project_id}/)
  ├─── Cria registro no PostgreSQL (status: "created")
  │
  ▼
Celery Task: separate_stems
  │
  ├─── Download do MinIO
  ├─── Executa Demucs (GPU Worker)
  ├─── Upload stems para MinIO (stems/{project_id}/)
  ├─── Atualiza PostgreSQL (status: "ready")
  │
  ▼
WebSocket Notification
  │
  └─── Notifica cliente sobre conclusão
```

### 2. Construção de Biblioteca de Grãos

```
Cliente
  │
  ├─── POST /upload/style-sound
  │
  ▼
FastAPI
  │
  ├─── Upload para MinIO (uploads/styles/{style_id}/)
  ├─── Cria registro no PostgreSQL
  │
  ▼
Celery Task: build_grain_library
  │
  ├─── Download do MinIO
  ├─── Split por silêncio (librosa.effects.split)
  ├─── Análise de pitch de cada grão (pYIN)
  ├─── Serializa grãos (pickle)
  ├─── Armazena em Redis (grains:{style_id})
  │
  ▼
Atualiza PostgreSQL
  │
  └─── grain_cache_key, grain_count, duration
```

### 3. Síntese e Mixagem

```
Cliente
  │
  ├─── POST /mix
  │      {config: {drums: {style_sound_id, volume}, ...}}
  │
  ▼
FastAPI
  │
  ├─── Valida projeto (status: "ready")
  ├─── Cria registro Mix (status: "queued")
  │
  ▼
Celery Task: create_mix
  │
  ├─── Para cada stem configurado:
  │     │
  │     ├─── Download stem base do MinIO
  │     ├─── Carrega biblioteca de grãos do Redis
  │     ├─── Detecta onsets (librosa.onset.onset_detect)
  │     ├─── Para cada onset:
  │     │     ├─── Analisa pitch (pYIN)
  │     │     ├─── Seleciona grão mais próximo
  │     │     ├─── Processa grão (envelope + amplitude)
  │     │     └─── Insere no buffer de saída
  │     │
  │     └─── Retorna stem sintetizado
  │
  ├─── Mixagem aditiva de todos stems
  ├─── Normalização (evita clipping)
  ├─── Export WAV
  ├─── Upload para MinIO (mixes/{mix_id}/)
  │
  ▼
Atualiza PostgreSQL
  │
  └─── status: "complete", output_path
```

---

## 🧩 Componentes de Processamento de Áudio

### 1. Separação de Stems (Demucs)

**Arquivo**: [src/services/stem_separator.py](src/services/stem_separator.py)

**Modelo**: `htdemucs_ft` (Hybrid Transformer Demucs Fine-Tuned)

**Saídas**:
- `vocals.wav` - Vocais isolados
- `drums.wav` - Bateria e percussão
- `bass.wav` - Baixo e sub-baixo
- `other.wav` - Outros instrumentos (guitarras, teclados, etc.)

**Hardware**: Requer GPU (CUDA) para performance aceitável

### 2. Detecção de Onsets

**Arquivo**: [src/services/onset_detector.py](src/services/onset_detector.py)

**Algoritmo**: `librosa.onset.onset_detect` com spectral flux

**Parâmetros**:
- `delta=0.06` - Threshold para detecção de picos
- `wait=1, pre_avg=1, post_avg=1, post_max=1` - Suavização temporal

**Saída**: Lista de posições (em samples) onde ocorrem eventos rítmicos

### 3. Análise de Pitch

**Arquivo**: [src/services/pitch_analyzer.py](src/services/pitch_analyzer.py)

**Algoritmo**: pYIN (Probabilistic YIN)

**Range**: C1 (32.7 Hz) a C7 (2093 Hz)

**Uso**:
- Determinar pitch de segmentos do stem original
- Selecionar grão com pitch mais próximo da biblioteca

### 4. Construção de Biblioteca de Grãos

**Arquivo**: [src/services/grain_builder.py](src/services/grain_builder.py)

**Processo**:
1. Split por silêncio (`librosa.effects.split`, `top_db=20`)
2. Filtra grãos muito curtos (< 512 samples)
3. Analisa pitch de cada grão (pYIN)
4. Calcula RMS (intensidade)
5. Serializa e armazena em Redis

**Estrutura do Grão**:
```python
@dataclass
class Grain:
    audio: np.ndarray  # Samples do grão
    pitch: float       # Frequência fundamental em Hz
    rms: float         # Root Mean Square (intensidade)
```

### 5. Síntese Granular

**Arquivo**: [src/services/granular_synth.py](src/services/granular_synth.py)

**Algoritmo**:
1. Detecta onsets no stem original
2. Para cada onset:
   - Analisa pitch do segmento
   - Seleciona grão com pitch mais próximo
   - Aplica envelope de decay exponencial
   - Ajusta amplitude baseada no peak do original
   - Insere no buffer de saída (mixagem aditiva)

**Parâmetros configuráveis**:
- `grain_duration_ms` - Duração do grão (padrão: 120ms)
- `use_pitch_mapping` - Usa mapeamento de pitch? (padrão: True)
- `use_envelope` - Aplica envelope? (padrão: True)

**Envelope**:
```python
envelope = np.linspace(1.0, 0.0, num=decay_samples)  # Decay linear
```

### 6. Mixer

**Arquivo**: [src/services/mixer.py](src/services/mixer.py)

**Processo**:
1. Combina stems com volumes individuais
2. Normaliza para evitar clipping (`max(abs(audio)) = 1.0`)
3. Exporta WAV (44100 Hz, mono)

---

## 🗄️ Modelos de Dados

### Project

```python
{
  "id": UUID,
  "name": str,
  "status": "created" | "separating" | "ready" | "error",
  "base_file_path": str,        # MinIO path
  "vocals_path": str,            # MinIO path
  "drums_path": str,             # MinIO path
  "bass_path": str,              # MinIO path
  "other_path": str,             # MinIO path
  "analysis_cache_key": str,     # Redis key
  "created_at": datetime,
  "updated_at": datetime
}
```

### StyleSound

```python
{
  "id": UUID,
  "name": str,
  "file_path": str,              # MinIO path
  "grain_cache_key": str,        # Redis key
  "grain_count": int,
  "duration_seconds": float,
  "created_at": datetime
}
```

### Mix

```python
{
  "id": UUID,
  "project_id": UUID,
  "status": "queued" | "processing" | "complete" | "error",
  "config": {
    "drums": {"style_sound_id": UUID, "volume": float, "enabled": bool},
    "bass": {...},
    "other": {...},
    "vocals": {"volume": float, "enabled": bool}
  },
  "settings": {
    "grain_duration_ms": int,
    "use_pitch_mapping": bool,
    "use_envelope": bool
  },
  "output_path": str,            # MinIO path
  "created_at": datetime,
  "completed_at": datetime
}
```

---

## 🔧 Configuração de Workers

### GPU Worker

**Hardware**: NVIDIA GPU com CUDA

**Tasks**: `tasks.separate_stems`

**Concorrência**: 1 (Demucs é I/O bound + GPU bound)

**Queue**: `gpu`

**Comando**:
```bash
celery -A src.tasks.celery_app worker --loglevel=info -Q gpu --concurrency=1
```

### CPU Workers

**Hardware**: CPUs multi-core

**Tasks**:
- `tasks.analyze_stems`
- `tasks.build_grain_library`
- `tasks.create_mix`

**Concorrência**: 4 (ajustar baseado em núcleos disponíveis)

**Queue**: `celery` (default)

**Comando**:
```bash
celery -A src.tasks.celery_app worker --loglevel=info --concurrency=4
```

---

## 📊 Performance e Escalabilidade

### Gargalos Identificados

1. **Separação Demucs**: ~30-60s para música de 3-4min (GPU)
2. **Síntese Granular**: ~5-15s por stem (CPU)
3. **Análise de Pitch**: ~2-5s por stem (CPU)

### Estratégias de Otimização

1. **Cache agressivo**: Grãos e análises nunca expiram (gerenciamento manual)
2. **Pré-download de modelos**: Demucs model incluído na imagem Docker
3. **Processamento paralelo**: Múltiplos workers CPU para análise/síntese
4. **Deduplicação**: Hash SHA256 para evitar reprocessamento

### Limites de Escala Atual

- **Uploads simultâneos**: Limitado por I/O do MinIO
- **Separações simultâneas**: 1 por GPU Worker
- **Sínteses simultâneas**: N (número de CPU workers)

### Escalabilidade Horizontal

- ✅ **API**: Múltiplas instâncias com load balancer
- ✅ **CPU Workers**: Adicionar mais workers Celery
- ⚠️ **GPU Workers**: Requer hardware adicional
- ✅ **PostgreSQL**: Read replicas para queries
- ✅ **Redis**: Redis Cluster para distribuição
- ✅ **MinIO**: Modo distribuído

---

## 🔒 Considerações de Segurança

### Implementado

- [x] Validação de tipos de arquivo (extensões)
- [x] Limite de tamanho de upload (100MB)
- [x] Hash de arquivos para deduplicação
- [x] Isolamento de arquivos por projeto/estilo (paths únicos)

### Recomendado para Produção

- [ ] Autenticação JWT na API
- [ ] Rate limiting por IP/usuário
- [ ] Validação de conteúdo de arquivo (magic numbers)
- [ ] Sanitização de nomes de arquivo
- [ ] HTTPS/TLS obrigatório
- [ ] Secrets management (Vault, AWS Secrets Manager)
- [ ] Assinatura de URLs do MinIO (presigned URLs com TTL curto)
- [ ] Auditoria de ações (logs estruturados)

---

## 📈 Monitoramento e Observabilidade

### Métricas Importantes

**API**:
- Taxa de requisições por endpoint
- Latência (p50, p95, p99)
- Taxa de erros (4xx, 5xx)

**Celery**:
- Tarefas em queue
- Tempo médio de processamento
- Taxa de falhas/retry

**Storage**:
- Uso de disco
- IOPS
- Largura de banda

**Database**:
- Pool de conexões
- Queries lentas
- Locks

### Ferramentas Recomendadas

- **Prometheus + Grafana**: Métricas e dashboards
- **Flower**: Monitoramento Celery
- **Sentry**: Error tracking
- **ELK Stack**: Logs centralizados

---

## 🧪 Testes

### Estratégia de Testes

**Unit Tests**:
- Serviços de processamento (`src/services/`)
- Validação de schemas (`src/api/v1/*/schemas.py`)

**Integration Tests**:
- Endpoints da API
- Tasks Celery (com mocks de I/O)

**E2E Tests**:
- Fluxo completo: Upload → Separação → Síntese → Download

### Fixtures de Teste

- Arquivo de áudio sintético (sine wave)
- Mock de resposta Demucs
- Biblioteca de grãos pré-processada

---

## 📚 Referências Técnicas

- **Demucs**: https://github.com/facebookresearch/demucs
- **librosa**: https://librosa.org/
- **pYIN**: https://www.eecs.qmul.ac.uk/~simond/pub/2014/MauchDixon-PYIN-ICASSP2014.pdf
- **Granular Synthesis**: Roads, Curtis (2001). Microsound. MIT Press.

---

Documentação técnica gerada a partir do plano de desenvolvimento do sistema de backend de mixagem de áudio.
