#!/usr/bin/env bash
# Exit on error
# set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright and its dependencies
playwright install
playwright install-deps
