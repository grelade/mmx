# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

ARG PYTHON_VERSION=3.9.16
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

ENV NUMBA_CACHE_DIR=/tmp/numba_cache

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /mmx_app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
ARG UID=10001
ARG GID=1000

RUN addgroup --gid ${GID} www
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/bin/sh" \
    --no-create-home \
    --uid "${UID}" \
    --gid ${GID} \
    www


# ARG GROUP_ID=1000
# ARG USER_ID=1000
# # Add user for flask application
# RUN addgroup --gid 1000 www
# RUN adduser -D --uid 1000 -G www www --shell /bin/sh

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.

RUN --mount=type=cache,target=/home/grela/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# RUN pip install gunicorn
#numba tmp directory hack

# Switch to the non-privileged user to run the application.

ENV TORCH_HOME=/tmp/torch_cache

# USER appuser
USER www

# EXPOSE 8002
# CMD [ "gunicorn", "-w", "4", "--bind", "0.0.0.0:8002", "wsgi"]


# Copy the source code into the container.
# COPY . .

# Expose the port that the application listens on.
# EXPOSE 8000

# Run the application.
# CMD python server_api.py
# CMD gunicorn 'server_api:app' --bind=0.0.0.0:8000
