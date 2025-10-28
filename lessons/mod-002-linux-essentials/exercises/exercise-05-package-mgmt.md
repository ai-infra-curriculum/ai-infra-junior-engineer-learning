# Exercise 05: Package Management for ML Stack Installation

## Overview

This exercise teaches you to install and manage software packages for ML infrastructure using Linux package managers. You'll learn to install Python, CUDA, Docker, ML frameworks, and manage dependencies across different Linux distributions. These skills are essential for setting up ML development and production environments.

## Learning Objectives

By completing this exercise, you will:
- Understand different package management systems (apt, yum, dnf)
- Install system packages and development tools
- Manage Python packages with pip and conda
- Install CUDA and GPU drivers
- Set up Docker and container runtime
- Install ML frameworks (TensorFlow, PyTorch)
- Handle dependency conflicts and version management
- Create reproducible installation scripts

## Prerequisites

- Completed Exercises 01-04
- Completed Lecture 04: System Administration Basics (package management section)
- Access to a Linux system (Ubuntu/Debian or RHEL/CentOS)
- Sudo privileges (for system package installation)
- Internet connection for downloading packages

## Time Required

- Estimated: 75-90 minutes
- Difficulty: Intermediate

## Part 1: System Package Management

### Step 1: Understanding Package Managers

```bash
# Create workspace
mkdir -p ~/package-management-lab
cd ~/package-management-lab

# Detect your distribution
cat > detect_distro.sh << 'EOF'
#!/bin/bash
# Detect Linux distribution and package manager

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "Distribution: $NAME"
        echo "Version: $VERSION"
        echo "ID: $ID"
        echo ""

        case $ID in
            ubuntu|debian)
                echo "Package Manager: apt"
                echo "Update command: sudo apt update"
                echo "Install command: sudo apt install <package>"
                echo "Search command: apt search <package>"
                ;;
            centos|rhel|fedora)
                if command -v dnf &> /dev/null; then
                    echo "Package Manager: dnf"
                    echo "Update command: sudo dnf check-update"
                    echo "Install command: sudo dnf install <package>"
                else
                    echo "Package Manager: yum"
                    echo "Update command: sudo yum check-update"
                    echo "Install command: sudo yum install <package>"
                fi
                ;;
            *)
                echo "Package Manager: Unknown"
                ;;
        esac
    else
        echo "Cannot detect distribution"
    fi
}

detect_distro

# Check available package managers
echo ""
echo "Available package managers:"
for pm in apt apt-get yum dnf zypper pacman; do
    if command -v $pm &> /dev/null; then
        echo "  ✓ $pm ($(which $pm))"
    fi
done
EOF

chmod +x detect_distro.sh
./detect_distro.sh
```

### Step 2: APT Package Management (Ubuntu/Debian)

