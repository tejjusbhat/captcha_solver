FROM python:3.11.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port that Uvicorn will listen on
EXPOSE 8080

# Set a default value for PORT if not passed as an environment variable
ENV PORT 8080

# Use the default PORT environment variable or 8080 if not set
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
