# Use the official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the Pipfiles
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install --upgrade pip pipenv && pipenv install --system --deploy

# Verify flask-restx installation
RUN python -c "import flask_restx; print('flask-restx installed successfully')"

# Copy the application code
COPY wsgi.py .
COPY service/ ./service/

# Set non-root user (optional, but good for security)
RUN useradd --uid 1001 flask && chown -R flask /app

# Expose the port
EXPOSE 8080

# Switch to non-root user
USER flask

# Start the service
CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:app"]