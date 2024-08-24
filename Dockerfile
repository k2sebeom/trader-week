FROM python:3.10-buster as builder
# Setup environment
RUN pip install -U pip && pip install --no-cache-dir pipenv

ENV PIPENV_VERBOSITY=-1 \
    PIPENV_VENV_IN_PROJECT=1

WORKDIR /app

# Install Dependencies
COPY Pipfile Pipfile.lock ./
RUN pipenv install --clear --categories packages

FROM python:3.10-slim

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy source code
COPY . .

CMD ["python3", "main.py"]
