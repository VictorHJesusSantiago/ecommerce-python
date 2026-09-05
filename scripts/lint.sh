#!/bin/bash
set -e

echo "Running linting..."
flake8 apps/ --max-line-length=120 --ignore=E501,W503
black --check apps/
isort --check-only apps/

echo "Linting complete!"
