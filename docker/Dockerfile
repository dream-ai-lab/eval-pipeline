# Reproducible image for the eval standard. Pinned base + pinned deps mean
# any machine builds the same environment — the core reproducibility claim.
# eval_lib is no longer vendored here; it is installed as a pinned dependency
# (eval-lib @ v0.1.0) from requirements.txt.
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1

# git is needed for pip to install eval-lib from its git tag.
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source is copied (not bind-mounted) so the image is self-contained.
# paper-registry is a git submodule; its checked-out contents are copied.
COPY paper-registry/ paper-registry/
COPY experiments/ experiments/
COPY tools/ tools/

# Real commit baked in at build time (no .git in the image).
ARG GIT_COMMIT=unknown
ENV GIT_COMMIT=${GIT_COMMIT}

CMD ["python", "experiments/distilbert-sst2/reproduce.py"]
