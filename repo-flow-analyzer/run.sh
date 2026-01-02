#!/bin/bash

# Enterprise Spring Boot Repository Analyzer
# Bash script to run the analyzer on Unix-like systems

echo ""
echo "==================================================="
echo " Enterprise Spring Boot Repository Analyzer"
echo "==================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

# Get Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python: $python_version"
echo ""

# Get repository path
if [ -z "$1" ]; then
    echo "Usage: ./run.sh <repository_path> [output_dir]"
    echo ""
    echo "Examples:"
    echo "  ./run.sh /path/to/spring-boot-project"
    echo "  ./run.sh /path/to/repo my-analysis"
    echo ""
    read -p "Enter repository path: " repo_path
else
    repo_path="$1"
fi

# Validate repository path
if [ ! -d "$repo_path" ]; then
    echo "Error: Repository path does not exist: $repo_path"
    exit 1
fi

# Get output directory
if [ -z "$2" ]; then
    output_dir="repo-analysis-output"
else
    output_dir="$2"
fi

echo "Repository: $repo_path"
echo "Output Dir: $output_dir"
echo ""
echo "Starting analysis..."
echo ""

# Run the analyzer
python3 "$(dirname "$0")/main.py" --repo "$repo_path" --out "$output_dir"

if [ $? -ne 0 ]; then
    echo ""
    echo "Error: Analysis failed"
    exit 1
fi

echo ""
echo "Analysis complete! Results saved to:"
echo "$repo_path/$output_dir"
echo ""
