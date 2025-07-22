#!/bin/bash
# Script to rebuild and test the dev container

echo "**********************************************************************"
echo "Rebuilding Dev Container..."
echo "**********************************************************************"

# Navigate to the workspace root
cd /app

# Rebuild the dev container
echo "Building container image..."
docker-compose -f .devcontainer/docker-compose.yml build --no-cache

echo "**********************************************************************"
echo "Testing flask-restx installation..."
echo "**********************************************************************"

# Start a temporary container to test
docker-compose -f .devcontainer/docker-compose.yml run --rm app python -c "import flask_restx; print('✅ flask-restx successfully installed and importable')"

echo "**********************************************************************"
echo "Container rebuild complete!"
echo "**********************************************************************"
echo "You can now open the container in VS Code using:"
echo "1. Command Palette (Ctrl+Shift+P)"
echo "2. 'Dev Containers: Reopen in Container'"
