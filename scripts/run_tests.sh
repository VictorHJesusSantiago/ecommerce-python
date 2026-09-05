#!/bin/bash
set -e

echo "Running tests..."
python -m pytest tests/ -v --tb=short --cov=apps --cov-report=html

echo "Coverage report generated in htmlcov/"
