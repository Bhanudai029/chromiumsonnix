#!/usr/bin/env bash
set -euxo pipefail

# Update package lists
apt-get update

# Install Chromium
apt-get install -y chromium-browser

# Verify Chromium installation
ls -l /usr/bin/chromium*
which chromium-browser || echo "chromium-browser not found in PATH"
