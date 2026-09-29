# Container image for Hugging Face Spaces (Docker SDK, free CPU hardware).
# Local development and the Render deployment do not use this file.

FROM python:3.12-slim

# Spaces run the container as a non-root user with uid 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR $HOME/app

# Install the CPU-only PyTorch build first (the default Linux build bundles
# several GB of CUDA libraries that CPU hardware can't use), then the app.
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Download the embedding model at build time so it is baked into the image:
# no download when the Space starts, and no dependency on the Hub at runtime.
ARG EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV EMBEDDING_MODEL=$EMBEDDING_MODEL
RUN python -c "import os; from sentence_transformers import SentenceTransformer; SentenceTransformer(os.environ['EMBEDDING_MODEL'], device='cpu')"

COPY --chown=user . .

# Keep semantic similarity on, and load the model at startup so the first
# analysis is fast.
ENV SEMANTIC_ENABLED=true \
    PRELOAD_EMBEDDING_MODEL=true

# Spaces route traffic to port 7860 (matches `app_port` in README.md).
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
