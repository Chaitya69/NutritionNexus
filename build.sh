#!/usr/bin/env bash
# build.sh - Custom build script for Render

# Install build dependencies
echo "Installing build dependencies..."
apt-get update && apt-get install -y build-essential libffi-dev python3-dev

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Explicitly install gunicorn first to ensure it's available
echo "Installing gunicorn..."
pip install gunicorn==23.0.0

# Explicitly install pycryptodome first to prevent pycrypto installation
echo "Installing pycryptodome..."
pip install pycryptodome==3.18.0

# Explicitly install cryptography
echo "Installing cryptography..."
pip install cryptography>=41.0.0

# Install pyrebase4 with specific version
echo "Installing pyrebase4..."
pip install pyrebase4==4.6.0

# Install the rest of dependencies but exclude pycrypto
echo "Installing remaining requirements..."
grep -v "pycrypto" requirements.txt | grep -v "pyrebase" | xargs pip install

# Install firebase-admin separately
echo "Installing firebase-admin..."
pip install firebase-admin==6.2.0

# Verify gunicorn installation
echo "Verifying gunicorn installation..."
which gunicorn || echo "ERROR: gunicorn not found in PATH"
pip list | grep gunicorn

# Add gunicorn to PATH if needed
echo "Adding Python bin directory to PATH..."
export PATH=$PATH:$(python -c "import sys; print(sys.prefix)")/bin
echo "Updated PATH: $PATH"

echo "Build completed successfully"