```bash
cd ~/package-management-lab

cat > apt_basics.sh << 'EOF'
#!/bin/bash
# APT package management basics

echo "=== APT Package Management ==="
echo ""

# Note: Most commands require sudo
# This script shows the commands without executing them

cat << 'COMMANDS'
APT BASIC COMMANDS
==================

Update Package Index:
---------------------
sudo apt update                 Update package lists
sudo apt upgrade                Upgrade all packages
sudo apt full-upgrade           Upgrade with dependency handling
sudo apt dist-upgrade           Distribution upgrade

Install Packages:
-----------------
sudo apt install <package>      Install package
sudo apt install -y <package>   Install without confirmation
sudo apt install pkg1 pkg2 pkg3 Install multiple packages

Remove Packages:
----------------
sudo apt remove <package>       Remove package (keep config)
sudo apt purge <package>        Remove package and config
sudo apt autoremove             Remove unused dependencies

Search and Info:
----------------
apt search <keyword>            Search for packages
apt show <package>              Show package details
apt list --installed            List installed packages
apt list --upgradable           List upgradable packages

Clean Up:
---------
sudo apt clean                  Clear downloaded package cache
sudo apt autoclean              Clear old cached packages
sudo apt autoremove             Remove orphaned dependencies

Examples:
---------
# Update and upgrade
sudo apt update && sudo apt upgrade -y

# Install development tools
sudo apt install -y build-essential

# Install Python
sudo apt install -y python3 python3-pip python3-dev

# Search for packages
apt search tensorflow

# Show package info
apt show python3-pip

# Remove package
sudo apt remove package-name

# Clean up
sudo apt autoremove && sudo apt clean
COMMANDS
EOF

cat apt_basics.sh

# Create package installation reference
cat > package_reference.md << 'EOF'
# Common ML Infrastructure Packages

## Development Tools

### Build Essentials
```bash
sudo apt install -y build-essential
sudo apt install -y gcc g++ make
sudo apt install -y cmake
sudo apt install -y git curl wget
```

### Python Development
```bash
sudo apt install -y python3 python3-pip python3-dev
sudo apt install -y python3-venv python3-wheel
sudo apt install -y python3-setuptools
```

## System Libraries

### BLAS/LAPACK (for numerical computing)
```bash
sudo apt install -y libopenblas-dev
sudo apt install -y liblapack-dev
sudo apt install -y libblas-dev
```

### Image Processing
```bash
sudo apt install -y libjpeg-dev libpng-dev
sudo apt install -y libfreetype6-dev
sudo apt install -y libhdf5-dev
```

### Compression Libraries
```bash
sudo apt install -y zlib1g-dev
sudo apt install -y liblzma-dev
sudo apt install -y libbz2-dev
```

## Monitoring and Utilities

### System Monitoring
```bash
sudo apt install -y htop
sudo apt install -y iotop
sudo apt install -y nethogs
sudo apt install -y sysstat
```

### Network Tools
```bash
sudo apt install -y net-tools
sudo apt install -y netcat
sudo apt install -y nmap
```

## Database Clients
```bash
sudo apt install -y postgresql-client
sudo apt install -y mysql-client
sudo apt install -y redis-tools
```

## Container and Virtualization
```bash
sudo apt install -y docker.io
sudo apt install -y docker-compose
```
EOF

cat package_reference.md
```

### Step 3: YUM/DNF Package Management (RHEL/CentOS)

```bash
cd ~/package-management-lab

cat > yum_basics.sh << 'EOF'
#!/bin/bash
# YUM/DNF package management basics

cat << 'COMMANDS'
YUM/DNF PACKAGE MANAGEMENT
==========================

Note: dnf is the next-generation replacement for yum
Commands are mostly interchangeable

Update Packages:
----------------
sudo yum check-update           Check for updates
sudo yum update                 Update all packages
sudo yum update <package>       Update specific package

sudo dnf check-update           (dnf equivalent)
sudo dnf upgrade                (dnf equivalent)

Install Packages:
-----------------
sudo yum install <package>      Install package
sudo yum install -y <package>   Install without confirmation
sudo yum groupinstall "Development Tools"

sudo dnf install <package>      (dnf equivalent)
sudo dnf group install "Development Tools"

Remove Packages:
----------------
sudo yum remove <package>       Remove package
sudo yum autoremove             Remove orphaned dependencies

sudo dnf remove <package>       (dnf equivalent)
sudo dnf autoremove             (dnf equivalent)

Search and Info:
----------------
yum search <keyword>            Search packages
yum info <package>              Show package info
yum list installed              List installed packages
yum list available              List available packages

dnf search <keyword>            (dnf equivalent)
dnf info <package>              (dnf equivalent)
dnf list --installed            (dnf equivalent)

Repository Management:
---------------------
yum repolist                    List enabled repositories
sudo yum-config-manager --add-repo <url>

dnf repolist                    (dnf equivalent)
sudo dnf config-manager --add-repo <url>

Clean Up:
---------
sudo yum clean all              Clear cache
sudo yum clean packages         Clear package cache

sudo dnf clean all              (dnf equivalent)

Examples:
---------
# Install development tools
sudo yum groupinstall "Development Tools"
sudo yum install -y python3 python3-pip python3-devel

# Install EPEL repository (Extra Packages for Enterprise Linux)
sudo yum install -y epel-release

# Search and install
yum search htop
sudo yum install -y htop

# Update all packages
sudo yum update -y
COMMANDS
EOF

cat yum_basics.sh
```

## Part 2: Python Package Management

### Step 4: pip Package Management

