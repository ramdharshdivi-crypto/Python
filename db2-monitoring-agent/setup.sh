#!/bin/bash
# Setup script for DB2 Monitoring Agent (Linux/Mac)

set -e

echo "========================================"
echo "DB2 & Kubernetes Monitoring Agent Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "Step 1: Creating virtual environment..."
uv venv

echo ""
echo "Step 2: Activating virtual environment..."
source .venv/bin/activate

echo ""
echo "Step 3: Installing dependencies..."
uv pip install -r requirements.txt --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple --allow-insecure-host pypi.ci.artifacts.walmart.com

echo ""
echo "Step 4: Creating config file from example..."
if [ ! -f config.yaml ]; then
    cp config.example.yaml config.yaml
    echo "Created config.yaml - PLEASE EDIT THIS FILE with your settings!"
else
    echo "config.yaml already exists, skipping..."
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit config.yaml with your DB2 and Kubernetes settings"
echo "2. Run the monitoring agent:"
echo "   source .venv/bin/activate"
echo "   python main.py"
echo ""
echo "For help:"
echo "   python main.py --help"
echo ""
