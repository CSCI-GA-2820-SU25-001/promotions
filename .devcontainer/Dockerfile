# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:sp25

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

# Verify flask-restx installation
RUN python -c "import flask_restx; print('flask-restx installed successfully')" || \
    (echo "Installing flask-restx manually..." && sudo pip install flask-restx)

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp && bash ./install-tools.sh