```bash
cd ~/package-management-lab
mkdir python_packages
cd python_packages

# Create pip reference
cat > pip_reference.md << 'EOF'
# Python Package Management with pip

## Basic Commands

### Install Packages
```bash
pip install package_name              Install latest version
pip install package_name==1.2.3       Install specific version
pip install package_name>=1.0.0       Install minimum version
pip install -U package_name           Upgrade package
pip install --upgrade pip             Upgrade pip itself
```

### Install from Requirements
```bash
pip install -r requirements.txt       Install from file
```

### Uninstall Packages
```bash
pip uninstall package_name            Uninstall package
pip uninstall -r requirements.txt     Uninstall from file
pip uninstall -y package_name         Uninstall without confirmation
```

### List and Search
```bash
pip list                              List installed packages
pip list --outdated                   List outdated packages
pip show package_name                 Show package details
pip search keyword                    Search PyPI (deprecated)
```

### Freeze Requirements
```bash
pip freeze                            List installed packages
pip freeze > requirements.txt         Save to file
```

## Virtual Environments

### Using venv
```bash
python3 -m venv ml_env                Create virtual environment
source ml_env/bin/activate            Activate (Linux/Mac)
ml_env\Scripts\activate               Activate (Windows)
deactivate                            Deactivate
```

### Install in Virtual Environment
```bash
python3 -m venv ml_env
source ml_env/bin/activate
pip install --upgrade pip
pip install numpy pandas scikit-learn
pip freeze > requirements.txt
deactivate
```

## ML Framework Installation

### TensorFlow
```bash
pip install tensorflow==2.13.0        CPU version
pip install tensorflow-gpu==2.13.0    GPU version (legacy)
# Modern TensorFlow includes GPU support automatically
```

### PyTorch
```bash
# CPU version
pip install torch torchvision torchaudio

# GPU version (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# GPU version (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Other ML Libraries
```bash
pip install scikit-learn              Machine learning
pip install xgboost lightgbm          Gradient boosting
pip install transformers              Hugging Face transformers
pip install opencv-python             Computer vision
pip install pillow                    Image processing
pip install matplotlib seaborn        Visualization
pip install jupyter notebook          Jupyter notebook
pip install pandas numpy scipy        Data science
pip install mlflow                    ML lifecycle
pip install wandb                     Experiment tracking
```
EOF

cat pip_reference.md

# Create virtual environment setup script
cat > setup_ml_env.sh << 'EOF'
#!/bin/bash
# Set up Python virtual environment for ML

ENV_NAME="ml_env"
PYTHON_VERSION="python3"

echo "Creating virtual environment: $ENV_NAME"

# Create virtual environment
$PYTHON_VERSION -m venv $ENV_NAME

# Activate
source $ENV_NAME/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install common ML packages
echo "Installing ML packages..."
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2
pip install jupyter==1.0.0
pip install ipython==8.14.0

# Install ML frameworks
echo "Installing TensorFlow..."
pip install tensorflow==2.13.0

echo "Installing PyTorch..."
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2

# Install utilities
echo "Installing utilities..."
pip install tqdm==4.66.1
pip install pyyaml==6.0.1
pip install python-dotenv==1.0.0
pip install requests==2.31.0

# Save requirements
pip freeze > requirements.txt

echo ""
echo "Installation complete!"
echo "Activate with: source $ENV_NAME/bin/activate"
echo "Requirements saved to: requirements.txt"

# Deactivate
deactivate
EOF

chmod +x setup_ml_env.sh

# Create requirements.txt template
cat > requirements_template.txt << 'EOF'
# Core ML Libraries
numpy>=1.24.0,<2.0.0
pandas>=2.0.0,<3.0.0
scikit-learn>=1.3.0,<2.0.0
scipy>=1.10.0,<2.0.0

# Deep Learning
tensorflow>=2.13.0,<3.0.0
torch>=2.0.0,<3.0.0
torchvision>=0.15.0,<1.0.0

# Data Processing
pillow>=10.0.0
opencv-python>=4.8.0

# Visualization
matplotlib>=3.7.0,<4.0.0
seaborn>=0.12.0,<1.0.0

# Development Tools
jupyter>=1.0.0
ipython>=8.14.0
black>=23.7.0
flake8>=6.0.0
pytest>=7.4.0

