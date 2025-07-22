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

echo "**********************************************************************"
echo "Setup complete"
echo "**********************************************************************"
