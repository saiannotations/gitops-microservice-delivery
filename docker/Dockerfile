# NOTE: this is the first version of the Dockerfile on purpose.
# It works, but the base image is large and carries known CVEs.
# See the repo issues/history for how it gets hardened.
FROM python:3.12

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.orders:app", "--host", "0.0.0.0", "--port", "8000"]
