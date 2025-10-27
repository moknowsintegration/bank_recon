#!/bin/bash

echo "========================================"
echo " Bank Reconciliation System"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
    echo
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade requirements
echo "Checking dependencies..."
pip install -r requirements.txt --quiet

# Run the main script
echo
echo "Starting reconciliation..."
echo "========================================"
python main.py

echo
echo "========================================"
echo "Reconciliation complete!"
echo "Check the data/output folder for your report."
echo