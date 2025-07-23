#!/bin/bash
#
# These must be installed as a user and therefore need to be run
# after the container has been created.
#
echo "**********************************************************************"
echo "Setting up Docker user development environment..."
echo "**********************************************************************"

echo "Setting up registry.local..."
sudo bash -c "echo '127.0.0.1    cluster-registry' >> /etc/hosts"

echo "Making git stop complaining about unsafe folders"
git config --global --add safe.directory /app

echo "Installing Python dependencies with pipenv..."
cd /app && pipenv install --dev

echo "Verifying flask-restx installation..."
if ! python -c "import flask_restx" 2>/dev/null; then
    echo "WARNING: flask-restx not found, installing manually..."
    pip install flask-restx
    echo "flask-restx installed successfully"
else
    echo "flask-restx is already installed"
fi

echo "Ensuring port 8080 is free for development..."
# Kill any processes that might be using port 8080
sudo fuser -k 8080/tcp 2>/dev/null || echo "Port 8080 is free"

# Also kill any lingering gunicorn processes
pkill -f "gunicorn.*wsgi:app" 2>/dev/null || echo "No gunicorn processes found"

# Wait for cleanup
sleep 2

echo "**********************************************************************"
echo "Setup complete"
echo "**********************************************************************"
