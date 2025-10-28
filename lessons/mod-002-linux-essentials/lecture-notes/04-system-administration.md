# Lecture 04: System Administration Basics

## Table of Contents
1. [Introduction](#introduction)
2. [Package Management](#package-management)
3. [Service Management with systemd](#service-management-with-systemd)
4. [Process Management](#process-management)
5. [System Monitoring](#system-monitoring)
6. [Log Files and Analysis](#log-files-and-analysis)
7. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

System administration is the backbone of AI infrastructure engineering. As an AI Infrastructure Engineer, you'll install ML frameworks, manage GPU services, monitor training processes, and debug system issues. Mastering system administration ensures your ML infrastructure runs reliably and efficiently.

This lecture covers essential system administration skills: package management, service control, process management, system monitoring, and log analysis - all critical for maintaining production AI systems.

### Learning Objectives

By the end of this lecture, you will:
- Manage system packages with apt/yum/dnf
- Control services using systemd
- Monitor and manage processes effectively
- Track system resource usage (CPU, memory, disk)
- Analyze system logs for troubleshooting
- Apply these skills to AI infrastructure scenarios

### Prerequisites
- Lectures 01-03 (Linux fundamentals, file systems, permissions)
- Root/sudo access to a Linux system
- Basic understanding of command-line operations

### Why System Administration for AI?

**Infrastructure Reliability**: ML training jobs run for hours or days. System failures waste time and resources.

**Resource Management**: GPUs, memory, and storage must be monitored and optimized.

**Dependency Management**: ML frameworks have complex dependencies that must be carefully maintained.

**Service Orchestration**: APIs, databases, and model servers must work together seamlessly.

**Troubleshooting**: When things break (and they will), you need to diagnose and fix issues quickly.

**Duration**: 120 minutes
**Difficulty**: Intermediate

---

## Package Management

### Understanding Package Management

A **package** is a compressed archive containing:
- Compiled binaries or scripts
- Configuration files
- Documentation
- Metadata (dependencies, version, description)
- Installation/removal scripts

**Package managers** automate software installation, updates, and dependency resolution.

### Package Manager Types

**High-Level** (User-friendly, handles dependencies):
- `apt` / `apt-get` (Debian, Ubuntu)
- `yum` / `dnf` (RHEL, CentOS, Fedora)
- `zypper` (openSUSE)

**Low-Level** (Manual dependency handling):
- `dpkg` (Debian packages)
- `rpm` (Red Hat packages)

### APT - Debian/Ubuntu Package Manager

#### Essential APT Commands

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

# Upgrade without confirmation (for scripts)
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

#### Managing Repositories

Repository configuration: `/etc/apt/sources.list` and `/etc/apt/sources.list.d/`

```bash
# View current repositories
cat /etc/apt/sources.list
ls /etc/apt/sources.list.d/

# Add repository (PPA)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Add repository manually
echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

# Add GPG key for repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Remove repository
sudo add-apt-repository --remove ppa:deadsnakes/ppa
sudo rm /etc/apt/sources.list.d/docker.list
```

#### AI/ML Package Installation Examples

**Python Development Environment**:
```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    wget
```

**System ML Dependencies**:
```bash
# Linear algebra libraries
sudo apt install -y \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev

# HDF5 for large datasets
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

**NVIDIA CUDA Installation**:
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

**Docker Installation**:
```bash
# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Verify
docker --version
```

### YUM/DNF - RHEL/CentOS Package Manager

**DNF** is the modern replacement for YUM (same commands work for both).

#### Basic YUM/DNF Commands

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

#### Managing Repositories

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

#### AI/ML on RHEL/CentOS

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
sudo dnf config-manager --add-repo \
    https://developer.download.nvidia.com/compute/cuda/repos/rhel8/x86_64/cuda-rhel8.repo
sudo dnf install -y cuda-toolkit-11-8

# Docker
sudo dnf config-manager --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl start docker
sudo systemctl enable docker
```

### Holding and Pinning Packages

Sometimes you need to prevent certain packages from being updated.

```bash
# Hold package (prevent updates) - APT
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

---

## Service Management with systemd

Modern Linux systems use **systemd** as the init system and service manager.

### Understanding systemd

**systemd** manages:
- System services (daemons)
- Boot process
- Device management
- System logging (journald)
- Timer-based activation (replaces cron)

**Unit Files**: Configuration files defining services, stored in:
- `/etc/systemd/system/` - System units (highest priority)
- `/usr/lib/systemd/system/` - Package units (default)
- `/run/systemd/system/` - Runtime units

### Essential systemctl Commands

```bash
# Service status
systemctl status nginx
systemctl status ml-inference

# Start/stop services
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx      # Reload config without restart

# Enable/disable at boot
sudo systemctl enable nginx      # Start on boot
sudo systemctl disable nginx     # Don't start on boot
sudo systemctl enable --now nginx  # Enable and start immediately

# Check if enabled
systemctl is-enabled nginx
systemctl is-active nginx
systemctl is-failed nginx

# List all services
systemctl list-units --type=service
systemctl list-units --type=service --state=running
systemctl list-units --type=service --state=failed

# View service dependencies
systemctl list-dependencies nginx
```

### Creating Custom Service Units

**Example: ML Inference Service**

Create `/etc/systemd/system/ml-inference.service`:

```ini
[Unit]
Description=ML Model Inference Service
After=network.target
Requires=postgresql.service

[Service]
Type=simple
User=mlservice
Group=mlservice
WorkingDirectory=/opt/ml-inference
Environment="PATH=/opt/ml-inference/venv/bin"
Environment="MODEL_PATH=/models/production/model.onnx"
ExecStart=/opt/ml-inference/venv/bin/python /opt/ml-inference/serve.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=8G
CPUQuota=400%

[Install]
WantedBy=multi-user.target
```

**Activate the service**:
```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Start and enable
sudo systemctl start ml-inference
sudo systemctl enable ml-inference

# Check status
systemctl status ml-inference

# View logs
journalctl -u ml-inference -f
```

### Service Unit File Sections

**[Unit]** - General information:
- `Description`: Service description
- `After`: Start after these units
- `Before`: Start before these units
- `Requires`: Hard dependencies (fail if not available)
- `Wants`: Soft dependencies (continue if not available)

**[Service]** - Service behavior:
- `Type`: simple, forking, oneshot, notify
- `User/Group`: Run as specific user
- `WorkingDirectory`: Working directory
- `Environment`: Environment variables
- `EnvironmentFile`: Load env vars from file
- `ExecStart`: Command to start
- `ExecStop`: Command to stop
- `ExecReload`: Command to reload
- `Restart`: Restart policy (no, always, on-failure, on-abnormal)
- `RestartSec`: Wait before restart
- `StandardOutput/StandardError`: Where to send output

**[Install]** - Installation information:
- `WantedBy`: Target to attach to (usually multi-user.target)

### Resource Limits in systemd

```ini
[Service]
# CPU limits
CPUQuota=200%                # 2 cores max
CPUWeight=100                # Relative weight (1-10000)

# Memory limits
MemoryMax=8G                 # Hard limit
MemoryHigh=6G                # Soft limit (throttle at this point)

# I/O limits
IOReadBandwidthMax=/dev/sda 100M
IOWriteBandwidthMax=/dev/sda 50M

# Task limits
TasksMax=500                 # Max number of tasks/threads
```

### Example: Training Job Scheduler

Create `/etc/systemd/system/ml-training@.service`:

```ini
[Unit]
Description=ML Training Job for GPU %i
After=network.target

[Service]
Type=oneshot
User=mluser
WorkingDirectory=/opt/ml-training
Environment="CUDA_VISIBLE_DEVICES=%i"
ExecStart=/opt/ml-training/venv/bin/python train.py \
    --gpu %i \
    --config /etc/ml-training/configs/gpu%i.yaml
StandardOutput=journal
StandardError=journal
TimeoutSec=48h

[Install]
WantedBy=multi-user.target
```

**Usage**:
```bash
# Start training on GPU 0
sudo systemctl start ml-training@0

# Start on multiple GPUs
sudo systemctl start ml-training@{0,1,2,3}

# Check status
systemctl status ml-training@0
```

### Viewing Logs with journalctl

```bash
# View all logs
journalctl

# Service-specific logs
journalctl -u ml-inference

# Follow logs (real-time)
journalctl -u ml-inference -f

# Recent logs
journalctl -u ml-inference -n 100     # Last 100 lines
journalctl -u ml-inference --since "1 hour ago"
journalctl -u ml-inference --since "2024-01-15 14:00"
journalctl -u ml-inference --since today

# Priority levels
journalctl -p err                     # Errors only
journalctl -p warning                 # Warnings and above

# By boot
journalctl -b                         # Current boot
journalctl -b -1                      # Previous boot

# Output formats
journalctl -u ml-inference -o json-pretty
journalctl -u ml-inference -o cat     # No metadata

# Disk usage
journalctl --disk-usage

# Cleanup old logs
sudo journalctl --vacuum-time=30d     # Keep 30 days
sudo journalctl --vacuum-size=1G      # Keep 1GB
```

---

## Process Management

### Understanding Processes

A **process** is a running instance of a program. Each process has:
- **PID** (Process ID): Unique identifier
- **PPID** (Parent Process ID): Process that created it
- **UID/GID**: User and group ownership
- **State**: Running, sleeping, stopped, zombie
- **Memory**: Code, data, stack, heap
- **Priority**: CPU scheduling priority

### Process States

**R - Running/Runnable**: Executing or ready to execute
**S - Sleeping (Interruptible)**: Waiting for event (I/O, timer)
**D - Disk Sleep (Uninterruptible)**: Waiting for disk I/O
**T - Stopped**: Suspended by signal (Ctrl+Z)
**Z - Zombie**: Terminated but parent hasn't read exit status
**I - Idle**: Kernel thread

### Viewing Processes with ps

```bash
# Simple view (current terminal only)
ps

# All user's processes
ps -u alice
ps -u $(whoami)

# All processes (BSD style)
ps aux

# All processes (Unix style)
ps -ef

# Sort by CPU usage
ps aux --sort=-%cpu | head -10

# Sort by memory usage
ps aux --sort=-%mem | head -10

# Find specific process
ps aux | grep python
ps aux | grep [p]ython          # Excludes grep itself

# Custom output format
ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%cpu | head

# Process tree (hierarchy)
ps auxf                         # ASCII tree
ps -ejH                         # Alternative tree format
pstree                          # Dedicated tree command
pstree -p                       # With PIDs
```

### AI/ML Process Queries

```bash
# Find all Python processes
ps aux | grep python

# Find GPU processes
ps aux | grep cuda
ps aux | grep nvidia

# Find training jobs
ps aux | grep train

# Jupyter notebook processes
ps aux | grep jupyter

# Show processes using most memory
ps aux --sort=-%mem | head -20

# Show processes using most CPU
ps aux --sort=-%cpu | head -20
```

### Monitoring with top and htop

**top** - Real-time process monitoring:

```bash
top

# Interactive commands:
# P - Sort by CPU usage
# M - Sort by memory usage
# T - Sort by running time
# k - Kill a process
# r - Renice a process
# u - Show specific user's processes
# 1 - Toggle individual CPU cores
# q - Quit
```

**htop** - Enhanced version:

```bash
# Install htop
sudo apt install htop        # Ubuntu/Debian
sudo yum install htop        # RHEL/CentOS

# Run
htop

# Features:
# - Color-coded display
# - Mouse support
# - Horizontal/vertical scrolling
# - Visual CPU and memory meters
# - Tree view by default
# - Easier process killing

# Function keys:
# F1 - Help
# F3 - Search process
# F4 - Filter processes
# F5 - Tree view
# F6 - Sort by column
# F9 - Kill process
# F10 - Quit
```

### Managing Processes with Signals

**Common Signals**:
- **SIGTERM (15)**: Polite termination request (default)
- **SIGKILL (9)**: Immediate termination (cannot be caught)
- **SIGHUP (1)**: Hangup (reload configuration)
- **SIGINT (2)**: Interrupt (Ctrl+C)
- **SIGSTOP (19)**: Pause process
- **SIGCONT (18)**: Resume process

```bash
# List all signals
kill -l

# Graceful termination (allows cleanup)
kill 1234
kill -15 1234
kill -SIGTERM 1234              # All equivalent

# Force termination (immediate, no cleanup)
kill -9 1234
kill -SIGKILL 1234

# Reload configuration
kill -HUP 1234

# Pause process
kill -STOP 1234

# Resume process
kill -CONT 1234
```

### killall and pkill

```bash
# Kill all processes with name
killall python
killall -9 python               # Force kill

# Kill specific user's processes
killall -u alice python

# Kill by pattern matching
pkill python                    # Kill all python processes
pkill -f train.py               # Kill processes with 'train.py' in command
pkill -u alice                  # Kill all alice's processes
pkill -9 -f "experiment_*"      # Force kill experimental processes

# Combined criteria
pkill -u alice -f python        # Alice's python processes
```

### pgrep - Find Process IDs

```bash
# Find PIDs by name
pgrep python

# Find with full command line
pgrep -f train.py

# Get detailed info
pgrep -l python                 # With process name
pgrep -a python                 # With full command

# Use in scripts
TRAINING_PID=$(pgrep -f train.py)
if [ -n "$TRAINING_PID" ]; then
    echo "Training job running: $TRAINING_PID"
    kill $TRAINING_PID
fi
```

### Job Control

**Foreground vs Background**:
- **Foreground**: Process controls terminal, receives keyboard input
- **Background**: Process runs independently, terminal available

```bash
# Start in background with &
python train.py &
# [1] 5678                     # Job number and PID

# Check job status
jobs

# Suspend foreground job
# Press Ctrl+Z

# Resume in background
bg

# Resume in foreground
fg

# Resume specific job
fg %1                           # Bring job 1 to foreground
bg %2                           # Continue job 2 in background

# Kill specific job
kill %1                         # Kill job 1
```

### nohup - Immune to Hangups

```bash
# Basic nohup
nohup python train.py &
# Output goes to nohup.out

# Redirect output
nohup python train.py > training.log 2>&1 &

# Alternative: disown
python train.py &
disown                          # Detach from shell
```

### Process Priorities (nice/renice)

**Nice** values control process priority:
- Range: -20 (highest priority) to +19 (lowest priority)
- Default: 0
- Lower nice value = higher priority = more CPU time
- Only root can set negative nice values

```bash
# Start with lower priority (nice value +10)
nice -n 10 python train.py

# Start with higher priority (requires sudo)
sudo nice -n -10 python priority_job.py

# Check nice values
ps -eo pid,ppid,ni,comm

# Change priority of running process
renice +10 5678                 # Set nice value to 10
sudo renice -10 5678            # Set nice value to -10 (requires sudo)

# Renice by user
sudo renice +5 -u alice

# AI Infrastructure use cases:
# Experimental training (low priority)
nice -n 15 python experimental_training.py &

# Production inference (high priority)
sudo nice -n -5 python production_inference.py &
```

---

## System Monitoring

### CPU Monitoring

**top/htop** - Real-time monitoring:
```bash
# View CPU usage
top
htop

# Check load average
uptime
# 14:32:15 up 5 days, 2:15, 3 users, load average: 4.52, 3.87, 2.91

# Load average explained:
# 4.52 = 1-minute average
# 3.87 = 5-minute average
# 2.91 = 15-minute average
# Value > number of CPUs = system overloaded
```

**mpstat** - Detailed CPU statistics:
```bash
# Install sysstat package
sudo apt install sysstat

# Show CPU usage
mpstat 1 5                      # 1 second intervals, 5 reports

# Show all CPUs
mpstat -P ALL 1
```

**Example monitoring script**:
```bash
#!/bin/bash
# Monitor CPU during training

while true; do
    echo "=== $(date) ==="
    mpstat 1 1 | tail -1
    sleep 60
done
```

### Memory Monitoring

**free** - Memory usage:
```bash
# Show memory usage
free -h                         # Human-readable

# Output:
#               total        used        free      shared  buff/cache   available
# Mem:           62Gi        30Gi       8.0Gi       2.0Gi        24Gi        28Gi
# Swap:         8.0Gi       0.0Gi       8.0Gi

# What each column means:
# total: Total physical RAM
# used: RAM used by programs
# free: Completely unused RAM
# shared: RAM used by tmpfs
# buff/cache: RAM used for disk caching (can be freed if needed)
# available: RAM available for new programs (free + reclaimable cache)
```

**vmstat** - Virtual memory statistics:
```bash
# Show memory and CPU stats
vmstat 1 5                      # 1 second intervals, 5 reports

# Output columns:
# r: Running processes
# b: Blocked processes
# swpd: Virtual memory used
# free: Idle memory
# buff: Buffer memory
# cache: Cache memory
# si: Memory swapped in from disk
# so: Memory swapped out to disk
```

**Monitoring OOM (Out of Memory) events**:
```bash
# Check for OOM killer activity
dmesg | grep -i "out of memory"
dmesg | grep -i "oom"

# View OOM score for processes (higher = more likely to be killed)
cat /proc/1234/oom_score
```

### Disk Monitoring

**df** - Disk space usage:
```bash
# Show disk usage
df -h                           # Human-readable

# Show specific filesystem
df -h /data

# Show inodes
df -i                           # Inode usage

# Example output:
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1       100G   45G   50G  48% /
# /dev/sdb1       1.0T  800G  200G  80% /data
```

**du** - Directory disk usage:
```bash
# Show directory size
du -sh /data/models

# Show subdirectory sizes
du -h --max-depth=1 /data

# Find largest directories
du -h /data | sort -rh | head -20

# Find large files
find /data -type f -size +1G -exec ls -lh {} \;
```

**iostat** - I/O statistics:
```bash
# Install sysstat
sudo apt install sysstat

# Show I/O stats
iostat -x 1 5                   # Extended stats, 1s intervals

# Key metrics:
# %util: Percentage of time device was busy
# r/s: Reads per second
# w/s: Writes per second
# rkB/s: KB read per second
# wkB/s: KB written per second
```

**iotop** - Real-time I/O monitoring:
```bash
# Install iotop
sudo apt install iotop

# Run iotop
sudo iotop

# Show only active I/O
sudo iotop -o
```

### GPU Monitoring

**nvidia-smi** - NVIDIA GPU monitoring:
```bash
# Show GPU status
nvidia-smi

# Watch GPU usage (update every second)
watch -n 1 nvidia-smi

# Query specific information
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total \
    --format=csv

# Query compute processes
nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv

# Find which process is using GPU
nvidia-smi pmon

# Log GPU metrics to file
while true; do
    nvidia-smi --query-gpu=timestamp,temperature.gpu,utilization.gpu,memory.used \
        --format=csv >> gpu_metrics.log
    sleep 60
done
```

### Comprehensive System Monitoring Script

```bash
#!/bin/bash
# system-health.sh - Monitor system resources

LOG_FILE="/var/log/system-health.log"

echo "=== System Health Report $(date) ===" | tee -a "$LOG_FILE"

# CPU
echo "" | tee -a "$LOG_FILE"
echo "--- CPU ---" | tee -a "$LOG_FILE"
uptime | tee -a "$LOG_FILE"
mpstat 1 1 | tail -1 | tee -a "$LOG_FILE"

# Memory
echo "" | tee -a "$LOG_FILE"
echo "--- Memory ---" | tee -a "$LOG_FILE"
free -h | tee -a "$LOG_FILE"

# Disk
echo "" | tee -a "$LOG_FILE"
echo "--- Disk ---" | tee -a "$LOG_FILE"
df -h | grep -v tmpfs | grep -v loop | tee -a "$LOG_FILE"

# Top processes by CPU
echo "" | tee -a "$LOG_FILE"
echo "--- Top CPU Processes ---" | tee -a "$LOG_FILE"
ps aux --sort=-%cpu | head -6 | tee -a "$LOG_FILE"

# Top processes by memory
echo "" | tee -a "$LOG_FILE"
echo "--- Top Memory Processes ---" | tee -a "$LOG_FILE"
ps aux --sort=-%mem | head -6 | tee -a "$LOG_FILE"

# GPU (if available)
if command -v nvidia-smi &> /dev/null; then
    echo "" | tee -a "$LOG_FILE"
    echo "--- GPU ---" | tee -a "$LOG_FILE"
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total \
        --format=csv | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
```

---

## Log Files and Analysis

### Understanding Linux Logging

**System Logs Location**: `/var/log/`

**Common Log Files**:
- `/var/log/syslog` - General system logs (Debian/Ubuntu)
- `/var/log/messages` - General system logs (RHEL/CentOS)
- `/var/log/auth.log` - Authentication logs
- `/var/log/kern.log` - Kernel logs
- `/var/log/dmesg` - Boot messages
- `/var/log/nginx/` - Nginx web server logs
- `/var/log/apache2/` - Apache web server logs

### Viewing Log Files

```bash
# View entire log
cat /var/log/syslog

# View last lines
tail /var/log/syslog

# Follow log in real-time
tail -f /var/log/syslog

# View with pager
less /var/log/syslog

# View specific number of lines
tail -n 100 /var/log/syslog
head -n 50 /var/log/syslog
```

### Searching Logs

```bash
# Search for errors
grep "ERROR" /var/log/syslog
grep -i "error" /var/log/syslog        # Case-insensitive

# Search for failed authentication
grep "Failed password" /var/log/auth.log

# Search multiple files
grep "cuda" /var/log/*.log

# Show context around matches
grep -A 5 "ERROR" /var/log/syslog      # 5 lines after
grep -B 5 "ERROR" /var/log/syslog      # 5 lines before
grep -C 5 "ERROR" /var/log/syslog      # 5 lines around

# Count occurrences
grep -c "ERROR" /var/log/syslog

# Search with line numbers
grep -n "ERROR" /var/log/syslog
```

### journalctl - systemd Journal

Modern systems use systemd's journal for logging.

```bash
# View all logs
journalctl

# View logs for specific service
journalctl -u nginx
journalctl -u ml-inference

# Follow logs in real-time
journalctl -f
journalctl -u ml-inference -f

# View logs since specific time
journalctl --since "2024-01-15 14:00"
journalctl --since "1 hour ago"
journalctl --since today
journalctl --since yesterday

# View logs between times
journalctl --since "2024-01-15 14:00" --until "2024-01-15 15:00"

# Filter by priority
journalctl -p err                      # Errors only
journalctl -p warning                  # Warnings and above
# Priorities: emerg, alert, crit, err, warning, notice, info, debug

# View kernel messages
journalctl -k
journalctl --dmesg

# View logs from specific boot
journalctl -b                          # Current boot
journalctl -b -1                       # Previous boot
journalctl --list-boots                # List all boots

# Reverse order (newest first)
journalctl -r

# Limit output
journalctl -n 50                       # Last 50 lines
journalctl -u nginx -n 100             # Last 100 lines from nginx

# Output formats
journalctl -o json-pretty              # JSON format
journalctl -o cat                      # Just messages, no metadata
journalctl -o short-iso                # ISO timestamps

# Disk usage
journalctl --disk-usage

# Cleanup old logs
sudo journalctl --vacuum-time=2weeks   # Keep 2 weeks
sudo journalctl --vacuum-size=500M     # Keep 500MB
```

### Log Rotation

**logrotate** automatically rotates, compresses, and removes old logs.

Configuration: `/etc/logrotate.conf` and `/etc/logrotate.d/`

**Example configuration** (`/etc/logrotate.d/ml-training`):
```
/var/log/ml-training/*.log {
    daily                      # Rotate daily
    rotate 7                   # Keep 7 days
    compress                   # Compress old logs
    delaycompress              # Delay compression for 1 rotation
    missingok                  # Don't error if log is missing
    notifempty                 # Don't rotate if empty
    create 0640 mluser mlgroup # Create new log with these permissions
    sharedscripts              # Run scripts once for all logs
    postrotate
        systemctl reload ml-training > /dev/null 2>&1 || true
    endscript
}
```

**Test logrotate**:
```bash
# Test configuration
sudo logrotate -d /etc/logrotate.d/ml-training

# Force rotation
sudo logrotate -f /etc/logrotate.d/ml-training
```

### AI Infrastructure Log Analysis Examples

**Find training errors**:
```bash
# Search for CUDA errors
journalctl -u ml-training | grep -i "cuda"

# Search for out-of-memory errors
journalctl -u ml-training | grep -i "out of memory"
dmesg | grep -i "oom"

# Find failed model loads
grep "Failed to load model" /var/log/ml-inference/*.log

# Check GPU errors
nvidia-smi --query-gpu=index,name,ecc.errors.corrected.aggregate.total \
    --format=csv
```

**Analyze training performance**:
```bash
# Extract epoch times from training logs
grep "Epoch" /var/log/ml-training/training.log | \
    awk '{print $NF}' | \
    awk '{sum+=$1; count++} END {print "Avg:", sum/count}'

# Find longest inference times
grep "inference_time" /var/log/ml-api/api.log | \
    sort -k5 -n -r | head -20

# Count API requests per hour
grep "$(date +%Y-%m-%d)" /var/log/nginx/access.log | \
    cut -d: -f2 | sort | uniq -c
```

**Security monitoring**:
```bash
# Failed SSH attempts
grep "Failed password" /var/log/auth.log | \
    awk '{print $(NF-5)}' | sort | uniq -c | sort -rn

# Successful root logins
grep "session opened for user root" /var/log/auth.log

# Sudo usage
grep "sudo" /var/log/auth.log | tail -20
```

---

## Summary and Key Takeaways

### Commands Mastered

**Package Management**:
- `apt update` / `apt upgrade` - Update and upgrade packages
- `apt install` / `apt remove` - Install and remove packages
- `apt search` / `apt show` - Search and show package info
- `dnf install` / `dnf remove` - RHEL/CentOS package management

**Service Management**:
- `systemctl start/stop/restart` - Control services
- `systemctl enable/disable` - Configure boot behavior
- `systemctl status` - Check service status
- `journalctl -u service` - View service logs

**Process Management**:
- `ps aux` - View all processes
- `top` / `htop` - Interactive monitoring
- `kill` / `pkill` / `killall` - Terminate processes
- `nice` / `renice` - Control process priority
- `pgrep` - Find process IDs

**System Monitoring**:
- `free -h` - Memory usage
- `df -h` - Disk usage
- `du -sh` - Directory sizes
- `uptime` - Load average
- `nvidia-smi` - GPU monitoring

**Log Analysis**:
- `journalctl` - systemd logs
- `tail -f` - Follow log files
- `grep` - Search logs
- `logrotate` - Automatic log rotation

### Key Concepts

1. **Package Management**: Automate software installation with apt/dnf
2. **Service Control**: Manage long-running services with systemd
3. **Process Monitoring**: Track and control running programs
4. **Resource Tracking**: Monitor CPU, memory, disk, and GPU usage
5. **Log Analysis**: Troubleshoot issues through system logs
6. **Automation**: Systemd timers and cron for scheduled tasks

### AI Infrastructure Best Practices

✅ **Pin dependency versions** for reproducibility
✅ **Use systemd services** for production ML applications
✅ **Set resource limits** to prevent resource exhaustion
✅ **Monitor GPU usage** continuously during training
✅ **Implement log rotation** to manage disk space
✅ **Use nice values** to prioritize production workloads
✅ **Regular system updates** for security patches
✅ **Automate health checks** with systemd timers

### Troubleshooting Checklist

When things go wrong, check:
1. Service status: `systemctl status service-name`
2. Service logs: `journalctl -u service-name -n 100`
3. Process list: `ps aux | grep service`
4. Resource usage: `top`, `free -h`, `df -h`
5. System logs: `journalctl -p err --since "1 hour ago"`
6. GPU status: `nvidia-smi` (if applicable)
7. Disk space: `df -h`, `du -sh /var/log`

### Common Issues and Solutions

**Service won't start**:
```bash
systemctl status ml-inference
journalctl -u ml-inference -n 50
# Check: permissions, missing files, port conflicts
```

**High CPU usage**:
```bash
top -o %CPU
# Identify process, check if expected, renice if needed
```

**Out of memory**:
```bash
free -h
dmesg | grep -i oom
# Check memory leaks, reduce batch size, add swap
```

**Disk full**:
```bash
df -h
du -h / | sort -rh | head -20
# Clean logs, remove old models, compress data
```

### Next Steps

In **Lecture 05: Introduction to Shell Scripting**, you'll learn:
- Writing bash scripts for automation
- Variables, loops, and conditionals
- Functions and argument processing
- Error handling basics
- Automating system administration tasks

### Quick Reference Card

```bash
# Package Management
sudo apt update && sudo apt upgrade -y
sudo apt install package-name
apt search keyword

# Service Management
sudo systemctl restart service-name
systemctl status service-name
journalctl -u service-name -f

# Process Management
ps aux --sort=-%cpu | head
kill -9 PID
nice -n 10 command

# Monitoring
top
htop
free -h
df -h
nvidia-smi

# Logs
journalctl -u service-name -f
tail -f /var/log/syslog
grep ERROR /var/log/syslog
```

---

**End of Lecture 04: System Administration Basics**

You now have the foundational system administration skills needed to manage AI infrastructure. Practice these commands regularly to build muscle memory and confidence.

**Next**: Lecture 05 - Introduction to Shell Scripting