# Utilities
tqdm>=4.66.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
requests>=2.31.0

# MLOps
mlflow>=2.5.0
wandb>=0.15.0
EOF

cat requirements_template.txt
```

### Step 5: Conda Package Management

```bash
cd ~/package-management-lab/python_packages

cat > conda_reference.md << 'EOF'
# Conda Package Management

Conda is an alternative to pip that manages both Python packages and system dependencies.

## Installation

### Miniconda (minimal installer)
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

### Anaconda (full distribution)
```bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.09-Linux-x86_64.sh
bash Anaconda3-2023.09-Linux-x86_64.sh
```

## Basic Commands

### Environment Management
```bash
conda create -n myenv python=3.10      Create environment
conda create -n myenv python=3.10 numpy pandas  Create with packages
conda activate myenv                   Activate environment
conda deactivate                       Deactivate environment
conda env list                         List environments
conda remove -n myenv --all            Remove environment
```

### Package Management
```bash
conda install package_name             Install package
conda install package_name=1.2.3       Install specific version
conda install -c conda-forge package   Install from channel
conda update package_name              Update package
conda remove package_name              Remove package
conda list                             List installed packages
conda search package_name              Search for package
```

### Export and Import
```bash
conda env export > environment.yml     Export environment
conda env create -f environment.yml    Create from file
conda list --export > requirements.txt Export to requirements
```

## ML Environment Setup

### TensorFlow Environment
```bash
conda create -n tensorflow python=3.10
conda activate tensorflow
conda install -c conda-forge tensorflow-gpu
conda install -c conda-forge cudatoolkit=11.8
conda install -c conda-forge cudnn
conda install pandas numpy matplotlib jupyter
```

### PyTorch Environment
```bash
conda create -n pytorch python=3.10
conda activate pytorch
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
conda install pandas numpy matplotlib jupyter
```

### Data Science Environment
```bash
conda create -n datascience python=3.10
conda activate datascience
conda install pandas numpy scipy scikit-learn
conda install matplotlib seaborn plotly
conda install jupyter jupyterlab
conda install -c conda-forge xgboost lightgbm
```

## Environment File (environment.yml)

```yaml
name: ml_project
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24
  - pandas=2.0
  - scikit-learn=1.3
  - matplotlib=3.7
  - jupyter=1.0
  - pip
  - pip:
    - tensorflow==2.13.0
    - mlflow==2.5.0
    - wandb==0.15.0
```

Create environment:
```bash
conda env create -f environment.yml
conda activate ml_project
```

## Conda vs pip

### Use Conda when:
- Need system library management
- Working with complex dependencies
- Need multiple Python versions
- Want reproducible environments across platforms

### Use pip when:
- Package only available on PyPI
- Need latest package versions
- Working in production Docker containers
- Want lightweight environments
EOF

cat conda_reference.md
```

## Part 3: CUDA and GPU Drivers

### Step 6: Installing NVIDIA Drivers and CUDA

```bash
cd ~/package-management-lab
mkdir gpu_setup
cd gpu_setup

cat > install_nvidia_cuda.md << 'EOF'
# Installing NVIDIA Drivers and CUDA

## Check GPU

```bash
# Check if NVIDIA GPU is present
lspci | grep -i nvidia

# Check current driver (if installed)
nvidia-smi
```

## Ubuntu/Debian Installation

### Method 1: Using Ubuntu Repository

```bash
# Check available drivers
ubuntu-drivers devices

# Install recommended driver
sudo ubuntu-drivers autoinstall

# Or install specific version
sudo apt install nvidia-driver-535

# Reboot
sudo reboot

# Verify installation
nvidia-smi
```

### Method 2: NVIDIA Official Repository

```bash
# Add NVIDIA package repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Install CUDA Toolkit
sudo apt install cuda-toolkit-12-2

# Install NVIDIA driver
sudo apt install nvidia-driver-535

# Add to PATH (add to ~/.bashrc)
export PATH=/usr/local/cuda-12.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH

# Reboot
sudo reboot

# Verify
nvidia-smi
nvcc --version
```

## RHEL/CentOS Installation

