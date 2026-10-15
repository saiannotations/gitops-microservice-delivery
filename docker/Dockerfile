# Multi-stage build: dependencies are compiled in the builder stage,
# and only the installed packages + app code ship in the final image.
FROM python:3.12-slim AS builder

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r app/requirements.txt

FROM python:3.12-slim

# Smallest possible attack surface: no build tools, no root user.
RUN useradd --create-home --uid 1000 appuser

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "app.orders:app", "--host", "0.0.0.0", "--port", "8000"]
