# ----------------------------------------------------------------------------
# Stage 1: Builder
# ----------------------------------------------------------------------------
FROM public.ecr.aws/unocha/python:3.13-stable AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Keep WORKDIR consistent to avoid confusion, though less critical with non-editable
WORKDIR /app

# 1. Install system deps
RUN --mount=type=cache,target=/var/cache/apk \
    apk add --upgrade git

# 2. Install Dependencies (Cached Layer)
COPY pyproject.toml uv.lock ./
#    --no-install-project: Installs libraries (pandas, etc.) but NOT your code yet
RUN uv sync --frozen --no-dev --no-install-project --compile

# 3. Install Your Project (Non-Editable)
COPY . .
#    We use 'uv pip install' here to force a non-editable install into the venv.
#    This packs your code into /app/.venv/lib/python3.13/site-packages/
RUN uv pip install --no-deps .

# ----------------------------------------------------------------------------
# Stage 2: Final Runtime
# ----------------------------------------------------------------------------
FROM public.ecr.aws/unocha/python:3.13-stable

WORKDIR /app

# 1. Copy the Virtual Environment
#    Since we did a non-editable install, your code is INSIDE this folder now.
ENV VIRTUAL_ENV=/app/.venv
COPY --from=builder /app/.venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# 2. Run
CMD ["python3", "run.py"]
