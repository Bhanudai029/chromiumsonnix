#!/usr/bin/env bash
set -o errexit

# Update package lists
apt-get update

# Install Chromium
apt-get install -y chromium-browser
