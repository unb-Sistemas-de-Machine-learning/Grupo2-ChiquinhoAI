FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir qdrant-client

COPY init.py .

CMD ["python", "init.py"]