```bash
# Add EPEL repository
sudo yum install epel-release

# Add NVIDIA repository
sudo yum-config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/cuda-rhel8.repo

# Install CUDA
sudo yum install cuda

# Reboot
sudo reboot

# Verify
nvidia-smi
```

## cuDNN Installation

cuDNN (CUDA Deep Neural Network library) is required for deep learning frameworks.

```bash
# Download from NVIDIA (requires account)
# https://developer.nvidia.com/cudnn

# Install (Ubuntu)
sudo dpkg -i libcudnn8_8.9.4.25-1+cuda12.2_amd64.deb
sudo dpkg -i libcudnn8-dev_8.9.4.25-1+cuda12.2_amd64.deb

# Or using tar
tar -xzvf cudnn-linux-x86_64-8.9.4.25_cuda12-archive.tar.xz
sudo cp cudnn-*-archive/include/cudnn*.h /usr/local/cuda/include
sudo cp -P cudnn-*-archive/lib/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```

## Verification Script

```bash
#!/bin/bash
# verify_cuda.sh

echo "=== NVIDIA GPU Check ==="
lspci | grep -i nvidia

echo ""
echo "=== NVIDIA Driver ==="
nvidia-smi

echo ""
echo "=== CUDA Version ==="
nvcc --version

echo ""
echo "=== cuDNN Version ==="
cat /usr/local/cuda/include/cudnn_version.h | grep CUDNN_MAJOR -A 2

echo ""
echo "=== TensorFlow GPU Test ==="
python3 << PYTHON
import tensorflow as tf
print("TensorFlow version:", tf.__version__)
print("GPU available:", tf.config.list_physical_devices('GPU'))
PYTHON

echo ""
echo "=== PyTorch GPU Test ==="
python3 << PYTHON
import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)
print("GPU count:", torch.cuda.device_count())
if torch.cuda.is_available():
    print("GPU name:", torch.cuda.get_device_name(0))
PYTHON
```

## Troubleshooting

### Issue: nouveau driver conflict
```bash
# Blacklist nouveau driver
sudo bash -c "echo blacklist nouveau > /etc/modprobe.d/blacklist-nvidia-nouveau.conf"
sudo bash -c "echo options nouveau modeset=0 >> /etc/modprobe.d/blacklist-nvidia-nouveau.conf"
sudo update-initramfs -u
sudo reboot
```

### Issue: NVIDIA driver not loading
```bash
# Check if driver is loaded
lsmod | grep nvidia

# Load driver manually
sudo modprobe nvidia

# Check for errors
dmesg | grep nvidia
```

### Issue: CUDA library not found
```bash
# Add to ~/.bashrc
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
export PATH=/usr/local/cuda/bin:$PATH

# Reload
source ~/.bashrc
```
EOF

cat install_nvidia_cuda.md
```

## Part 4: Docker Installation

### Step 7: Installing Docker

```bash
cd ~/package-management-lab
mkdir docker_setup
cd docker_setup

cat > install_docker.sh << 'EOF'
#!/bin/bash
# Install Docker on Ubuntu/Debian

set -e

echo "Installing Docker on Ubuntu/Debian"

# Update package index
sudo apt update

# Install prerequisites
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add current user to docker group
sudo usermod -aG docker $USER

echo ""
echo "Docker installation complete!"
echo "Log out and back in for group changes to take effect"
echo ""
echo "Verify installation:"
echo "  docker --version"
echo "  docker compose version"
echo "  docker run hello-world"
EOF

chmod +x install_docker.sh

cat > install_nvidia_docker.md << 'EOF'
# Installing NVIDIA Docker (for GPU containers)

NVIDIA Container Toolkit allows Docker containers to access NVIDIA GPUs.

## Prerequisites
- NVIDIA GPU
- NVIDIA drivers installed
- Docker installed

## Installation (Ubuntu/Debian)

```bash
# Add NVIDIA Docker repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Update package index
sudo apt update

# Install NVIDIA Docker
sudo apt install -y nvidia-docker2

# Restart Docker
sudo systemctl restart docker

# Verify installation
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Testing GPU Access

```bash
# Run CUDA sample
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Run TensorFlow with GPU
docker run --rm --gpus all tensorflow/tensorflow:latest-gpu \
    python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Run PyTorch with GPU
