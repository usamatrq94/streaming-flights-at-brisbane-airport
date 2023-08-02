# Use the official Python base image
FROM python:3.11.4-bullseye as base

# Setup shared environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup"
ENV PATH="$POETRY_HOME/bin:$PATH"

WORKDIR $PYSETUP_PATH

FROM base as builder
# Install system dependencies
RUN apt-get update \
    && apt-get install -y curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Install Python dependencies
COPY poetry.lock pyproject.toml ./
RUN --mount=type=ssh poetry install --no-root --without dev --all-extras

FROM builder as application
# Set working directory
WORKDIR /app

ENV PYTHONPATH="$PWD/bin:$PYTHONPATH"

# Copy the source code into the container
COPY . .
