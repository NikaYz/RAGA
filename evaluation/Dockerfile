# evaluation/Dockerfile
FROM python:3.11-slim

WORKDIR /shaky_evaluator
COPY . .

RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt --no-cache-dir

CMD ["python3", "evaluate.py"]