# Lecture 01: Introduction to Linux and Command Line

## Table of Contents
1. [Introduction](#introduction)
2. [History and Philosophy of Linux](#history-and-philosophy-of-linux)
3. [Linux Distributions](#linux-distributions)
4. [Terminal Emulators and Shells](#terminal-emulators-and-shells)
5. [Basic Command Structure](#basic-command-structure)
6. [Getting Help and Documentation](#getting-help-and-documentation)
7. [Environment Variables](#environment-variables)
8. [Best Practices for AI Infrastructure](#best-practices-for-ai-infrastructure)
9. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

As an AI Infrastructure Engineer, Linux is your foundation. Whether deploying machine learning models, managing GPU servers, or orchestrating containers, Linux powers over 90% of cloud infrastructure and is the standard for AI/ML workloads.

This lecture introduces you to Linux, its philosophy, the command-line environment, and essential concepts that will prepare you for deeper technical work ahead.

### Learning Objectives

By the end of this lecture, you will:
- Understand the history and philosophy of Linux
- Navigate the Linux distribution landscape
- Use terminal emulators and understand different shells
- Construct and execute basic Linux commands
- Access help and documentation systems
- Work with environment variables
- Apply Linux fundamentals to AI infrastructure scenarios

### Prerequisites
- Access to a Linux system (Ubuntu 22.04 LTS, CentOS 8, or similar)
- Basic computer literacy
- Willingness to learn command-line interfaces

### Why Linux for AI Infrastructure?

**Industry Standard**: Over 90% of cloud infrastructure runs on Linux. Major AI platforms like TensorFlow, PyTorch, and CUDA are optimized for Linux environments.

**Performance**: Linux provides direct hardware access, critical for GPU computing and high-performance ML workloads.

**Automation**: Shell scripting and command-line tools enable infrastructure automation at scale.

**Open Source**: Free, customizable, and supported by extensive community resources.

**Container Native**: Docker, Kubernetes, and modern orchestration tools are built for Linux.

## History and Philosophy of Linux

### The Birth of Unix (1969)

The story begins at Bell Labs with **Unix**, created by Ken Thompson and Dennis Ritchie. Unix introduced revolutionary concepts:
- Hierarchical file system
- Everything is a file
- Small, composable programs
- Pipes for connecting programs
- Portable across hardware

**Unix Philosophy**: "Do one thing and do it well"

### The GNU Project (1983)

Richard Stallman launched the **GNU Project** (GNU's Not Unix) to create a free Unix-like operating system:
- Free Software Foundation
- GNU tools (bash, gcc, make, etc.)
- GPL (General Public License)
- **Freedom**: Use, study, modify, distribute software

### Linux Kernel (1991)

Linus Torvalds, a Finnish computer science student, created the **Linux kernel**:
```
Date: August 25, 1991
From: torvalds@klaava.Helsinki.FI (Linus Benedict Torvalds)
Subject: What would you like to see most in minix?

Hello everybody out there using minix -

I'm doing a (free) operating system (just a hobby, won't be big and
professional like gnu) for 386(486) AT clones. This has been brewing
since april, and is starting to get ready.
```

**Key Innovations**:
- Open source from day one
- Monolithic kernel architecture
- Community-driven development
- Rapid iteration and improvement

### GNU/Linux Combination

**GNU + Linux Kernel = Complete Operating System**
- GNU provided user-space tools
- Linux provided the kernel
- Combined: A free, powerful, Unix-like OS

### Linux Today

**Statistics (2024)**:
- 100% of supercomputers run Linux
- 96.3% of top million web servers run Linux
- 85% of smartphones (Android) use Linux kernel
- Major cloud providers (AWS, Azure, GCP) primarily Linux
- NASA, CERN, SpaceX use Linux

## Linux Distributions

A **Linux distribution** (distro) packages the Linux kernel with software, tools, package managers, and configurations.

### Major Distribution Families

#### 1. Debian Family
**Debian**: Stable, community-driven, massive package repository
- **Ubuntu**: Most popular, user-friendly, strong community
  - **Ubuntu Server**: For servers and cloud
  - **Ubuntu LTS**: Long-term support (5 years)
- **Linux Mint**: Desktop-focused, beginner-friendly

**Package Manager**: `apt`, `dpkg`
**AI/ML Use**: Very common, excellent NVIDIA/CUDA support

#### 2. Red Hat Family
**Red Hat Enterprise Linux (RHEL)**: Enterprise, commercial support
- **CentOS**: Free RHEL clone (being replaced by Rocky/Alma)
- **Fedora**: Cutting-edge, Red Hat sponsored
- **Rocky Linux**: CentOS replacement
- **AlmaLinux**: Another CentOS replacement

**Package Manager**: `yum`, `dnf`, `rpm`
**AI/ML Use**: Common in enterprise environments

#### 3. SUSE Family
**SUSE Linux Enterprise**: Enterprise Linux, popular in Europe
- **openSUSE**: Community version

**Package Manager**: `zypper`
**AI/ML Use**: Less common but supported

#### 4. Arch Family
**Arch Linux**: Rolling release, cutting-edge, DIY
- **Manjaro**: User-friendly Arch derivative

**Package Manager**: `pacman`
**AI/ML Use**: Developer workstations, less common for production

### Choosing a Distribution for AI Infrastructure

**For Learning** (Recommended for this course):
- **Ubuntu 22.04 LTS**: Best documentation, community support
- **Ubuntu 20.04 LTS**: Still widely used, very stable

**For Production**:
- **Ubuntu Server LTS**: Cloud, GPU servers, ML platforms
- **RHEL/Rocky/Alma**: Enterprise, regulated industries
- **Amazon Linux 2**: AWS-optimized

**Key Factors**:
- LTS (Long Term Support) for stability
- Hardware support (NVIDIA drivers, CUDA)
- Package availability (ML frameworks)
- Community size and documentation
- Enterprise support needs

## Terminal Emulators and Shells

### What is a Terminal?

A **terminal** is your interface to the command-line environment.

**Historical Context**:
- Originally: Physical hardware terminals (VT100, etc.)
- Modern: Software emulators running in graphical environments

### Common Terminal Emulators

**Linux Desktop**:
- **GNOME Terminal** (Ubuntu default)
- **Konsole** (KDE)
- **Terminator**: Split panes, advanced features
- **Alacritty**: GPU-accelerated, fast
- **Kitty**: GPU-based, modern

**Remote Access**:
- **SSH clients**: PuTTY (Windows), iTerm2 (macOS), built-in ssh

**Professional Tools**:
- **tmux**: Terminal multiplexer (split panes, persistence)
- **screen**: Older multiplexer, still widely used

### Understanding Shells

A **shell** is the command interpreter between you and the kernel.

#### Common Shells

**Bash (Bourne Again Shell)**:
- Default on most Linux systems
- Rich scripting capabilities
- Extensive documentation
- **Most common for AI infrastructure automation**

```bash
# Check your current shell
echo $SHELL
# /bin/bash

# Bash version
bash --version
# GNU bash, version 5.1.16
```

**Zsh (Z Shell)**:
- Advanced features, plugins
- Oh-My-Zsh framework
- Better auto-completion
- Popular among developers

```bash
# Install zsh
sudo apt install zsh

# Change default shell
chsh -s $(which zsh)
```

**Fish (Friendly Interactive Shell)**:
- User-friendly, syntax highlighting
- Auto-suggestions
- Different syntax from bash

**Sh (Bourne Shell)**:
- Original Unix shell
- POSIX-compliant, portable
- Used for system scripts

#### Shell Comparison

| Feature | Bash | Zsh | Fish | Sh |
|---------|------|-----|------|-----|
| Portability | High | Medium | Low | Very High |
| Scripting | Excellent | Excellent | Different | Basic |
| Interactive | Good | Excellent | Excellent | Basic |
| Compatibility | Standard | Bash-like | Unique | POSIX |
| AI/ML Scripts | ✓✓✓ | ✓✓ | ✓ | ✓✓ |

**Recommendation**: Learn Bash first. It's universal, standard for system administration and automation.

## Basic Command Structure

### Command Anatomy

```
command [options] [arguments]
   │        │           │
   │        │           └─ What to act on
   │        └─ How to modify behavior
   └─ What action to perform
```

**Examples**:
```bash
ls                      # Command only
ls -l                   # Command + option
ls -l /home            # Command + option + argument
ls -la /home/alice     # Command + multiple options + argument
```

### Options (Flags)

**Short Options** (single hyphen):
```bash
ls -l                   # Long format
ls -a                   # Show all (including hidden)
ls -h                   # Human-readable sizes
ls -lah                 # Combine multiple options
```

**Long Options** (double hyphen):
```bash
ls --all                # Same as -a
ls --human-readable     # Same as -h
ls --help               # Show help
```

### Arguments

Arguments specify what the command acts on:
```bash
cat file.txt            # Display file.txt
mkdir new_directory     # Create new_directory
cp source.txt dest.txt  # Copy source to dest
```

### Common Command Patterns

**List files**:
```bash
ls                      # Current directory
ls /var/log            # Specific directory
ls *.py                # Pattern matching (all Python files)
```

**Navigate**:
```bash
pwd                     # Print working directory
cd /home/alice         # Change to absolute path
cd documents           # Change to relative path
cd ..                  # Up one level
cd ~                   # Home directory
cd -                   # Previous directory
```

**File viewing**:
```bash
cat file.txt           # Display entire file
head file.txt          # First 10 lines
tail file.txt          # Last 10 lines
tail -f logfile.log    # Follow file (real-time updates)
less large_file.txt    # Page through file
```

**System information**:
```bash
whoami                 # Current username
hostname               # Computer name
uname -a               # System information
date                   # Current date/time
uptime                 # System uptime
```

### Special Characters

**Wildcards**:
```bash
*                      # Match any characters
?                      # Match single character
[abc]                  # Match a, b, or c
[0-9]                  # Match any digit

# Examples
ls *.py                # All Python files
ls file?.txt           # file1.txt, fileA.txt, etc.
ls [a-z]*.log          # Logs starting with lowercase letter
```

**Redirection**:
```bash
>                      # Redirect output to file (overwrite)
>>                     # Redirect output to file (append)
<                      # Redirect input from file
2>                     # Redirect stderr
&>                     # Redirect stdout and stderr

# Examples
echo "Hello" > file.txt        # Write to file
echo "World" >> file.txt       # Append to file
python train.py > output.log   # Save output
python train.py 2> error.log   # Save errors only
python train.py &> all.log     # Save everything
```

**Pipes**:
```bash
|                      # Send output to next command

# Examples
ls -l | grep ".py"     # List then filter
cat file.txt | wc -l   # Count lines
ps aux | grep python   # Find Python processes
```

**Background and Control**:
```bash
&                      # Run in background
Ctrl+C                 # Terminate current process
Ctrl+Z                 # Suspend current process
Ctrl+D                 # End input / logout
Ctrl+L                 # Clear screen
```

## Getting Help and Documentation

### Man Pages (Manual)

The primary documentation system in Linux:

```bash
# View manual for a command
man ls
man grep
man python

# Search man pages
man -k "network"       # Search by keyword
apropos "copy"         # Same as man -k

# Man page sections
man 1 passwd           # User commands
man 5 passwd           # File formats
```

**Man Page Navigation**:
- **Space**: Next page
- **b**: Previous page
- **/pattern**: Search forward
- **?pattern**: Search backward
- **n**: Next search result
- **q**: Quit

**Man Page Structure**:
```
NAME        - Command name and brief description
SYNOPSIS    - Usage syntax
DESCRIPTION - Detailed explanation
OPTIONS     - Available flags and options
EXAMPLES    - Usage examples
SEE ALSO    - Related commands
```

### Help Options

Most commands have built-in help:

```bash
# Short help
ls --help
grep --help
python --help

# Often shows:
# - Usage syntax
# - Common options
# - Quick examples
```

### Info Pages

More detailed than man pages:
```bash
info ls
info bash
info coreutils
```

### Command-Specific Documentation

```bash
# Python help
python -m pydoc os

# Git help
git help commit

# Systemctl help
systemctl --help
```

### Online Resources

**Official Documentation**:
- Ubuntu Documentation: https://help.ubuntu.com
- RHEL Documentation: https://access.redhat.com
- Arch Wiki: https://wiki.archlinux.org (excellent even for other distros)

**Command Examples**:
- **tldr**: Simplified man pages with examples
  ```bash
  sudo apt install tldr
  tldr tar
  tldr find
  ```

- **cheat**: Community-driven cheat sheets
  ```bash
  pip install cheat
  cheat grep
  ```

- **explainshell.com**: Web-based command explainer

**AI Infrastructure Specific**:
- NVIDIA CUDA Documentation
- Docker Documentation
- Kubernetes Documentation
- TensorFlow/PyTorch Installation Guides

## Environment Variables

Environment variables store system configuration and paths.

### Viewing Environment Variables

```bash
# View all environment variables
env
printenv

# View specific variable
echo $HOME
echo $USER
echo $PATH
printenv PATH
```

### Common Environment Variables

**System Variables**:
```bash
$HOME                  # User's home directory
$USER                  # Current username
$SHELL                 # Current shell
$PWD                   # Present working directory
$OLDPWD               # Previous directory
$HOSTNAME             # Computer name
$LANG                 # Language/locale
```

**$PATH - Command Search Path**:
```bash
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/usr/games

# How Linux finds commands:
which python
# Searches each directory in $PATH until found
```

**AI/ML Specific Variables**:
```bash
# CUDA (GPU computing)
$CUDA_VISIBLE_DEVICES  # Which GPUs to use
$CUDA_HOME             # CUDA installation path

# Python
$PYTHONPATH            # Python module search path
$VIRTUAL_ENV           # Active virtual environment

# TensorFlow
$TF_CPP_MIN_LOG_LEVEL # TensorFlow logging level
```

### Setting Environment Variables

**Temporary** (current session only):
```bash
# Set variable
export MODEL_PATH="/models/production"
export CUDA_VISIBLE_DEVICES=0

# Use variable
echo $MODEL_PATH
python train.py  # Can access CUDA_VISIBLE_DEVICES
```

**Persistent** (across sessions):
```bash
# Add to ~/.bashrc (user-specific)
echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.bashrc
source ~/.bashrc

# Add to /etc/environment (system-wide)
sudo sh -c 'echo "MODEL_DIR=/opt/models" >> /etc/environment'
```

### Practical AI Examples

**GPU Selection**:
```bash
# Use GPU 0 only
export CUDA_VISIBLE_DEVICES=0
python train.py

# Use GPUs 2 and 3
export CUDA_VISIBLE_DEVICES=2,3
python multi_gpu_train.py

# Use CPU only (no GPU)
export CUDA_VISIBLE_DEVICES=""
python cpu_train.py
```

**Python Path Management**:
```bash
# Add custom module directory
export PYTHONPATH="/opt/ml-project/src:$PYTHONPATH"
python -c "import custom_module"
```

**Model Configuration**:
```bash
# Set model path for application
export MODEL_PATH="/models/resnet50/model.h5"
export CONFIG_PATH="/config/production.yaml"
python serve.py  # Reads these variables
```

## Best Practices for AI Infrastructure

### 1. Use Absolute Paths in Production

```bash
# Bad: Relies on current directory
python train.py --data data/train

# Good: Explicit and unambiguous
python /opt/ml/train.py --data /data/ml/train
```

### 2. Set Up Environment Properly

```bash
# Create a setup script for consistency
cat > ~/setup-ml-env.sh << 'EOF'
#!/bin/bash
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
export PYTHONPATH=/opt/ml-project/src:$PYTHONPATH
EOF

# Source before working
source ~/setup-ml-env.sh
```

### 3. Document Your Environment

```bash
# Save environment for reproducibility
env | grep -E "(CUDA|PYTHON|MODEL)" > environment.txt

# Save system information
uname -a > system_info.txt
lsb_release -a >> system_info.txt
python --version >> system_info.txt
nvidia-smi >> system_info.txt
```

### 4. Use Version Control for Scripts

```bash
# Track your automation scripts
mkdir -p ~/ml-scripts
cd ~/ml-scripts
git init
git add setup-env.sh deploy-model.sh
git commit -m "Initial automation scripts"
```

### 5. Leverage Tab Completion

```bash
# Press TAB to auto-complete
cd /var/lo<TAB>        # Completes to /var/log/
python train<TAB>      # Shows train.py, train_v2.py, etc.

# Double TAB to show options
ls --<TAB><TAB>        # Shows all --options
```

## Summary and Key Takeaways

### Essential Concepts

**Linux Foundation**:
- Born from Unix philosophy: simple, composable tools
- Open source, community-driven
- Industry standard for AI/ML infrastructure

**Distributions**:
- Choose Ubuntu or RHEL family for production
- LTS versions for stability
- Package managers vary by family

**Command Line**:
- Terminal + Shell = Your interface
- Bash is standard for scripting and automation
- Commands follow: `command [options] [arguments]`

**Getting Help**:
- `man command` for documentation
- `command --help` for quick reference
- Online resources (Arch Wiki, tldr, etc.)

**Environment Variables**:
- Configure system and applications
- `$PATH`, `$HOME`, `$USER` are essential
- AI-specific: `$CUDA_VISIBLE_DEVICES`, `$PYTHONPATH`

### Commands Introduced

```bash
# Basic navigation
pwd                    # Print working directory
cd                     # Change directory
ls                     # List files

# System information
whoami                 # Current user
hostname               # Computer name
uname -a               # System details

# Getting help
man command            # Manual pages
command --help         # Quick help
info command           # Detailed info

# Environment
env                    # View all variables
echo $VARIABLE         # View specific variable
export VAR=value       # Set variable
```

### Best Practices

✅ Learn Bash - it's universal
✅ Use man pages and help options
✅ Leverage tab completion
✅ Set up environment consistently
✅ Document your configuration
✅ Use absolute paths in production
✅ Version control your scripts
✅ Understand your distribution's package manager

### AI Infrastructure Applications

- Remote server management via SSH
- GPU environment configuration
- Python path and dependency management
- Model deployment automation
- System monitoring and logging
- Distributed training orchestration

### Next Steps

In **Lecture 02: File System and Navigation**, you'll learn:
- Linux filesystem hierarchy
- Advanced navigation techniques
- File operations and management
- Finding files quickly
- Working with archives
- Organizing ML projects

### Practice Exercises

1. Explore your Linux system:
   ```bash
   uname -a
   lsb_release -a
   echo $SHELL
   echo $PATH
   ```

2. Practice basic commands:
   ```bash
   pwd
   cd /tmp
   ls -la
   whoami
   hostname
   ```

3. Read documentation:
   ```bash
   man ls
   man bash
   ls --help
   ```

4. Set up environment:
   ```bash
   export TEST_VAR="Hello Linux"
   echo $TEST_VAR
   ```

5. Explore your system:
   ```bash
   which python
   which bash
   echo $HOME
   cd ~
   pwd
   ```

### Quick Reference Card

```bash
# Navigation
pwd                    # Where am I?
cd <directory>         # Go to directory
ls                     # List files

# Help
man <command>          # Full manual
<command> --help       # Quick help

# Environment
echo $VAR              # Show variable
export VAR=value       # Set variable
env                    # Show all variables

# System info
whoami                 # Current user
hostname               # Computer name
uname -a               # System details
date                   # Current date/time
```

---

**End of Lecture 01**

Continue to **Lecture 02: File System and Navigation** to learn the Linux filesystem structure and essential file operations for AI infrastructure work.
