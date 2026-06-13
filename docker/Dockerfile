# Reproducible image for the eval standard. Pinned base + pinned deps mean
# any machine builds the same environment — the core reproducibility claim.
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

# torch CPU wheel from the dedicated index, pinned to match dev.
RUN pip install --no-cache-dir torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is copied (not bind-mounted) so the image is self-contained.
COPY eval_lib/ eval_lib/
COPY paper-registry/ paper-registry/
COPY experiments/ experiments/
COPY tools/ tools/
COPY tests/ tests/

# Real commit baked in at build time (no .git in the image).
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}

CMD ["python", "experiments/distilbert-sst2/reproduce.py"]
