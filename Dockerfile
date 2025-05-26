FROM docker.io/python:3.12

# Set the working directory
WORKDIR /

# Install necessary tools and libraries
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip git cmake build-essential \
        libboost-all-dev libopenblas-dev liblapack-dev \
        libglib2.0-dev libsm6 libxext6 libxrender-dev

# Copy application files
COPY . /

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set Gunicorn command-line arguments
ENV GUNICORN_CMD_ARGS="--workers=1 --bind=0.0.0.0:8587"

# Expose the application port
EXPOSE 8587

# Define environment variable
ENV FLASK_ENV=production

# Run the application
CMD ["gunicorn", "main:app"]
