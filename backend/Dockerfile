# Stage 1: Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /shakespeare

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies in a separate location
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Copy code into a clean image
FROM python:3.11-slim

WORKDIR /shakespeare

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy only the backend code
COPY . .

# Expose backend port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
