# Base image
FROM python:3.11-slim

# Working directory
WORKDIR /app

# Copy your app files
COPY . /app

# Install system dependencies for MySQL client
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config

# Install Python dependencies
RUN pip install --no-cache-dir flask flask-mysqldb mysqlclient

# Expose Flask port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask app
CMD ["flask", "run"]
