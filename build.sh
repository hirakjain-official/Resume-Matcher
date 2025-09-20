#!/bin/bash

# Exit on any error
set -e

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p temp
mkdir -p results
mkdir -p out

# Set appropriate permissions
echo "Setting permissions..."
chmod -R 755 uploads temp results out

echo "Build completed successfully!"