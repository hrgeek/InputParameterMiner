#!/bin/bash

# Install Python and pip (if not already installed)
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Installing Python3..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip
fi

# Install the tool using setup.py
echo "Installing Input Parameter Miner..."
pip3 install .

# Make the tool executable
echo "Making the tool executable..."
chmod +x input-parameter-miner

echo "Installation complete! You can now use the tool by typing 'input-parameter-miner' in your terminal."
