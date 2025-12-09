# docker/worker-gpu/Dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3.11 /usr/bin/python

COPY requirements.txt .
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Pre-download Demucs model (já incluído no requirements.txt)
RUN python3.11 -c "import torch; print('PyTorch version:', torch.__version__)"
RUN python3.11 -c "import demucs; print('Demucs installed successfully')"

COPY src/ ./src/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["celery", "-A", "src.tasks.celery_app", "worker", "--loglevel=info", "-Q", "gpu", "--concurrency=1"]
