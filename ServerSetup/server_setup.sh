#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Function to print messages with date and time
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')] $@"
}

# Ensure the script is run as a normal user, not root
if [[ $EUID -eq 0 ]]; then
    log "This script should not be run using sudo or as the root user"
    exit 1
fi

# Update package lists and Upgrade system
log "Updating and upgrading package lists..."
sudo apt-get update && sudo apt-get upgrade -y

# Check for CUDA compatibility (Assuming the user has an NVIDIA GPU)
log "Checking for NVIDIA GPU..."
if ! lspci | grep -i nvidia > /dev/null; then
    log "No NVIDIA GPU detected. Skipping CUDA installation."
else
    # Install CUDA Toolkit
    log "Installing CUDA Toolkit..."
    sudo apt install -y nvidia-cuda-toolkit
    
    # Check if CUDA installation was successful
    cuda_installed=$(which nvcc)
    if [[ -n $cuda_installed ]]; then
        log "CUDA Toolkit installation was successful."
    else
        log "CUDA Toolkit installation failed."
        exit 1
    fi
fi

# Download Miniforge installer
log "Downloading Miniforge installer..."
wget -q https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O Miniforge3-Linux-x86_64.sh

# Make Miniforge installer executable
log "Making Miniforge installer executable..."
chmod +x Miniforge3-Linux-x86_64.sh

# Install Miniforge
log "Installing Miniforge..."
./Miniforge3-Linux-x86_64.sh -b -p "$HOME/miniforge3"

# Initialize Miniforge
log "Initializing Miniforge..."
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"
mamba init

# Create a new conda environment with Mamba
log "Creating a new conda environment with Mamba..."
mamba create -n llm python=3.10 -y

# Activate the conda environment
log "Activating the conda environment..."
source $HOME/miniforge3/bin/activate llm

# Install machine learning libraries using Mamba
log "Installing machine learning libraries..."
mamba install -y numpy scipy matplotlib ipython jupyter pandas sympy nose scikit-learn transformers

# Cleanup downloaded files
log "Cleaning up..."
rm Miniforge3-Linux-x86_64.sh

# Post-installation test
log "Testing the machine learning environment..."
if python -c "import transformers"; then
    log "All packages imported successfully!"
else
    log "There was a problem importing one of the libraries."
    exit 1
fi

# Interactive prompt for a system reboot
read -p "Installation is complete. It is recommended to reboot your system. Would you like to reboot now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    log "Rebooting now."
    sudo reboot
fi

# Finish
log "Setup complete. Machine learning environment is ready."
log "Activate it using: conda activate llm"