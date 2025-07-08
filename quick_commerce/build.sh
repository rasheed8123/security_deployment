#!/bin/bash
set -e

# Install system dependencies for Pillow
apt-get update
apt-get install -y libjpeg-dev zlib1g-dev libpng-dev

# Install Python packages
pip install --no-cache-dir -r requirements.txt 