# ------------------------------------------------------------
# 1️⃣ Builder stage – builds the virtual environment
# ------------------------------------------------------------
FROM python:3.11.3 AS builder

# Build argument to select dependency group (wvnet or uat)
ARG DEPENDENCY_GROUP=wvnet

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry==2.1.4 \
    && pip install pipdeptree \
    && set -ex \
    && BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libpq-dev \
        default-libmysqlclient-dev \
        pkg-config \
        " \
    && apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends $BUILD_DEPS \
    && touch README.md \
    && poetry install --with ${DEPENDENCY_GROUP} --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && pipdeptree -fl --exclude poetry --exclude pipdeptree --python /app/.venv/bin/python > requirements.txt

# ------------------------------------------------------------
# Test stage - contains dev dependencies for testing
# Tests are now run in Jenkins before the build, not during Docker build
# ------------------------------------------------------------
FROM builder AS test

# Install dev dependencies for testing
RUN poetry install --with dev --no-root

COPY ./ ./

# Test stage is ready for running tests in Jenkins
# Tests will be executed by Jenkins using: /app/.venv/bin/pytest ...

# ------------------------------------------------------------
# 2️⃣ Runtime stage – the production runtime environment
# ------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Build argument for deployment environment (main or uat)
ARG DEPLOY_ENV=main

# ── Expose the HTTP port that uWSGI will listen on ────────────────────────
EXPOSE 9090

# ── Environment variables ───────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:${PATH}" \
    PYTHONPATH=/app/src \
    UWSGI_WSGI_FILE=src/parts_webapi/wsgi.py \
    UWSGI_HTTP=:9090 \
    UWSGI_MASTER=1 \
    UWSGI_HTTP_AUTO_CHUNKED=1 \
    UWSGI_HTTP_KEEPALIVE=1 \
    UWSGI_LAZY_APPS=1 \
    UWSGI_WSGI_ENV_BEHAVIOR=holy \
    UWSGI_WORKERS=2 \
    UWSGI_THREADS=4 \
    LIB_SSL=libssl1.1_1.1.1f-1ubuntu2.24_amd64.deb

# ── Runtime dependencies (no build‑deps) ─────────────────────────────────────
RUN RUN_DEPS=" \
        postgresql-client \
        libxml2 \
        cron \
        curl \
        gosu \
    " \
    && mkdir -p /usr/share/man/man{1..8} \
    && apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/${LIB_SSL} -o ${LIB_SSL} \
    && dpkg -i ${LIB_SSL} \
    && rm ${LIB_SSL}

# ── Working directory ───────────────────────────────────────────────────────
WORKDIR /app

# ── Pull the virtual‑env built in the previous stage ───────────────────────
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# ── Copy application source code ───────────────────────────────────────────
COPY ./ /app

# ── Create the non‑privileged user (UID/GID 1000) ────────────────────────
RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser -s /bin/bash appuser

# ── Set up the crontab (runs as root) ─────────────────────────────────────
RUN mv ./crontab /etc/cron.d/myjob \
    && chmod 0644 /etc/cron.d/myjob \
    && crontab /etc/cron.d/myjob \
    && touch /var/log/cron.log \
    && chmod 666 /var/log/cron.log   # writable for any user (including appuser)

# ── For main branch: setup deployment scripts and wsgi ────────────────────
RUN if [ "${DEPLOY_ENV}" = "main" ]; then \
        apt update && apt install -y openssh-client wget && rm -rf /var/lib/apt/lists/* && \
        pip install paramiko==3.5.1 pysftp && \
        mkdir /wsgi && \
        cp ./src/parts_webapi/wsgi.py /wsgi/wsgi.py && \
        mkdir /scripts && \
        cd /scripts && \
        wget https://raw.githubusercontent.com/bduke-dev/scripts/main/delete_remote_files.py && \
        wget https://raw.githubusercontent.com/bduke-dev/scripts/main/upload_directory.py; \
    fi

# ── Health‑check ───────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD sh -c '\
    pid_file="/var/run/crond.pid"; \
    [ -f "$pid_file" ] && \
    pid=$(cat "$pid_file") && \
    [ -d "/proc/$pid" ] && exit 0; \
    exit 1'

# ── ENTRYPOINT / CMD ───────────────────────────────────────────────────────
#   • `cron -f` stays in the foreground (runs as root)  
#   • `gosu appuser uwsgi …` drops to the non‑privileged user **only** for uWSGI
CMD ["sh", "-c", "cron -f & exec gosu appuser uwsgi --show-config"]