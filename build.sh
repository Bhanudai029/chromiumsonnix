#!/usr/bin/env bash
set -euxo pipefail

CHROMIUM_DIR="/opt/render/project/chromium"
CHROMIUM_VERSION="120.0.6099.109" # A recent, stable Chromium build
CHROMIUM_URL="https://storage.googleapis.com/chromium-browser-snapshots/Linux_x64/${CHROMIUM_VERSION}/chrome-linux.zip"

mkdir -p "${CHROMIUM_DIR}"

echo "Downloading Chromium ${CHROMIUM_VERSION} from ${CHROMIUM_URL}"
curl -L "${CHROMIUM_URL}" -o "${CHROMIUM_DIR}/chrome-linux.zip"

echo "Extracting Chromium..."
unzip "${CHROMIUM_DIR}/chrome-linux.zip" -d "${CHROMIUM_DIR}"

echo "Setting executable permissions..."
chmod +x "${CHROMIUM_DIR}/chrome-linux/chrome"

# Rename the extracted directory to simplify path, if necessary
mv "${CHROMIUM_DIR}/chrome-linux" "${CHROMIUM_DIR}/chrome"

echo "Verifying Chromium installation:"
ls -l "${CHROMIUM_DIR}/chrome/chrome"
"${CHROMIUM_DIR}/chrome/chrome" --version

echo "Chromium setup complete. Installing Python dependencies..."

pip install -r requirements.txt
