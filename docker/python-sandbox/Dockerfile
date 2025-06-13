# docker/python-sandbox/Dockerfile
FROM python:3.12-slim

WORKDIR /sandbox

COPY runner.py .

RUN pip install --no-cache-dir pytest

ENTRYPOINT ["python", "runner.py"]
