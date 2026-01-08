# Build Stage
FROM python:3.10-slim-bullseye as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY pyproject.toml .
# Install dependencies into server_inventory.egg-info and get requirements
# We'll use a trick to install dependencies into a virtual environment or just user install
# Install dependencies into wheels directory
COPY . .
RUN pip wheel --no-cache-dir --wheel-dir /app/wheels ".[test]"

# Runtime Stage
FROM python:3.10-slim-bullseye

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Install Runtime Dependencies
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/pyproject.toml .

# Install dependencies from wheels
RUN pip install --no-cache /wheels/*

COPY . /app

# Change ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
