FROM ubuntu:22.04

RUN  useradd -rm -d /home/ubuntu -s /bin/bash -g root -G sudo -u 1000 ubuntu

RUN apt update && apt upgrade -y

ENV POETRY_VERSION=1.8.3

# Install packages needed to run your application (not build deps):
#   mime-support -- for mime types when serving static files
#   postgresql-client -- for running database commands
# We need to recreate the /usr/share/man/man{1..8} directories first because
# they were clobbered by a parent image.
RUN set -ex \
    && RUN_DEPS=" \
    libpcre3 \
    mime-support \
    mysql-client \
    postgresql-client \
    python3.11 \
    python3.11-dev \
    python3-pip \
    python3-dev \
    openssh-client \
    sshpass \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt update && apt install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /code/
WORKDIR /code/
ADD ./ /code/

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step.
# Correct the path to your production requirements file, if needed.
RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libpcre3-dev \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    " \
    && apt update && apt install -y --no-install-recommends $BUILD_DEPS \
    && python3.11 -m pip install "poetry==$POETRY_VERSION" \
    && python3.11 -m pip install pysftp \
    && python3.11 -m pip install pipdeptree \
    && poetry install --with wvnet \
    && mv .venv venv \
    && . ./venv/bin/activate \
    && pipdeptree > requirements.txt \
    && rm -r ./venv \