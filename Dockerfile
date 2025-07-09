# Use official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc
# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev

# Copy Pipfiles
COPY Pipfile Pipfile.lock ./

# Install Python dependencies
RUN pip install pipenv && pipenv install --system --deploy

# ✅ Install psycopg2-binary manually
RUN pip install psycopg2-binary

# Copy application code
COPY wsgi.py .
COPY service/ ./service/

# Create a non-root user and switch
RUN useradd --uid 1001 flask && chown -R flask /app
USER flask

# Command to run the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:app"]