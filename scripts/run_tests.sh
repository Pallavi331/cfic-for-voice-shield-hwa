#!/usr/bin/env bash
# Run the full CFIC test suite using virtual environment
set -e
echo "Running CFIC test suite..."
python3 -m pytest -v
