# FlowGuard's API, with the embedding model built in.
FROM python:3.13.18-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/opt/huggingface

WORKDIR /app

# CPU-only PyTorch: the embedding model is small, and the CUDA build adds about
# 2 GB. The model that needs a GPU runs in Ollama, outside this image.
RUN pip install torch==2.15.0 --index-url https://download.pytorch.org/whl/cpu

# Dependencies first, so a code change doesn't reinstall them.
# The package metadata includes the licence, so the build needs it.
COPY pyproject.toml LICENSE ./
COPY src ./src
# Editable, so the code finds the seeded data next to it, in /app/data.
RUN pip install -e .

# Download the embedding model now, so the container starts without the internet.
RUN python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('BAAI/bge-small-en-v1.5')"

COPY data ./data

# Run as an ordinary user, with the databases on a volume it owns.
RUN useradd --create-home flowguard \
    && mkdir -p /var/lib/flowguard \
    && chown flowguard /var/lib/flowguard
USER flowguard

ENV HF_HUB_OFFLINE=1 \
    FLOWGUARD_AUDIT_DB=/var/lib/flowguard/audit.db \
    FLOWGUARD_CHECKPOINT_DB=/var/lib/flowguard/checkpoints.db

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=90s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/ready')"

CMD ["uvicorn", "flowguard.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
