FROM mcr.microsoft.com/devcontainers/python:1-3.11

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Install global npm packages
RUN npm install -g \
    typescript \
    eslint \
    prettier

# Set working directory
WORKDIR /workspace

# Set default user
USER vscode

# Keep container running
CMD ["sleep", "infinity"]

