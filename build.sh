#!/usr/bin/env bash
# build.sh - Custom build script for Render

# Install build dependencies
echo "Installing build dependencies..."
apt-get update && apt-get install -y build-essential libffi-dev python3-dev

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Explicitly install Flask and core dependencies first
echo "Installing Flask and core dependencies..."
pip install flask==3.1.0
pip install flask-login==0.6.3
pip install flask-sqlalchemy==3.1.1
pip install flask-wtf==1.2.2
pip install requests==2.32.3
pip install werkzeug==3.1.3

# Explicitly install gunicorn
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

# Install firebase-admin separately
echo "Installing firebase-admin..."
pip install firebase-admin==6.2.0

# Install MongoDB-related packages
echo "Installing MongoDB dependencies..."
# Remove standalone bson if it exists (it conflicts with pymongo's bson module)
pip uninstall -y bson
# Install pymongo first, which includes its own bson module
pip install pymongo==4.4.0
pip install flask-pymongo==2.3.0
# Do NOT install standalone bson package

# Install remaining packages
echo "Installing remaining dependencies..."
pip install email-validator>=2.2.0
pip install psycopg2-binary>=2.9.10
pip install trafilatura>=2.0.0
pip install wtforms>=3.2.1
pip install oauthlib>=3.2.2

# Verify key packages are installed correctly
echo "Verifying installations..."
pip list | grep flask
pip list | grep gunicorn
pip list | grep pymongo
pip list | grep pyrebase

# Add gunicorn to PATH if needed
echo "Adding Python bin directory to PATH..."
export PATH=$PATH:$(python -c "import sys; print(sys.prefix)")/bin
echo "Updated PATH: $PATH"

# Create a .env file with the path
echo "Creating .env file with PATH..."
echo "export PATH=$PATH" > .env

echo "Build completed successfully"
