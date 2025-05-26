FROM python:3.12-slim

# Install minimal build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake libglib2.0-dev libsm6 libxext6 libxrender-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Pre-install dlib and face_recognition
RUN pip install --no-cache-dir dlib face_recognition

# Copy application code
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the application port
EXPOSE 8587

# Set environment variables
ENV FLASK_ENV=production
ENV GUNICORN_CMD_ARGS="--workers=1 --bind=0.0.0.0:8587"

# Run the application
CMD ["gunicorn", "main:app"]
