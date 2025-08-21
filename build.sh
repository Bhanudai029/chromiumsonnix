#!/usr/bin/env bash
set -euxo pipefail

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Playwright browsers..."
playwright install chromium

echo "Verifying Playwright Chromium installation:"
ls -l /opt/render/.cache/ms-playwright/
ls -l /opt/render/.cache/ms-playwright/chromium_headless_shell*/chrome-linux/ || true
ls -l /opt/render/.cache/ms-playwright/chromium*/chrome-linux/ || true
