# Use the official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the Pipfiles
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Copy the application code
COPY wsgi.py .
COPY service/ ./service/

# Set non-root user (optional, but good for security)
RUN useradd --uid 1001 flask && chown -R flask /app
USER flask

# Start the service
CMD ["gunicorn", "-b", "0.0.0.0:8080", "wsgi:app"]