docker run --rm --gpus all pytorch/pytorch:latest \
    python -c "import torch; print(torch.cuda.is_available())"
```

## Docker Compose with GPU

```yaml
version: '3.8'

services:
  ml_training:
    image: tensorflow/tensorflow:latest-gpu
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    volumes:
      - ./code:/workspace
    command: python /workspace/train.py
```

Run with:
```bash
docker compose up
```
EOF

cat install_nvidia_docker.md
```

## Part 5: Complete ML Stack Installation

### Step 8: Automated ML Stack Setup

```bash
cd ~/package-management-lab
mkdir full_stack
cd full_stack

cat > install_ml_stack.sh << 'EOF'
#!/bin/bash
###############################################################################
# Complete ML Infrastructure Stack Installation
# Supports Ubuntu/Debian
###############################################################################

set -euo pipefail

# Configuration
LOG_FILE="installation.log"
ERROR_LOG="installation_errors.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$ERROR_LOG"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    error "Do not run as root. Script will use sudo when needed."
    exit 1
fi

# Detect distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION=$VERSION_ID
        log "Detected: $NAME $VERSION"
    else
        error "Cannot detect Linux distribution"
        exit 1
    fi
}

# Install system packages
install_system_packages() {
    log "Installing system packages..."

    case $DISTRO in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y \
                build-essential \
                gcc g++ make \
                cmake \
                git curl wget \
                python3 python3-pip python3-dev python3-venv \
                libopenblas-dev liblapack-dev \
                libjpeg-dev libpng-dev \
                libhdf5-dev \
                htop iotop \
                net-tools \
                ca-certificates gnupg lsb-release
            ;;
        centos|rhel|fedora)
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                python3 python3-pip python3-devel \
                openblas-devel lapack-devel \
                libjpeg-devel libpng-devel \
                hdf5-devel \
                htop \
                net-tools
            ;;
        *)
            error "Unsupported distribution: $DISTRO"
            return 1
            ;;
    esac

    log "System packages installed"
}

# Setup Python virtual environment
setup_python_env() {
    log "Setting up Python environment..."

    # Create virtual environment
    python3 -m venv ~/ml_env

    # Activate
    source ~/ml_env/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install ML packages
    log "Installing Python ML packages..."
    pip install numpy pandas scikit-learn matplotlib seaborn
    pip install jupyter jupyterlab ipython
    pip install tensorflow torch torchvision
    pip install mlflow wandb
    pip install tqdm pyyaml python-dotenv requests

    # Save requirements
    pip freeze > ~/ml_env_requirements.txt

    deactivate

    log "Python environment created at ~/ml_env"
    log "Activate with: source ~/ml_env/bin/activate"
}

# Install Docker
install_docker() {
    log "Installing Docker..."

    if command -v docker &> /dev/null; then
        warn "Docker already installed"
        return 0
    fi

    case $DISTRO in
        ubuntu|debian)
            # Add Docker repository
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
                sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

            echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
                https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
                sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            sudo apt update
            sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

            # Start Docker
            sudo systemctl start docker
            sudo systemctl enable docker

            # Add user to docker group
            sudo usermod -aG docker $USER

            log "Docker installed successfully"
            ;;
        *)
            warn "Docker installation not supported for $DISTRO in this script"
            ;;
    esac
}

# Generate summary report
generate_report() {
    local report_file="installation_report.txt"

    {
        echo "ML Infrastructure Installation Report"
        echo "====================================="
        echo "Date: $(date)"
        echo "User: $(whoami)"
        echo "Host: $(hostname)"
        echo ""

        echo "System Information:"
        echo "-------------------"
        echo "Distribution: $DISTRO $VERSION"
        echo "Kernel: $(uname -r)"
        echo "Python: $(python3 --version)"
        echo ""

        echo "Installed Components:"
        echo "---------------------"

        if command -v gcc &> /dev/null; then
            echo "✓ GCC: $(gcc --version | head -1)"
        fi

        if command -v python3 &> /dev/null; then
            echo "✓ Python: $(python3 --version)"
        fi

        if command -v pip3 &> /dev/null; then
            echo "✓ pip: $(pip3 --version)"
        fi

        if command -v docker &> /dev/null; then
            echo "✓ Docker: $(docker --version)"
        fi

        if command -v nvidia-smi &> /dev/null; then
            echo "✓ NVIDIA Driver: $(nvidia-smi --query-gpu=driver_version --format=csv,noheader)"
        fi

        echo ""
        echo "Next Steps:"
        echo "-----------"
        echo "1. Activate Python environment: source ~/ml_env/bin/activate"
        echo "2. Log out and back in for Docker group changes"
        echo "3. Test Docker: docker run hello-world"
        echo "4. Install CUDA if you have NVIDIA GPU"
        echo ""

    } > "$report_file"

    cat "$report_file"
    log "Report saved to: $report_file"
}

# Main installation workflow
main() {
    log "========================================"
    log "ML Infrastructure Stack Installation"
    log "========================================"

    detect_distro
    install_system_packages
    setup_python_env
    install_docker
    generate_report

    log "========================================"
    log "Installation Complete!"
    log "========================================"
    log "Review logs: $LOG_FILE"
    if [ -f "$ERROR_LOG" ]; then
        warn "Errors logged to: $ERROR_LOG"
    fi
}

# Run main
main "$@"
EOF

chmod +x install_ml_stack.sh
```

