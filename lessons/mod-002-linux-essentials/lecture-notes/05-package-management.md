# Lecture 05: Package Management and System Administration

## Table of Contents
1. [Introduction](#introduction)
2. [Package Management Fundamentals](#package-management-fundamentals)
3. [APT - Debian/Ubuntu Package Manager](#apt-debianubuntu-package-manager)
4. [YUM/DNF - RHEL/CentOS Package Manager](#yumdnf-rhelcentos-package-manager)
5. [System Updates and Security](#system-updates-and-security)
6. [Building from Source](#building-from-source)
7. [Python Package Management](#python-package-management)
8. [Managing ML Dependencies](#managing-ml-dependencies)
9. [Best Practices](#best-practices)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Package management is critical for maintaining AI infrastructure. You'll install ML frameworks, system libraries, GPU drivers, and countless dependencies. Understanding package managers ensures reproducible environments and prevents dependency conflicts.

This lecture covers Linux package management, focusing on practical applications for AI infrastructure engineering.

### Learning Objectives

By the end of this lecture, you will:
- Understand package management concepts and repositories
- Use APT (Debian/Ubuntu) and YUM/DNF (RHEL/CentOS) effectively
- Install and manage ML framework dependencies
- Handle system updates and security patches
- Build software from source when necessary
- Manage Python packages and virtual environments
- Create reproducible ML environments

### Prerequisites
- Lectures 01-04 (Linux fundamentals through shell scripting)
- Basic understanding of software dependencies
- Root/sudo access to practice system

### Why Package Management for AI?

**Dependency Management**: ML frameworks have complex dependencies (CUDA, cuDNN, TensorFlow, PyTorch, NumPy, etc.)

**Reproducibility**: Same environment across development, staging, and production

**Security**: Regular updates patch vulnerabilities in system libraries

**Efficiency**: Binary packages install faster than compiling from source

**Compatibility**: Ensure GPU drivers, CUDA versions, and frameworks align

## Package Management Fundamentals

### What is a Package?

A **package** is a compressed archive containing:
- Compiled binaries or scripts
- Configuration files
- Documentation
- Metadata (dependencies, version, description)
- Installation/removal scripts

### Package Managers

**High-Level** (User-friendly, handles dependencies):
- `apt` / `apt-get` (Debian, Ubuntu)
- `yum` / `dnf` (RHEL, CentOS, Fedora)
- `zypper` (openSUSE)

**Low-Level** (Manual dependency handling):
- `dpkg` (Debian packages)
- `rpm` (Red Hat packages)

### Repositories

**Repositories** are servers hosting package collections. Example:
- Official Ubuntu repositories
- Third-party PPAs (Personal Package Archives)
- NVIDIA CUDA repository
- Docker repository
- Python Package Index (PyPI)

### Dependency Resolution

Package managers automatically:
1. Identify required dependencies
2. Download all necessary packages
3. Install in correct order
4. Handle conflicts and version requirements

```bash
# When you install:
apt install python3-pip

# Package manager installs:
# - python3-pip (requested package)
# - python3 (dependency)
# - python3-distutils (dependency)
# - python3-setuptools (dependency)
# - libpython3-stdlib (dependency)
# ... and more
```

## APT - Debian/Ubuntu Package Manager

### Basic APT Commands

**Update Package Lists**:
```bash
# Download package information from repositories
sudo apt update
# Always run before installing to get latest package info
```

**Upgrade Packages**:
```bash
# Upgrade all installed packages
sudo apt upgrade

# Upgrade with smart conflict resolution
sudo apt full-upgrade

# Upgrade without confirmation (scripting)
sudo apt upgrade -y
```

**Installing Packages**:
```bash
# Install single package
sudo apt install nginx

# Install multiple packages
sudo apt install python3 python3-pip python3-venv

# Install specific version
sudo apt install nginx=1.18.0-0ubuntu1

# Install without prompts
sudo apt install -y docker.io

# Simulate installation (dry run)
sudo apt install --dry-run cuda-11-8
```

**Removing Packages**:
```bash
# Remove package (keep configuration)
sudo apt remove nginx

# Remove package and configuration
sudo apt purge nginx

# Remove package and unused dependencies
sudo apt autoremove nginx

# Clean up
sudo apt autoremove        # Remove unused dependencies
sudo apt autoclean         # Remove old package files
sudo apt clean             # Remove all package files from cache
```

**Searching Packages**:
```bash
# Search for package
apt search python3

# Search in package names only
apt search --names-only cuda

# Show package details
apt show python3-pip

# List installed packages
apt list --installed
apt list --installed | grep python

# List upgradable packages
apt list --upgradable
```

**Package Information**:
```bash
# Show package details
apt show nvidia-driver-530

# Show package dependencies
apt depends python3-pip

# Show reverse dependencies (what needs this package)
apt rdepends python3

# Which package provides a file
dpkg -S /usr/bin/python3

# List files in package
dpkg -L python3-pip
```

### Managing Repositories

**Repository Configuration**: `/etc/apt/sources.list` and `/etc/apt/sources.list.d/`

```bash
# View current repositories
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/

# Add repository
sudo add-apt-repository ppa:deadsnakes/ppa  # Python versions
sudo apt update

# Add repository manually
echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

# Add GPG key for repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Remove repository
sudo add-apt-repository --remove ppa:deadsnakes/ppa
sudo rm /etc/apt/sources.list.d/docker.list
```

### AI/ML Specific Packages

**Install Python Development Tools**:
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git
```

**Install System ML Dependencies**:
```bash
# BLAS libraries (linear algebra)
sudo apt install -y \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

# HDF5 (data format for large datasets)
sudo apt install -y libhdf5-dev

# OpenCV dependencies
sudo apt install -y \
    libopencv-dev \
    python3-opencv

# Database libraries
sudo apt install -y \
    libpq-dev \
    libmysqlclient-dev \
    libsqlite3-dev
```

**Install NVIDIA CUDA**:
```bash
# Add NVIDIA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Install CUDA toolkit
sudo apt install -y cuda-toolkit-11-8

# Install cuDNN
sudo apt install -y libcudnn8 libcudnn8-dev

# Verify installation
nvcc --version
```

**Install Docker**:
```bash
# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Verify
docker --version
```

## YUM/DNF - RHEL/CentOS Package Manager

### Basic YUM/DNF Commands

**DNF** is the modern replacement for YUM (same commands work for both).

**Update and Upgrade**:
```bash
# Update package cache
sudo dnf check-update

# Upgrade all packages
sudo dnf upgrade

# Upgrade without prompts
sudo dnf upgrade -y
```

**Installing Packages**:
```bash
# Install package
sudo dnf install nginx

# Install multiple packages
sudo dnf install python3 python3-pip python3-devel

# Install specific version
sudo dnf install nginx-1.20.1

# Install group
sudo dnf groupinstall "Development Tools"

# Reinstall package
sudo dnf reinstall nginx
```

**Removing Packages**:
```bash
# Remove package
sudo dnf remove nginx

# Remove with dependencies
sudo dnf autoremove nginx

# Clean cache
sudo dnf clean all
```

**Searching and Information**:
```bash
# Search packages
dnf search python

# Show package info
dnf info python3-pip

# List installed
dnf list installed

# List available
dnf list available | grep cuda

# Find which package provides file
dnf provides /usr/bin/python3

# Show dependencies
dnf deplist python3-pip
```

### Managing Repositories

```bash
# List enabled repositories
dnf repolist

# List all repositories
dnf repolist all

# Enable repository
sudo dnf config-manager --set-enabled powertools

# Disable repository
sudo dnf config-manager --set-disabled epel

# Add repository
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install EPEL (Extra Packages for Enterprise Linux)
sudo dnf install -y epel-release
```

### AI/ML on RHEL/CentOS

```bash
# Development tools
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y python3 python3-pip python3-devel

# ML dependencies
sudo dnf install -y \
    openblas-devel \
    lapack-devel \
    hdf5-devel

# NVIDIA CUDA (RHEL 8)
sudo dnf config-manager --add-repo https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/cuda-rhel8.repo
sudo dnf install -y cuda-toolkit-11-8

# Docker
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

## System Updates and Security

### Regular Update Strategy

```bash
# Weekly maintenance script
#!/bin/bash
set -euo pipefail

echo "=== System Update $(date) ===" | tee -a /var/log/updates.log

# Update package lists
sudo apt update | tee -a /var/log/updates.log

# Check for updates
UPDATES=$(apt list --upgradable 2>/dev/null | grep -v "Listing" | wc -l)
echo "Available updates: $UPDATES" | tee -a /var/log/updates.log

# Upgrade packages
sudo apt upgrade -y | tee -a /var/log/updates.log

# Autoremove unused packages
sudo apt autoremove -y | tee -a /var/log/updates.log

# Clean cache
sudo apt autoclean | tee -a /var/log/updates.log

# Check if reboot required
if [ -f /var/run/reboot-required ]; then
    echo "REBOOT REQUIRED" | tee -a /var/log/updates.log
    cat /var/run/reboot-required.pkgs | tee -a /var/log/updates.log
fi

echo "Update completed" | tee -a /var/log/updates.log
```

### Security Updates

```bash
# Ubuntu: Install security updates only
sudo apt update
sudo apt upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold"

# Unattended upgrades (automatic security updates)
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Configuration: /etc/apt/apt.conf.d/50unattended-upgrades
# Enable: Unattended-Upgrade::Automatic-Reboot "true";

# Check for CVEs
sudo apt install -y ubuntu-security-status
sudo ubuntu-security-status

# RHEL/CentOS: Security updates only
sudo dnf upgrade --security -y
```

### Kernel Updates

```bash
# View current kernel
uname -r
# 5.15.0-78-generic

# List available kernels
apt list linux-image-* | grep installed

# Install new kernel
sudo apt install -y linux-image-5.15.0-80-generic

# Remove old kernels (keep current + 1 previous)
sudo apt autoremove --purge

# Update GRUB
sudo update-grub

# Reboot to new kernel
sudo reboot
```

### Handling Held Packages

```bash
# Hold package (prevent updates)
sudo apt-mark hold cuda-toolkit-11-8

# Show held packages
apt-mark showhold

# Unhold package
sudo apt-mark unhold cuda-toolkit-11-8

# Why hold packages?
# - CUDA version compatibility with ML frameworks
# - Prevent Docker updates during critical operations
# - Kernel version pinning for driver compatibility
```

## Building from Source

Sometimes packages aren't available or you need specific versions.

### Prerequisites for Building

```bash
# Install build tools (Ubuntu)
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    wget \
    curl

# Install build tools (RHEL/CentOS)
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y cmake git wget
```

### General Build Process

```bash
# 1. Download source
wget https://example.com/software-1.0.tar.gz
tar -xzf software-1.0.tar.gz
cd software-1.0

# 2. Configure
./configure --prefix=/usr/local

# 3. Compile
make -j$(nproc)  # Use all CPU cores

# 4. Test (if available)
make test

# 5. Install
sudo make install

# 6. Update library cache
sudo ldconfig
```

### Example: Building Python from Source

```bash
# Install dependencies
sudo apt install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev

# Download Python
wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz
tar -xzf Python-3.11.5.tgz
cd Python-3.11.5

# Configure with optimizations
./configure --enable-optimizations --prefix=/usr/local

# Build
make -j$(nproc)

# Install
sudo make altinstall  # Use altinstall to not replace system python

# Verify
python3.11 --version
```

### Example: Building OpenCV with CUDA

```bash
# Dependencies
sudo apt install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    python3-dev

# Download OpenCV
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv
mkdir build && cd build

# Configure with CUDA
cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
    -D WITH_CUDA=ON \
    -D WITH_CUDNN=ON \
    -D OPENCV_DNN_CUDA=ON \
    -D ENABLE_FAST_MATH=1 \
    -D CUDA_FAST_MATH=1 \
    -D WITH_CUBLAS=1 \
    -D PYTHON3_EXECUTABLE=/usr/bin/python3 \
    ..

# Build (this takes time!)
make -j$(nproc)

# Install
sudo make install
sudo ldconfig
```

## Python Package Management

### pip - Python Package Installer

```bash
# Install pip
sudo apt install -y python3-pip

# Upgrade pip
python3 -m pip install --upgrade pip

# Install package
pip install numpy

# Install specific version
pip install tensorflow==2.13.0

# Install from requirements
pip install -r requirements.txt

# Install with extras
pip install "transformers[torch]"

# Uninstall
pip uninstall numpy

# List installed
pip list
pip freeze                    # Format for requirements.txt

# Show package info
pip show numpy

# Search packages (deprecated, use PyPI website)
# pip search tensorflow

# Upgrade package
pip install --upgrade numpy

# Upgrade all packages (be careful!)
pip list --outdated --format=freeze | cut -d = -f 1 | xargs -n1 pip install -U
```

### Virtual Environments

**Why Virtual Environments?**
- Isolate project dependencies
- Avoid conflicts between projects
- Reproducible environments
- Don't pollute system Python

**Using venv**:
```bash
# Create virtual environment
python3 -m venv myproject_env

# Activate
source myproject_env/bin/activate

# Now pip installs go into this environment
pip install tensorflow torch numpy pandas

# Deactivate
deactivate

# Delete environment
rm -rf myproject_env
```

**Using virtualenv**:
```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv myenv
virtualenv -p python3.11 myenv  # Specific Python version

# Activate/deactivate same as venv
source myenv/bin/activate
deactivate
```

**Using conda** (popular for ML):
```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create environment
conda create -n ml-env python=3.10

# Activate
conda activate ml-env

# Install packages
conda install numpy pandas scikit-learn
conda install pytorch torchvision torchaudio -c pytorch

# Install from pip if needed
pip install transformers

# Export environment
conda env export > environment.yml

# Create from environment file
conda env create -f environment.yml

# List environments
conda env list

# Remove environment
conda env remove -n ml-env
```

### requirements.txt Best Practices

```bash
# Generate requirements
pip freeze > requirements.txt

# Better: Pin exact versions for reproducibility
cat > requirements.txt << EOF
# ML Frameworks
tensorflow==2.13.0
torch==2.0.1
torchvision==0.15.2

# Data processing
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0

# Visualization
matplotlib==3.7.2
seaborn==0.12.2

# Utilities
tqdm==4.66.1
pyyaml==6.0.1
EOF

# Install from requirements
pip install -r requirements.txt

# Separate dev requirements
cat > requirements-dev.txt << EOF
-r requirements.txt
pytest==7.4.0
black==23.7.0
pylint==2.17.5
jupyter==1.0.0
EOF

pip install -r requirements-dev.txt
```

## Managing ML Dependencies

### Creating Reproducible ML Environment

```bash
#!/bin/bash
# setup-ml-env.sh - Set up ML development environment

set -euo pipefail

readonly ENV_NAME="ml-project"
readonly PYTHON_VERSION="3.10"
readonly CUDA_VERSION="11.8"

function install_system_deps() {
    echo "Installing system dependencies..."
    sudo apt update
    sudo apt install -y \
        python3-dev \
        build-essential \
        git \
        curl \
        wget \
        libhdf5-dev \
        libblas-dev \
        liblapack-dev \
        libopencv-dev \
        graphviz
}

function install_cuda() {
    echo "Installing CUDA $CUDA_VERSION..."
    # Add NVIDIA repository
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_1.1-1_all.deb
    sudo apt update
    sudo apt install -y cuda-toolkit-${CUDA_VERSION/./-}

    # Add to PATH
    echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
}

function create_python_env() {
    echo "Creating Python environment..."
    python${PYTHON_VERSION} -m venv ${ENV_NAME}
    source ${ENV_NAME}/bin/activate

    # Upgrade pip
    pip install --upgrade pip setuptools wheel

    # Install ML frameworks
    pip install \
        tensorflow==2.13.0 \
        torch==2.0.1 \
        torchvision==0.15.2 \
        transformers==4.33.0 \
        scikit-learn==1.3.0 \
        numpy==1.24.3 \
        pandas==2.0.3 \
        matplotlib==3.7.2 \
        jupyter==1.0.0 \
        tensorboard==2.13.0

    # Save requirements
    pip freeze > requirements.txt
}

function verify_installation() {
    echo "Verifying installation..."
    source ${ENV_NAME}/bin/activate

    python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}')"
    python -c "import torch; print(f'PyTorch: {torch.__version__}')"
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
}

# Main
install_system_deps
install_cuda
create_python_env
verify_installation

echo "Environment setup complete!"
echo "Activate with: source ${ENV_NAME}/bin/activate"
```

### Docker for Reproducibility

```bash
# Dockerfile for ML environment
cat > Dockerfile << 'EOF'
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set up Python
RUN ln -s /usr/bin/python3.10 /usr/bin/python
RUN pip install --upgrade pip

# Install ML frameworks
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
EOF

# Build image
docker build -t ml-env:latest .

# Run container with GPU
docker run --gpus all -it --rm -v $(pwd):/workspace ml-env:latest

# Or use docker-compose
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  ml-dev:
    image: ml-env:latest
    volumes:
      - .:/workspace
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    shm_size: '8gb'
EOF

docker-compose run ml-dev
```

## Best Practices

### 1. Version Pinning

```bash
# Bad: Unpinned versions (will break over time)
pip install tensorflow

# Good: Pin exact versions
pip install tensorflow==2.13.0

# Better: Use requirements.txt with pinned versions
pip install -r requirements.txt
```

### 2. Separate Environments

```bash
# One environment per project
project1/
  venv/
  requirements.txt

project2/
  venv/
  requirements.txt

# NOT a global environment for all projects
```

### 3. Document Dependencies

```bash
# Include README with setup instructions
cat > SETUP.md << 'EOF'
# Setup Instructions

## System Requirements
- Ubuntu 22.04
- NVIDIA GPU with CUDA 11.8
- 16GB RAM minimum

## Installation

1. Install system dependencies:
```bash
sudo apt update
sudo apt install -y python3.10 python3-pip build-essential
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```
EOF
```

### 4. Regular Maintenance

```bash
# Update security patches weekly
sudo apt update && sudo apt upgrade -y

# Audit Python packages for vulnerabilities
pip install pip-audit
pip-audit

# Keep requirements up to date (carefully!)
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

### 5. Use Lock Files

```bash
# pip-tools for deterministic builds
pip install pip-tools

# Create requirements.in (high-level dependencies)
cat > requirements.in << EOF
tensorflow
torch
numpy
pandas
EOF

# Compile to requirements.txt (with all subdependencies)
pip-compile requirements.in

# Install from locked requirements
pip-sync requirements.txt
```

## Summary and Key Takeaways

### Commands Mastered

**APT (Ubuntu/Debian)**:
- `apt update` - Update package lists
- `apt upgrade` - Upgrade packages
- `apt install` - Install packages
- `apt remove` - Remove packages
- `apt search` - Search packages

**YUM/DNF (RHEL/CentOS)**:
- `dnf check-update` - Check updates
- `dnf upgrade` - Upgrade packages
- `dnf install` - Install packages
- `dnf remove` - Remove packages

**pip (Python)**:
- `pip install` - Install packages
- `pip freeze` - List installed
- `pip install -r requirements.txt` - Install from file

**Virtual Environments**:
- `python3 -m venv env` - Create environment
- `source env/bin/activate` - Activate
- `deactivate` - Deactivate

### Key Concepts

1. **Package Management**: Automated software installation and updates
2. **Dependencies**: Packages require other packages
3. **Repositories**: Centralized package sources
4. **Virtual Environments**: Isolated Python environments
5. **Reproducibility**: Same environment everywhere
6. **Security**: Regular updates patch vulnerabilities

### AI/ML Best Practices

✅ Pin dependency versions for reproducibility
✅ Use virtual environments for each project
✅ Document system and Python dependencies
✅ Test environment setup in containers
✅ Separate development and production dependencies
✅ Regular security updates
✅ Hold critical packages (CUDA) during projects
✅ Version control requirements.txt

### Common Workflow

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install system dependencies
sudo apt install -y python3-dev build-essential

# 3. Create virtual environment
python3 -m venv myproject-env
source myproject-env/bin/activate

# 4. Install Python packages
pip install -r requirements.txt

# 5. Freeze dependencies
pip freeze > requirements.txt

# 6. Commit to version control
git add requirements.txt
git commit -m "Update dependencies"
```

### Next Steps

You've completed all Module 002 lectures! Next:
- **Complete hands-on exercises** to practice these skills
- **Take the module quiz** to assess your learning
- **Build automation scripts** for real infrastructure tasks
- **Move to Module 003**: Git and Version Control

### Quick Reference

```bash
# System packages
sudo apt update                     # Update lists (Ubuntu)
sudo apt install package            # Install (Ubuntu)
sudo dnf install package            # Install (RHEL)
apt search keyword                  # Search
apt show package                    # Info

# Python packages
pip install package                 # Install
pip install -r requirements.txt     # Install from file
pip freeze > requirements.txt       # Export
pip list --outdated                 # Check updates

# Virtual environments
python3 -m venv env                 # Create
source env/bin/activate             # Activate
deactivate                          # Deactivate

# Build from source
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
sudo ldconfig
```

---

**End of Lecture 05**

**Congratulations!** You've completed all lectures in Module 002: Linux Essentials. Continue with the hands-on exercises to practice these skills in real scenarios.
