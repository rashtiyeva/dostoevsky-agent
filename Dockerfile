FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/app/.cache/huggingface

WORKDIR /app

COPY requirements.txt ./

# Install CPU-only PyTorch to avoid unnecessary CUDA dependencies.
RUN python -m pip install --index-url https://download.pytorch.org/whl/cpu torch \
    && python -m pip install -r requirements.txt

RUN useradd --create-home --uid 10001 app \
    && mkdir -p /home/app/.cache/huggingface \
    && chown -R app:app /home/app/.cache

COPY agent/ ./agent/
COPY app/ ./app/
COPY chunking/ ./chunking/
COPY embeddings/ ./embeddings/
COPY frontend/ ./frontend/
COPY generation/ ./generation/
COPY indexing/ ./indexing/
COPY ingestion/ ./ingestion/
COPY retrieval/ ./retrieval/
COPY tools/ ./tools/
COPY vector_store/ ./vector_store/
COPY scripts/index_corpus.py scripts/docker_start.py ./scripts/
COPY data/books/ ./data/books/

USER app

EXPOSE 8000

ENTRYPOINT ["python", "-m", "scripts.docker_start"]
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]