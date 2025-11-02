# The builder image, used to build the virtual environment
FROM python:3.11.3 AS builder

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
    wget \
    " \
    && apt update \
    && apt upgrade -y \
    && apt install -y --no-install-recommends $BUILD_DEPS \
    && touch README.md \
    && poetry install --with wvnet --no-root \
    && rm -rf $POETRY_CACHE_DIR \
    && pipdeptree -fl --exclude poetry --exclude pipdeptree --python /app/.venv/bin/python > requirements.txt

# Test stage - contains dev dependencies for testing
# Tests are now run in Jenkins before the build, not during Docker build
FROM builder AS test

# Install dev dependencies for testing
RUN poetry install --with dev --no-root

COPY ./ ./

# Test stage is ready for running tests in Jenkins
# Tests will be executed by Jenkins using: /app/.venv/bin/pytest ...

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
COPY ./ ./

# Copy virtual env from previous step
COPY --from=builder /app/requirements.txt ./

RUN useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 ubuntu \
    && apt update \
    && apt upgrade -y \
    && apt install openssh-client wget -y \
    && pip install paramiko==3.5.1  pysftp \
    && rm ./poetry.toml \
    && mkdir /wsgi \
    && cp ./src/parts_webapi/wsgi.py /wsgi/wsgi.py \
    && mkdir /scripts \
    && cd /scripts \
    && wget https://raw.githubusercontent.com/bduke-dev/scripts/main/delete_remote_files.py \
    && wget https://raw.githubusercontent.com/bduke-dev/scripts/main/upload_directory.py