## Validation

```bash
cd ~/package-management-lab

cat > validate_installation.sh << 'EOF'
#!/bin/bash
# Validate ML stack installation

echo "=== ML Stack Validation ==="
echo ""

check_command() {
    local cmd=$1
    local name=$2

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -1)
        echo "✓ $name: $version"
        return 0
    else
        echo "✗ $name: Not found"
        return 1
    fi
}

# System tools
echo "System Tools:"
check_command gcc "GCC"
check_command python3 "Python"
check_command pip3 "pip"
check_command git "Git"

echo ""
echo "Python Packages:"
if [ -f ~/ml_env/bin/python ]; then
    source ~/ml_env/bin/activate
    python -c "import numpy; print('✓ NumPy:', numpy.__version__)"
    python -c "import pandas; print('✓ Pandas:', pandas.__version__)"
    python -c "import sklearn; print('✓ scikit-learn:', sklearn.__version__)"
    python -c "import tensorflow; print('✓ TensorFlow:', tensorflow.__version__)" 2>/dev/null || echo "✗ TensorFlow"
    python -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>/dev/null || echo "✗ PyTorch"
    deactivate
else
    echo "✗ Virtual environment not found"
fi

echo ""
echo "Container Tools:"
check_command docker "Docker"

echo ""
echo "GPU Tools:"
if command -v nvidia-smi &> /dev/null; then
    echo "✓ NVIDIA Driver:"
    nvidia-smi --query-gpu=name,driver_version --format=csv
else
    echo "✗ NVIDIA Driver: Not found"
fi

echo ""
echo "=== Validation Complete ==="
EOF

chmod +x validate_installation.sh
./validate_installation.sh
```

## Troubleshooting

**Problem**: Package installation fails with permission denied
- **Solution**: Use sudo: `sudo apt install package`
- Check if you have sudo privileges

**Problem**: pip install fails with "externally managed environment"
- **Solution**: Use virtual environment: `python3 -m venv env`
- Or use `pip install --user package`

**Problem**: CUDA version mismatch
- **Solution**: Check compatibility matrix for your ML framework
- Install matching CUDA version

**Problem**: Docker permission denied
- **Solution**: Add user to docker group: `sudo usermod -aG docker $USER`
- Log out and back in

## Reflection Questions

1. What's the difference between system packages and Python packages?
2. When would you use pip vs conda?
3. Why use virtual environments?
4. How do you resolve dependency conflicts?
5. What's the purpose of requirements.txt?

## Next Steps

- **Exercise 06**: Log Analysis
- **Exercise 07**: Troubleshooting
- **Lecture 06**: System Administration

## Additional Resources

- pip documentation: https://pip.pypa.io/
- conda documentation: https://docs.conda.io/
- CUDA installation: https://docs.nvidia.com/cuda/
- Docker installation: https://docs.docker.com/engine/install/

---

**Congratulations!** You've mastered package management for ML infrastructure!
