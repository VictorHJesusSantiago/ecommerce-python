#!/bin/bash
set -e

echo "Formatting code..."
black apps/
isort apps/
echo "Formatting complete!"
