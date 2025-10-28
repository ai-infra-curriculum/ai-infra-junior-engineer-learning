# Lecture 02: File System and Navigation

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding the Linux File System](#understanding-the-linux-file-system)
3. [Essential Navigation Commands](#essential-navigation-commands)
4. [File Operations](#file-operations)
5. [Finding Files and Directories](#finding-files-and-directories)
6. [Working with Links](#working-with-links)
7. [Archiving and Compression](#archiving-and-compression)
8. [Best Practices for AI Infrastructure](#best-practices-for-ai-infrastructure)
9. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

As an AI Infrastructure Engineer, you'll spend significant time working with Linux file systems. Whether deploying machine learning models, managing GPU servers, or orchestrating containers, understanding the file system structure and navigation is fundamental to all your future work.

This lecture introduces you to the Linux file system hierarchy and essential commands for navigating and managing files and directories in AI infrastructure scenarios.

### Learning Objectives

By the end of this lecture, you will:
- Understand the Linux file system hierarchy and organization
- Navigate efficiently using command-line tools
- Perform file and directory operations confidently
- Find files quickly using various search tools
- Work with symbolic and hard links
- Create and extract archives for data and model management
- Apply Linux fundamentals to AI infrastructure scenarios

### Prerequisites
- Lecture 01: Introduction to Linux and Command Line
- Access to a Linux system (Ubuntu 22.04 LTS, CentOS 8, or similar)
- Basic understanding of what an operating system does
- Terminal emulator installed and accessible

### Why File System Knowledge for AI Infrastructure?

**Data Management**: Training datasets, model files, and results must be organized properly across potentially hundreds of GB or TB.

**Model Storage**: Understanding where and how to store models, checkpoints, and configurations ensures reproducible deployments.

**Performance**: Knowing which filesystems to use for different workloads (NVMe SSDs for training data, network storage for archives) impacts performance.

**Collaboration**: Proper file organization enables teams to work together on ML projects effectively.

## Understanding the Linux File System

### The Filesystem Hierarchy Standard (FHS)

Unlike Windows with drive letters (C:\, D:\), Linux uses a single unified tree structure starting from the root directory `/`.

```
/                          # Root - top of filesystem hierarchy
├── bin/                   # Essential user command binaries
├── boot/                  # Boot loader files (kernel, initrd)
├── dev/                   # Device files (hardware interfaces)
├── etc/                   # System configuration files
├── home/                  # User home directories
│   ├── alice/
│   └── bob/
├── lib/                   # Shared libraries
├── media/                 # Removable media mount points
├── mnt/                   # Temporary mount points
├── opt/                   # Optional/add-on software packages
├── proc/                  # Process and kernel information (virtual)
├── root/                  # Root user's home directory
├── run/                   # Runtime data
├── sbin/                  # System administration binaries
├── srv/                   # Service data (web servers, FTP)
├── sys/                   # System/kernel information (virtual)
├── tmp/                   # Temporary files (cleared on reboot)
├── usr/                   # User programs and data
│   ├── bin/              # User command binaries
│   ├── lib/              # Libraries for /usr/bin
│   ├── local/            # Locally installed software
│   └── share/            # Architecture-independent data
└── var/                   # Variable data (logs, databases)
    ├── log/              # Log files
    ├── cache/            # Application cache
    └── tmp/              # Temp files (persistent across reboots)
```

### Key Directories for AI Infrastructure

**`/home/username/`**: Your personal workspace. Store ML notebooks, training scripts, and datasets here during development.

**Example**:
```bash
/home/alice/
├── ml-projects/
│   ├── image-classifier/
│   │   ├── data/
│   │   ├── models/
│   │   ├── notebooks/
│   │   └── train.py
│   └── nlp-sentiment/
└── datasets/
```

**`/opt/`**: Install custom ML frameworks, CUDA toolkits, or proprietary software here.

**Example**:
```bash
/opt/
├── cuda-11.8/
├── ml-framework/
└── custom-models/
```

**`/var/log/`**: Critical for troubleshooting. Training logs, service logs, and error messages live here.

**Example**:
```bash
/var/log/
├── training/
│   ├── model-2024-01-15.log
│   └── errors.log
├── inference/
└── system/
```

**`/etc/`**: Configuration files for services like Docker, Kubernetes, and NVIDIA drivers.

**Example**:
```bash
/etc/
├── docker/
│   └── daemon.json
├── kubernetes/
└── nvidia/
    └── cuda.conf
```

**`/tmp/`**: Temporary storage for intermediate training data or model checkpoints. **Warning: Contents may be deleted on reboot!**

**`/usr/local/`**: Custom-built software like specific Python versions or ML libraries compiled from source.

### Path Concepts

**Absolute Path**: Starts from root directory `/`

```bash
/home/alice/ml-projects/image-classifier/train.py
```

**Relative Path**: Relative to current location

```bash
# If currently in /home/alice/
ml-projects/image-classifier/train.py

# If currently in /home/alice/ml-projects/
image-classifier/train.py
```

**Special Path Symbols**:
- `.` - Current directory
- `..` - Parent directory
- `~` - Current user's home directory
- `-` - Previous directory

```bash
cd ~                    # Go to home directory
cd ..                   # Go up one level
cd -                    # Return to previous directory
cd ~/ml-projects        # Go to ml-projects in home
./script.sh             # Run script in current directory
```

## Essential Navigation Commands

### pwd - Print Working Directory

Always know where you are in the filesystem.

```bash
pwd
# Output: /home/alice/ml-projects

# Useful in scripts to verify location
CURRENT_DIR=$(pwd)
echo "Running training from: $CURRENT_DIR"
```

**AI Infrastructure Use Case**: When running training jobs, always verify the working directory to ensure data paths are correct.

```bash
#!/bin/bash
# Verify we're in the right place before training
if [[ $(pwd) != "/opt/ml-training" ]]; then
    echo "Error: Must run from /opt/ml-training"
    exit 1
fi

python train.py
```

### ls - List Directory Contents

The most frequently used Linux command. List files and directories with various options.

**Basic Usage**:
```bash
ls                      # List files in current directory
ls /var/log            # List files in /var/log
ls ~                   # List files in home directory
```

**Common Options**:
```bash
ls -l                   # Long format (permissions, owner, size, date)
ls -a                   # Show hidden files (starting with .)
ls -h                   # Human-readable sizes (KB, MB, GB)
ls -t                   # Sort by modification time (newest first)
ls -r                   # Reverse order
ls -R                   # Recursive (show subdirectories)

# Combine options
ls -lah                 # Long format, all files, human-readable
ls -lt                  # Long format, sorted by time
ls -lhS                 # Long format, human-readable, sorted by size
```

**Practical Examples**:
```bash
# Find largest model files in current directory
ls -lhS *.h5 | head -5

# List all Python files with details
ls -lh *.py

# Find recently modified training checkpoints
ls -lt checkpoints/ | head -10

# Check total disk usage
ls -lh --block-size=G
```

**Output Explanation**:
```bash
$ ls -lh model.h5
-rw-r--r-- 1 alice mlteam 500M Oct 15 14:30 model.h5
│   │  │  │ │     │      │    │           │
│   │  │  │ │     │      │    │           └─ Filename
│   │  │  │ │     │      │    └─ Modification date/time
│   │  │  │ │     │      └─ File size (human readable)
│   │  │  │ │     └─ Group owner
│   │  │  │ └─ File owner
│   │  │  └─ Number of hard links
│   │  └─ Group permissions (read)
│   └─ Owner permissions (read, write)
│   └─ File type (- = regular file, d = directory, l = link)
```

### cd - Change Directory

Navigate through the filesystem efficiently.

```bash
cd /var/log                      # Absolute path
cd logs/training                 # Relative path
cd                               # Go to home directory
cd ~                             # Also goes to home
cd ..                            # Go up one level
cd ../..                         # Go up two levels
cd -                             # Toggle to previous directory

# Advanced navigation
cd ~/ml-projects/model-v2        # Direct jump using absolute path
cd ../../data/processed          # Relative navigation
```

**Pro Tips**:
```bash
# Quick directory switching
cd /var/log/nginx
cd -                    # Returns to previous directory
cd -                    # Back to /var/log/nginx (toggle)

# Navigate to sibling directory
cd ../another-project   # From /home/alice/project-a to project-b

# Use tab completion to save time
cd /var/lo<TAB>         # Autocompletes to /var/log/
```

**AI Infrastructure Example**:
```bash
# Navigate to training directory
cd ~/ml-projects/image-classifier

# Check where we are
pwd

# Go to data directory
cd data/raw

# Back to project root
cd ../..

# Check training logs
cd /var/log/training

# Return to project
cd -
```

### tree - Visual Directory Structure

Display directory hierarchy as a tree (may need installation: `sudo apt install tree`).

```bash
tree                           # Show tree from current directory
tree -L 2                      # Limit depth to 2 levels
tree -d                        # Directories only
tree -h                        # Human-readable sizes
tree -a                        # Include hidden files

# Practical ML example
tree -L 3 ml-project/
# ml-project/
# ├── data/
# │   ├── raw/
# │   └── processed/
# ├── models/
# │   ├── checkpoints/
# │   └── final/
# ├── notebooks/
# └── src/
#     ├── train.py
#     └── evaluate.py
```

**Exclude Patterns**:
```bash
# Exclude Python cache and git directories
tree -I '__pycache__|.git'

# Exclude large data directories
tree -I 'data|*.h5|*.pt'
```

## File Operations

### Creating Files and Directories

**touch - Create Empty Files**:
```bash
touch train.py                    # Create single file
touch model.py utils.py          # Create multiple files
touch experiment_{1..5}.log      # Create numbered files

# Update modification time of existing file
touch -t 202310151430 model.h5   # Set specific timestamp
```

**mkdir - Create Directories**:
```bash
mkdir models                     # Create single directory
mkdir data logs checkpoints      # Create multiple directories
mkdir -p data/raw/images         # Create parent directories as needed
mkdir -p experiments/{exp1,exp2,exp3}/checkpoints

# Verify structure
tree experiments/
# experiments/
# ├── exp1/
# │   └── checkpoints/
# ├── exp2/
# │   └── checkpoints/
# └── exp3/
#     └── checkpoints/
```

**AI Infrastructure Example**:
```bash
# Set up ML project structure
mkdir -p ml-project/{data/{raw,processed},models/{checkpoints,final},notebooks,src,logs}

tree ml-project/
# ml-project/
# ├── data/
# │   ├── raw/
# │   └── processed/
# ├── logs/
# ├── models/
# │   ├── checkpoints/
# │   └── final/
# ├── notebooks/
# └── src/
```

### Copying Files and Directories

**cp - Copy Files**:
```bash
cp source.py destination.py              # Copy file
cp model.h5 models/backup/               # Copy to directory
cp -r experiments/ backup/               # Copy directory recursively
cp -p config.yaml config.yaml.bak        # Preserve timestamps
cp -i model.h5 models/                   # Interactive (prompt before overwrite)
cp -u *.py backup/                       # Update (copy only newer files)

# Advanced patterns
cp train_{v1,v2}.py archive/             # Copy specific files
cp --backup=numbered model.h5 models/    # Create numbered backups
```

**Real-World ML Scenarios**:
```bash
# Backup model before retraining
cp -p model_best.h5 model_best.h5.$(date +%Y%m%d)

# Copy dataset to local SSD for faster training
cp -r /mnt/nas/datasets/imagenet /local/ssd/datasets/

# Duplicate experiment configuration
cp -r experiments/baseline experiments/experiment_2

# Backup with timestamp
cp model.h5 backups/model_$(date +%Y%m%d_%H%M%S).h5
```

### Moving and Renaming

**mv - Move/Rename Files**:
```bash
mv old_name.py new_name.py              # Rename file
mv model.h5 models/                     # Move file
mv experiments/old_exp experiments/new  # Rename directory
mv -i file.py dest/                     # Interactive mode
mv *.log logs/                          # Move multiple files
mv -n file.py dest/                     # No overwrite

# Bulk renaming with pattern
for file in model_v*.h5; do
    mv "$file" "${file/v/version_}"
done
# model_v1.h5 → model_version_1.h5
```

**Practical Uses**:
```bash
# Organize trained models
mv model_epoch_*.h5 models/checkpoints/

# Rename experiment after completion
mv experiment_temp experiment_resnet50_baseline

# Move logs to archive
mv logs/training_$(date -d '30 days ago' +%Y%m).log logs/archive/

# Stage model for deployment
mv models/checkpoints/best_model.h5 models/production/
```

### Deleting Files and Directories

**rm - Remove Files** (⚠️ **Use with caution - no undo!**):
```bash
rm file.txt                         # Delete single file
rm file1.txt file2.txt              # Delete multiple files
rm -i *.log                         # Interactive (confirm each deletion)
rm -f locked_file                   # Force delete (ignore warnings)
rm -r directory/                    # Delete directory recursively
rm -rf temp_data/                   # Force recursive delete

# Safe practices
rm -i *.h5                          # Always confirm for important files
rm -v deleted_file                  # Verbose (show what's deleted)
```

**⚠️ Dangerous Commands - Never Run These**:
```bash
# NEVER do these - they delete everything!
rm -rf /                            # Deletes entire system (protected on modern systems)
rm -rf /*                           # Same disaster
rm -rf $VARIABLE/                   # If $VARIABLE is empty, deletes from root!

# Always verify before running rm -rf
echo rm -rf $DIR/*                  # Check what would be deleted
```

**Safe Deletion Practices**:
```bash
# Create trash directory instead of immediate deletion
mkdir -p ~/.trash
alias trash='mv --target-directory=$HOME/.trash'

# Use trash instead of rm
trash old_model.h5                  # Moves to trash, can be recovered

# Empty trash periodically
find ~/.trash -mtime +30 -delete    # Delete files older than 30 days

# For critical operations, use interactive mode
rm -ri experiments/failed_*         # Confirm each deletion
```

**AI Infrastructure Safety**:
```bash
# Before deleting training data, verify
ls -lh data/to_delete/
du -sh data/to_delete/
# Then delete
rm -rf data/to_delete/

# Create a cleanup script with confirmation
cat > cleanup.sh << 'EOF'
#!/bin/bash
echo "This will delete:"
find checkpoints/ -mtime +7 -name "*.ckpt"
read -p "Proceed? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    find checkpoints/ -mtime +7 -name "*.ckpt" -delete
    echo "Cleanup complete"
fi
EOF
```

### Viewing File Contents

**cat - Concatenate and Display**:
```bash
cat file.txt                        # Display entire file
cat file1.txt file2.txt             # Display multiple files
cat file1.txt file2.txt > combined.txt  # Combine files
cat -n file.py                      # Show line numbers
```

**less - Page Through Files**:
```bash
less large_log.txt                  # View large file with pagination

# Navigation in less:
# Space/PgDn - Next page
# b/PgUp - Previous page
# /pattern - Search forward
# ?pattern - Search backward
# n - Next search result
# q - Quit
```

**head/tail - View File Beginnings/Ends**:
```bash
head file.txt                       # First 10 lines
head -n 20 file.txt                # First 20 lines
tail file.txt                       # Last 10 lines
tail -n 50 training.log            # Last 50 lines
tail -f training.log               # Follow log in real-time (Ctrl+C to stop)

# Monitor training progress
tail -f logs/training.log | grep "epoch"
```

**Practical AI Examples**:
```bash
# Check first few lines of CSV dataset
head -20 data.csv

# Monitor training in real-time
tail -f training.log

# View last 100 errors
grep ERROR training.log | tail -100

# Check model architecture saved in text
cat model_architecture.txt

# Compare configurations
cat config_v1.yaml config_v2.yaml

# Extract specific lines
sed -n '100,200p' large_dataset.csv  # Lines 100-200
```

## Finding Files and Directories

### find - Powerful File Search

The `find` command is one of the most powerful tools for locating files and directories.

**Basic Syntax**: `find [path] [expression]`

**Search by Name**:
```bash
find . -name "*.py"                    # Find all Python files
find /var/log -name "*.log"            # Find log files
find ~ -name "model.h5"                # Find specific file
find . -iname "*.PY"                   # Case-insensitive search
```

**Search by Type**:
```bash
find . -type f                         # Files only
find . -type d                         # Directories only
find . -type l                         # Symbolic links only
```

**Search by Size**:
```bash
find . -size +1G                       # Files larger than 1GB
find . -size -100M                     # Files smaller than 100MB
find . -size +500M -size -2G           # Files between 500MB and 2GB

# Find large model files
find models/ -type f -size +100M -exec ls -lh {} \;
```

**Search by Time**:
```bash
find . -mtime -7                       # Modified in last 7 days
find . -mtime +30                      # Modified more than 30 days ago
find . -mmin -60                       # Modified in last 60 minutes
find . -atime -1                       # Accessed in last day
```

**Execute Actions**:
```bash
# Delete old checkpoint files
find checkpoints/ -name "*.ckpt" -mtime +7 -delete

# Copy recent models to backup
find models/ -name "*.h5" -mtime -1 -exec cp {} backup/ \;

# List large files with details
find . -size +1G -exec ls -lh {} \;

# Count Python files
find . -name "*.py" -type f | wc -l

# Find and compress old logs
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
```

**AI Infrastructure Examples**:
```bash
# Find all Jupyter notebooks
find . -name "*.ipynb"

# Find model files larger than 500MB
find . \( -name "*.h5" -o -name "*.pt" \) -size +500M

# Find recently modified training scripts
find . -name "train*.py" -mtime -7

# Locate all requirements.txt files in projects
find ~ -name "requirements.txt"

# Find empty directories (failed experiments?)
find experiments/ -type d -empty

# Find world-writable files (security issue)
find . -type f -perm 0777

# Clean up Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +

# Find datasets not accessed in 90 days
find /data/datasets -type f -atime +90 -size +1G

# Find broken symlinks
find . -type l ! -exec test -e {} \; -print
```

### locate - Fast Database Search

Faster than `find` but uses a database (updated daily).

```bash
# Update database first (requires sudo)
sudo updatedb

# Search for files
locate model.h5                        # Find all model.h5 files
locate -i python                       # Case-insensitive
locate -c "*.log"                      # Count matches
locate -e file.txt                     # Only existing files

# Limit results
locate -l 10 "*.py"                    # Show first 10 results

# Search specific paths
locate -b '\model.h5'                  # Basename only (exact name)
```

**When to Use**:
- Use `locate` for quick searches by name
- Use `find` for complex queries (size, time, permissions)

### which - Find Command Location

Locate executables in PATH.

```bash
which python                           # /usr/bin/python
which python3                          # /usr/bin/python3
which docker                           # /usr/bin/docker
which nvidia-smi                       # /usr/bin/nvidia-smi

# Find all instances
which -a python                        # Show all python in PATH
```

**AI Infrastructure Use**:
```bash
# Verify correct Python version
which python
python --version

# Check CUDA installation
which nvcc
nvcc --version

# Locate Docker
which docker
docker --version

# Find pip location (virtual env check)
which pip

# Verify virtual environment is active
which python
# Should show: /path/to/venv/bin/python
```

### whereis - Locate Binary, Source, Manual

```bash
whereis python                         # Binary, source, man page
whereis -b python                      # Binary only
whereis -m python                      # Man page only
```

## Working with Links

Linux supports two types of links: **hard links** and **symbolic (soft) links**.

### Symbolic Links (Symlinks)

A symbolic link is like a shortcut - it points to another file or directory.

**Creating Symlinks**:
```bash
ln -s /path/to/original /path/to/link

# Examples
ln -s /data/datasets ~/datasets                    # Quick access to datasets
ln -s /opt/cuda-11.8 /opt/cuda                     # Version management
ln -s models/model_best.h5 current_model.h5       # Point to latest model
ln -s /mnt/nas/training_data ~/training_data      # Network storage shortcut

# Verify
ls -l current_model.h5
# lrwxrwxrwx 1 alice mlteam 20 Oct 15 14:30 current_model.h5 -> models/model_best.h5
```

**Symlink Characteristics**:
- Can link to files or directories
- Can span file systems (different partitions/drives)
- Become broken if target is moved or deleted
- Have their own permissions (usually 777, but target permissions apply)
- Small file size (just stores the path)

**AI Infrastructure Use Cases**:
```bash
# Link to current production model
ln -s models/model_v3.h5 production_model.h5

# Version management for datasets
ln -s /data/imagenet-2023 /data/imagenet-current

# Python virtual environment
ln -s /opt/venvs/ml-env ~/.venv

# Configuration management
ln -s /etc/ml-service/config.prod.yaml /etc/ml-service/config.yaml

# Quick access to log directory
ln -s /var/log/ml-training ~/logs

# Shared model repository
ln -s /mnt/shared/models ~/shared-models
```

### Hard Links

Hard links create multiple directory entries for the same file data.

```bash
ln original.txt hardlink.txt          # Create hard link (no -s flag)

# Verify - same inode number
ls -li original.txt hardlink.txt
# 12345678 -rw-r--r-- 2 alice mlteam 1024 Oct 15 14:30 original.txt
# 12345678 -rw-r--r-- 2 alice mlteam 1024 Oct 15 14:30 hardlink.txt
#    ↑ Same inode = same file data
```

**Hard Link Characteristics**:
- Share the same inode (same file data)
- Cannot link to directories (in most cases)
- Cannot span file systems
- File persists until all hard links are deleted
- Indistinguishable from original

**When to Use**:
- Use **symlinks** for most cases (directories, cross-filesystem, clarity)
- Use **hard links** for backup scenarios where you want file to persist

### Managing Links

```bash
# Check if file is a symlink
ls -l file.txt                         # Shows -> if symlink
file file.txt                          # Shows symbolic link info
readlink file.txt                      # Shows target of symlink
readlink -f file.txt                   # Follow all symlinks to final target

# Find broken symlinks
find . -type l ! -exec test -e {} \; -print

# Remove symlink (doesn't affect target)
rm symlink_name                        # Safe - only removes link
unlink symlink_name                    # Alternative command

# Update symlink
ln -sf new_target existing_link        # Force update

# List all symlinks
find . -type l -ls

# List symlinks in current directory
ls -l | grep ^l
```

## Archiving and Compression

Essential for managing datasets, model files, and backups.

### tar - Tape Archive

Combine multiple files into a single archive.

**Create Archives**:
```bash
tar -cvf archive.tar files/            # Create tar archive
tar -czvf archive.tar.gz files/        # Create compressed tar (gzip)
tar -cjvf archive.tar.bz2 files/       # Create compressed tar (bzip2)
tar -cJvf archive.tar.xz files/        # Create compressed tar (xz - best compression)

# Options:
# c - create
# x - extract
# v - verbose
# f - file
# z - gzip compression
# j - bzip2 compression
# J - xz compression
```

**Extract Archives**:
```bash
tar -xvf archive.tar                   # Extract tar
tar -xzvf archive.tar.gz               # Extract gzip compressed tar
tar -xjvf archive.tar.bz2              # Extract bzip2 compressed tar
tar -xvf archive.tar -C /target/dir    # Extract to specific directory

# Extract single file
tar -xzvf archive.tar.gz path/to/file.txt
```

**List Contents**:
```bash
tar -tvf archive.tar                   # List contents without extracting
tar -tzvf archive.tar.gz               # List compressed archive
tar -tzvf archive.tar.gz | grep model  # Find specific files
```

**AI Infrastructure Examples**:
```bash
# Backup model checkpoints
tar -czvf model_checkpoints_$(date +%Y%m%d).tar.gz checkpoints/

# Archive completed experiment
tar -czvf experiment_resnet50_baseline.tar.gz experiments/resnet50/

# Compress large dataset
tar -cJvf imagenet_subset.tar.xz data/imagenet_subset/

# Extract pretrained weights
tar -xzvf pretrained_weights.tar.gz -C models/pretrained/

# Backup configuration and code (excluding large files)
tar -czvf project_backup_$(date +%Y%m%d).tar.gz \
    --exclude='*.h5' \
    --exclude='*.pt' \
    --exclude='__pycache__' \
    --exclude='.git' \
    ml-project/

# Verify archive integrity
tar -tzvf archive.tar.gz > /dev/null && echo "Archive OK" || echo "Archive corrupted"

# Create split archives for large datasets
tar -czvf - large_dataset/ | split -b 1G - dataset.tar.gz.
```

### gzip/gunzip - Compression

Compress individual files.

```bash
gzip file.txt                          # Compresses to file.txt.gz (replaces original)
gzip -k file.txt                       # Keep original file
gzip -9 file.txt                       # Maximum compression (1-9 scale)
gunzip file.txt.gz                     # Decompress
gzip -d file.txt.gz                    # Also decompresses

# View compressed files without extracting
zcat file.txt.gz                       # View contents
zless file.txt.gz                      # Page through contents
zgrep "pattern" file.txt.gz            # Search compressed file

# Compress multiple files
gzip -r directory/                     # Recursive compression

# Check compression ratio
gzip -l file.txt.gz
```

### zip/unzip - Cross-Platform Archives

```bash
zip archive.zip file1.txt file2.txt    # Create zip archive
zip -r archive.zip directory/          # Recursive
zip -9 archive.zip files/              # Maximum compression
unzip archive.zip                      # Extract
unzip -l archive.zip                   # List contents
unzip archive.zip -d /target/dir       # Extract to directory

# AI Infrastructure use
zip -r model_package.zip models/ config.yaml requirements.txt
unzip -q pretrained_model.zip          # Quiet extraction

# Password protected
zip -e -r secure.zip sensitive_data/
unzip secure.zip  # Will prompt for password
```

### Compression Comparison

```bash
# Original file: 1GB model
# gzip (.gz):  ~300MB, fast compression/decompression
# bzip2 (.bz2): ~250MB, slower but better compression
# xz (.xz):    ~200MB, slowest but best compression
# zip:         ~300MB, cross-platform compatible

# Choose based on priority:
# Speed: gzip (.tar.gz)
# Compression ratio: xz (.tar.xz)
# Compatibility: zip
# Balance: bzip2 (.tar.bz2)
```

**Practical Workflow**:
```bash
# Daily backups (speed priority)
tar -czvf backup_$(date +%Y%m%d).tar.gz important_data/

# Long-term archival (compression priority)
tar -cJvf archive_$(date +%Y%m).tar.xz completed_projects/

# Sharing with Windows users
zip -r project_share.zip project/

# Large dataset distribution (split into chunks)
tar -czvf - dataset/ | split -b 1G - dataset.tar.gz.
# Creates dataset.tar.gz.aa, dataset.tar.gz.ab, etc.
# To reconstruct: cat dataset.tar.gz.* | tar -xzvf -
```

## Best Practices for AI Infrastructure

### 1. Organize Your Projects Consistently

```bash
# Standard ML project structure
ml-project/
├── data/
│   ├── raw/              # Original immutable data
│   ├── processed/        # Cleaned/transformed data
│   └── external/         # External datasets
├── models/
│   ├── checkpoints/      # Training checkpoints
│   ├── final/            # Production models
│   └── experiments/      # Experimental models
├── notebooks/            # Jupyter notebooks
├── src/                  # Source code
│   ├── data/            # Data processing
│   ├── models/          # Model definitions
│   ├── training/        # Training scripts
│   └── evaluation/      # Evaluation scripts
├── tests/               # Unit tests
├── logs/                # Training logs
├── configs/             # Configuration files
├── scripts/             # Utility scripts
├── docs/                # Documentation
├── requirements.txt     # Dependencies
├── README.md            # Project overview
└── .gitignore          # Git ignore rules
```

### 2. Use Descriptive Naming

```bash
# Good names
model_resnet50_imagenet_20231015.h5
experiment_baseline_lr0.001_batch32/
training_log_2023_10_15_14_30.log

# Poor names
model1.h5
exp_new/
log.txt
```

### 3. Version Control Your Data Locations

```bash
# Use symlinks for dataset versions
ln -s /data/imagenet/2023 ~/projects/classifier/data/imagenet

# Easy to update when new data arrives
rm ~/projects/classifier/data/imagenet
ln -s /data/imagenet/2024 ~/projects/classifier/data/imagenet
```

### 4. Automate Cleanup

```bash
# Remove old checkpoints (keep last 10)
ls -t checkpoints/*.ckpt | tail -n +11 | xargs rm

# Archive old logs monthly
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Automated cleanup script
cat > cleanup.sh << 'EOF'
#!/bin/bash
echo "Cleaning old checkpoints..."
find checkpoints/ -name "*.ckpt" -mtime +7 -delete
echo "Compressing old logs..."
find logs/ -name "*.log" -mtime +30 ! -name "*.gz" -exec gzip {} \;
echo "Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +
echo "Cleanup complete"
EOF
chmod +x cleanup.sh
```

### 5. Use Absolute Paths in Scripts

```bash
# Bad - depends on current directory
python train.py --data data/train

# Good - explicit and unambiguous
python /home/alice/ml-project/src/train.py \
    --data /home/alice/ml-project/data/train

# Better - use variables
PROJECT_ROOT="/home/alice/ml-project"
python $PROJECT_ROOT/src/train.py --data $PROJECT_ROOT/data/train

# Best - detect script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
python $PROJECT_ROOT/src/train.py --data $PROJECT_ROOT/data/train
```

### 6. Document File Operations

```bash
# Create README files in data directories
cat > data/imagenet/README.txt << EOF
ImageNet 2023 dataset
Downloaded: 2023-10-15
Source: http://www.image-net.org/
Preprocessing: Resized to 224x224, normalized to [-1,1]
Classes: 1000
Total images: 1,281,167 training, 50,000 validation
EOF

# Log model metadata
cat > models/model_v1_metadata.txt << EOF
Model: ResNet50
Training date: $(date)
Accuracy: 0.92
Dataset: ImageNet 2023
Hyperparameters:
  - Learning rate: 0.001
  - Batch size: 32
  - Epochs: 100
EOF
```

### 7. Check Before Destructive Operations

```bash
# Always verify before deletion
ls checkpoints/*.ckpt | wc -l        # Count files
ls checkpoints/*.ckpt | head -5      # Preview files
# Then delete
rm checkpoints/*.ckpt

# Use echo to preview
echo rm -rf experiments/failed_*     # Shows what would be deleted

# Create confirmation wrapper
safe_rm() {
    echo "About to delete:"
    ls -lh "$@"
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$@"
    fi
}
```

### 8. Handle Disk Space Proactively

```bash
# Check available space before large operations
df -h /data                          # Check disk space
du -sh data/                         # Check directory size
du -h --max-depth=1 /data | sort -h  # Find large directories

# Monitor while training
watch -n 60 'df -h /data && du -sh checkpoints/'

# Set up alerts
DISK_USAGE=$(df -h /data | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo "WARNING: Disk space above 90%!"
    # Send alert (email, Slack, etc.)
fi

# Find largest files
find /data -type f -size +1G -exec ls -lh {} \; | sort -k5 -h

# Disk usage report
du -h --max-depth=2 /data | sort -hr | head -20
```

## Summary and Key Takeaways

### Essential Commands Mastered

**Navigation**:
- `pwd` - Know where you are
- `cd` - Move between directories
- `ls` - List contents
- `tree` - Visual structure

**File Operations**:
- `touch` - Create files
- `mkdir -p` - Create directory hierarchies
- `cp -r` - Copy files/directories
- `mv` - Move/rename
- `rm -rf` - Delete (careful!)

**Viewing**:
- `cat` - Display files
- `less` - Page through files
- `head/tail` - View file ends
- `tail -f` - Follow logs

**Finding**:
- `find` - Powerful search
- `locate` - Fast database search
- `which` - Find commands
- `whereis` - Locate binaries

**Linking**:
- `ln -s` - Create symlinks
- `ln` - Create hard links

**Archiving**:
- `tar -czf` - Create compressed archives
- `tar -xzf` - Extract archives
- `gzip/gunzip` - Compression
- `zip/unzip` - Cross-platform

### Key Concepts

1. **Filesystem Hierarchy**: Single tree from `/`, logical organization
2. **Paths**: Absolute vs relative, special symbols (`.`, `..`, `~`, `-`)
3. **Everything is a File**: Devices, processes, sockets - all represented as files
4. **No Undo**: Most operations are permanent - verify before executing
5. **Case Sensitive**: `File.txt` ≠ `file.txt` ≠ `FILE.TXT`

### AI Infrastructure Applications

- Organize ML projects with consistent structure
- Navigate quickly between code, data, and models
- Find and manage large model files efficiently
- Archive experiments and datasets
- Monitor training through log files
- Automate cleanup and maintenance tasks

### Best Practices

✅ Use descriptive names for files and directories
✅ Organize projects with consistent structure
✅ Verify before destructive operations
✅ Use absolute paths in scripts
✅ Document your file organization
✅ Automate repetitive tasks
✅ Monitor disk space proactively
✅ Keep backups of important data

❌ Don't use `rm -rf` without verification
❌ Don't store important data in `/tmp`
❌ Don't use spaces in filenames (use underscores/hyphens)
❌ Don't work as root unless necessary
❌ Don't ignore disk space warnings

### Practice Exercises

1. Create a complete ML project structure
2. Use `find` to locate all Python files larger than 1MB
3. Archive and compress a directory, then extract it elsewhere
4. Create symlinks to organize multiple dataset versions
5. Write a script to clean old checkpoint files
6. Monitor a training log in real-time with `tail -f`
7. Find and delete all Python cache directories

### Next Steps

In **Lecture 03: Permissions and Security**, you'll learn:
- Understanding Linux permission model
- Managing users and groups
- Securing ML infrastructure
- Setting up multi-user environments
- Access control best practices

### Quick Reference Card

```bash
# Navigation
pwd                    # Print working directory
cd /path               # Change directory
ls -lah               # List all files with details
tree -L 2             # Show directory tree

# File operations
touch file.txt        # Create file
mkdir -p dir/subdir   # Create directories
cp -r src/ dst/       # Copy recursively
mv old new            # Move/rename
rm -i file            # Remove (interactive)

# Viewing
cat file.txt          # Display file
less file.txt         # Page through file
head -20 file.txt     # First 20 lines
tail -f log.txt       # Follow log file

# Finding
find . -name "*.py"   # Find by name
find . -size +1G      # Find by size
locate filename       # Fast database search
which command         # Find command location

# Archiving
tar -czvf arch.tar.gz dir/  # Create archive
tar -xzvf arch.tar.gz       # Extract archive
gzip file.txt               # Compress file
unzip archive.zip           # Extract zip
```

---

**End of Lecture 02**

Continue to **Lecture 03: Permissions and Security** to learn how to secure your Linux systems and manage multi-user environments for AI infrastructure.
