# Lecture 03: Process Management and Service Control

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Linux Processes](#understanding-linux-processes)
3. [Viewing Processes with ps](#viewing-processes-with-ps)
4. [Monitoring with top and htop](#monitoring-with-top-and-htop)
5. [Managing Processes](#managing-processes)
6. [Job Control](#job-control)
7. [Process Priorities and Nice Values](#process-priorities-and-nice-values)
8. [Service Management with systemd](#service-management-with-systemd)
9. [Resource Limits and Control Groups](#resource-limits-and-control-groups)
10. [Process Management for AI Workloads](#process-management-for-ai-workloads)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

As an AI Infrastructure Engineer, you'll manage compute-intensive workloads, GPU processes, training jobs, and inference services. Understanding process management is critical for optimizing resource usage, troubleshooting issues, and ensuring system stability.

This lecture covers Linux process fundamentals, monitoring tools, service management with systemd, and best practices for managing AI/ML workloads.

### Learning Objectives

By the end of this lecture, you will:
- Understand Linux process architecture and lifecycle
- Use `ps`, `top`, and `htop` to monitor processes
- Manage processes with signals (kill, SIGTERM, SIGKILL)
- Control foreground and background jobs
- Adjust process priorities with `nice` and `renice`
- Manage services using systemd and systemctl
- Monitor and limit resource usage
- Apply process management to ML training and inference

### Prerequisites
- Lecture 01: Linux Fundamentals
- Lecture 02: File Permissions
- Basic understanding of system resources (CPU, memory, disk)

### Why Process Management Matters for AI

**Resource Optimization**: ML training consumes massive CPU, GPU, and memory. Efficient process management prevents resource waste.

**Multi-Tenancy**: Share GPU servers among multiple users and experiments without conflicts.

**Reliability**: Automatically restart failed inference services, manage long-running training jobs.

**Performance**: Prioritize production workloads over experimental jobs.

**Cost Control**: Prevent runaway processes from consuming expensive cloud resources.

## Understanding Linux Processes

### What is a Process?

A **process** is a running instance of a program. Each process has:
- **PID** (Process ID): Unique identifier
- **PPID** (Parent Process ID): Process that created this one
- **UID/GID**: User and group ownership
- **State**: Running, sleeping, stopped, zombie
- **Memory**: Code, data, stack, heap
- **File Descriptors**: Open files, network connections
- **Environment**: Variables, working directory
- **Priority**: CPU scheduling priority

### Process Creation

In Linux, new processes are created through **forking**:

1. Parent process calls `fork()`
2. Kernel creates identical copy (child process)
3. Child gets new PID, same code/data as parent
4. Typically, child calls `exec()` to run different program

```bash
# Example: When you run a command in bash
$ ls -l
# Bash forks itself, creating a child process
# Child process calls exec() to replace itself with 'ls'
# Parent (bash) waits for child to complete
```

### Process Hierarchy

All processes descend from `init` (PID 1), forming a tree:

```
init (PID 1)
├── systemd services
├── login shells
│   └── bash (your session)
│       ├── python train.py
│       │   └── python subprocess (data loader)
│       └── nvidia-smi
└── sshd
    └── bash (remote session)
```

View process tree:
```bash
pstree                          # ASCII tree
pstree -p                       # With PIDs
pstree -u alice                 # User's processes
pstree -p 1234                  # From specific process
```

### Process States

**R - Running/Runnable**: Executing or ready to execute
**S - Sleeping (Interruptible)**: Waiting for event (I/O, timer)
**D - Disk Sleep (Uninterruptible)**: Waiting for disk I/O
**T - Stopped**: Suspended by signal (Ctrl+Z)
**Z - Zombie**: Terminated but parent hasn't read exit status
**I - Idle**: Kernel thread

```bash
# View process states
ps aux | awk '{print $8}' | sort | uniq -c
#  150 I     # Idle kernel threads
#   45 S     # Sleeping processes
#    3 R     # Running processes
#    1 Z     # Zombie (needs investigation!)
```

### Viewing Process Information

```bash
# Basic process info
ps                              # Current terminal processes
ps -u alice                     # User's processes
ps aux                          # All processes, detailed
ps -ef                          # All processes, full format

# Process details
cat /proc/1234/status           # Detailed process status
cat /proc/1234/cmdline          # Command line
cat /proc/1234/environ          # Environment variables
ls -l /proc/1234/fd/            # Open file descriptors
cat /proc/1234/maps             # Memory mappings
```

## Viewing Processes with ps

`ps` (process status) is the fundamental tool for viewing processes.

### Basic ps Usage

```bash
# Simple view (current terminal only)
ps
#   PID TTY          TIME CMD
#  1234 pts/0    00:00:00 bash
#  5678 pts/0    00:00:12 python

# All user's processes
ps -u alice
ps -u $(whoami)

# All processes (BSD style)
ps aux
# USER   PID %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
# alice 1234  0.0  0.1  21532  5432 pts/0 Ss   10:30   0:00 bash
# alice 5678 98.5 15.2 8234567 2456789 ? Sl  10:35  45:23 python train.py
```

### Column Meanings

**USER**: Process owner
**PID**: Process ID
**%CPU**: CPU usage percentage
**%MEM**: Memory usage percentage
**VSZ**: Virtual memory size (KB)
**RSS**: Resident set size (actual physical memory, KB)
**TTY**: Terminal (? = no terminal)
**STAT**: Process state
**START**: Start time
**TIME**: Cumulative CPU time
**COMMAND**: Command name/path

### Useful ps Patterns

**Sort by CPU usage**:
```bash
ps aux --sort=-%cpu | head -10
# Shows top 10 CPU-consuming processes
```

**Sort by memory usage**:
```bash
ps aux --sort=-%mem | head -10
# Shows top 10 memory-consuming processes
```

**Find specific process**:
```bash
ps aux | grep python
ps aux | grep train.py
ps aux | grep [p]ython          # Excludes grep itself from results
```

**Custom output format**:
```bash
ps -eo pid,ppid,cmd,%cpu,%mem --sort=-%cpu | head
# PID  PPID CMD                          %CPU %MEM
# 5678 1234 python train.py --gpu 0      98.5 15.2
```

**Process tree (hierarchy)**:
```bash
ps auxf                         # ASCII tree
ps -ejH                         # Alternative tree format
ps -e --forest                  # Forest view
```

### AI/ML Specific Queries

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

# TensorFlow processes
ps aux | grep tensorflow

# Show processes using most memory (for data loading issues)
ps aux --sort=-%mem | head -20

# Show processes using most CPU (for training monitoring)
ps aux --sort=-%cpu | head -20

# Find process by port (if running server)
sudo lsof -i :8080
```

## Monitoring with top and htop

Real-time process monitoring for interactive system observation.

### Using top

Interactive process viewer, updates every 3 seconds by default.

```bash
top
# Press 'h' for help, 'q' to quit
```

**Top Display Sections**:

1. **Summary** (first 5 lines):
```
top - 14:32:15 up 5 days,  2:15,  3 users,  load average: 4.52, 3.87, 2.91
Tasks: 312 total,   2 running, 310 sleeping,   0 stopped,   0 zombie
%Cpu(s): 45.2 us,  2.1 sy,  0.0 ni, 52.5 id,  0.1 wa,  0.0 hi,  0.1 si,  0.0 st
MiB Mem :  64234.5 total,   8234.2 free,  32156.8 used,  23843.5 buff/cache
MiB Swap:   8192.0 total,   8192.0 free,      0.0 used.  29876.3 avail Mem
```

**Load Average**: 1-min, 5-min, 15-min averages (4.52 = 4.52 processes waiting for CPU)
**CPU States**:
- `us`: user space (normal programs)
- `sy`: system/kernel
- `ni`: nice (low priority)
- `id`: idle
- `wa`: I/O wait
- `hi`: hardware interrupts
- `si`: software interrupts
- `st`: steal (virtual machines)

2. **Process List**:
```
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 5678 alice     20   0  8.0g    2.3g   45m S  398.2  15.2  45:23.45 python
 1234 alice     20   0  156m    12m   8.0m S    0.3   0.1   0:02.15 bash
```

### top Interactive Commands

```bash
# Sorting
P               # Sort by CPU usage
M               # Sort by memory usage
T               # Sort by running time
N               # Sort by PID

# Filtering
u               # Show specific user's processes
k               # Kill a process (enter PID)
r               # Renice a process (change priority)

# Display options
1               # Toggle individual CPU cores
c               # Toggle full command path
V               # Forest/tree view
i               # Hide idle processes
z               # Toggle color
d               # Change update interval

# Saving
W               # Write config to ~/.toprc
```

### Using htop

Enhanced, more user-friendly version of `top`.

**Installation**:
```bash
sudo apt install htop        # Ubuntu/Debian
sudo yum install htop        # RHEL/CentOS
```

**Advantages over top**:
- Color-coded display
- Mouse support
- Horizontal/vertical scrolling
- Visual CPU and memory meters
- Tree view by default
- Easier process killing and renicing

**htop Features**:
```bash
htop

# Function keys
F1 - Help
F2 - Setup (customize)
F3 - Search process
F4 - Filter processes
F5 - Tree view
F6 - Sort by column
F9 - Kill process
F10 - Quit

# Keyboard shortcuts
Space - Tag process
U - Untag all
/ - Search
\ - Filter
+ - Expand tree
- - Collapse tree
u - Show specific user
```

### Monitoring AI/ML Workloads

```bash
# Watch GPU processes (if nvidia-smi available)
watch -n 1 nvidia-smi

# Monitor specific training job
top -p $(pgrep -f train.py)

# Monitor Python processes
htop -p $(pgrep python | tr '\n' ',')

# Watch memory usage
watch -n 1 'ps aux --sort=-%mem | head -20'

# Monitor system during training
# Terminal 1: Training
python train.py

# Terminal 2: Monitoring
htop

# Terminal 3: GPU monitoring
watch -n 1 nvidia-smi
```

## Managing Processes

### Process Signals

Signals are software interrupts sent to processes. Common signals:

**SIGTERM (15)**: Polite termination request (default for `kill`)
**SIGKILL (9)**: Immediate termination (cannot be caught or ignored)
**SIGHUP (1)**: Hangup (reload configuration)
**SIGINT (2)**: Interrupt (Ctrl+C)
**SIGSTOP (19)**: Pause process
**SIGCONT (18)**: Resume process
**SIGUSR1 (10)**: User-defined signal 1
**SIGUSR2 (12)**: User-defined signal 2

```bash
# List all signals
kill -l
# 1) SIGHUP   2) SIGINT   3) SIGQUIT  4) SIGILL   5) SIGTRAP
# 6) SIGABRT  7) SIGBUS   8) SIGFPE   9) SIGKILL 10) SIGUSR1
# ...
```

### Using kill

Send signals to processes by PID.

```bash
# Graceful termination (allows cleanup)
kill 1234
kill -15 1234
kill -SIGTERM 1234              # All equivalent

# Force termination (immediate, no cleanup)
kill -9 1234
kill -SIGKILL 1234

# Reload configuration (common for services)
kill -HUP 1234
kill -1 1234

# Pause process
kill -STOP 1234

# Resume process
kill -CONT 1234
```

**Best Practice**: Always try `kill` (SIGTERM) first, use `kill -9` only if process doesn't respond.

### killall - Kill by Name

```bash
# Kill all processes with name
killall python
killall -9 python               # Force kill

# Kill specific user's processes
killall -u alice python

# Interactive mode
killall -i python               # Prompt for each process

# Wait for processes to die
killall -w python               # Wait until all killed
```

### pkill - Kill by Pattern

```bash
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
# 1234
# 5678

# Find with full command line
pgrep -f train.py
# 5678

# Get detailed info
pgrep -l python                 # With process name
# 1234 python
# 5678 python

pgrep -a python                 # With full command
# 1234 python -m jupyter notebook
# 5678 python train.py --epochs 100

# Use in scripts
TRAINING_PID=$(pgrep -f train.py)
if [ -n "$TRAINING_PID" ]; then
    echo "Training job running: $TRAINING_PID"
    kill $TRAINING_PID
fi
```

### Practical Examples

```bash
# Stop a runaway training job
pkill -f train_experiment_01.py

# Kill all Jupyter notebooks
killall jupyter-notebook

# Terminate user's processes (when user left processes running)
pkill -u bob

# Kill zombie processes (kill parent process)
ps aux | grep defunct
# Find PPID and kill parent
kill <PPID>

# Kill processes using specific GPU
# First find them
nvidia-smi
fuser -v /dev/nvidia0
# Then kill
kill <PID>

# Emergency: Kill all Python processes
killall -9 python
```

## Job Control

Manage foreground and background processes in the shell.

### Foreground vs Background

**Foreground**: Process controls the terminal, receives keyboard input
**Background**: Process runs independently, terminal available for other commands

### Running Jobs in Background

```bash
# Start in background with &
python train.py &
# [1] 5678                     # Job number and PID

# Check job status
jobs
# [1]+  Running                 python train.py &

# Long-running tasks in background
nohup python train.py > training.log 2>&1 &
# nohup: ignoring input and appending output to 'nohup.out'
# [1] 5678

# Even better: Redirect output explicitly
nohup python train.py > logs/training.log 2>&1 &
```

### Suspending and Resuming

```bash
# Start in foreground
python train.py

# Suspend with Ctrl+Z
^Z
# [1]+  Stopped                 python train.py

# Resume in background
bg
# [1]+ python train.py &

# Resume in foreground
fg
# python train.py

# Multiple jobs
python train1.py &
# [1] 1111
python train2.py &
# [2] 2222

jobs
# [1]-  Running                 python train1.py &
# [2]+  Running                 python train2.py &

# Resume specific job
fg %1                           # Bring job 1 to foreground
bg %2                           # Continue job 2 in background

# Kill specific job
kill %1                         # Kill job 1
```

### nohup - Immune to Hangups

Prevents process from terminating when terminal closes.

```bash
# Basic nohup
nohup python train.py &
# Output goes to nohup.out

# Redirect output
nohup python train.py > training.log 2>&1 &

# Check if still running after logout
ps aux | grep train.py

# Alternative: disown
python train.py &
disown                          # Detach from shell
# Now safe to logout
```

### screen and tmux

Terminal multiplexers for persistent sessions.

**screen**:
```bash
# Start screen session
screen -S training

# Run your process
python train.py

# Detach: Ctrl+A, then D
# Session continues running

# List sessions
screen -ls
# There is a screen on:
#     12345.training  (Detached)

# Reattach
screen -r training

# Kill session
screen -X -S training quit
```

**tmux** (more modern):
```bash
# Start tmux session
tmux new -s training

# Run process
python train.py

# Detach: Ctrl+B, then D

# List sessions
tmux ls
# training: 1 windows (created Wed Oct 15 14:30:00 2023)

# Reattach
tmux attach -t training

# Kill session
tmux kill-session -t training
```

**Why use screen/tmux for ML?**
- Run long training jobs without keeping terminal open
- Immune to network disconnections
- Multiple windows for monitoring (code, logs, GPU, system)
- Share sessions with team members

### Practical Workflow

```bash
# Start training session
tmux new -s experiment_42

# Window 1: Training
python train.py --config config.yaml

# Ctrl+B, C (create new window)
# Window 2: Monitoring
watch -n 1 nvidia-smi

# Ctrl+B, C
# Window 3: Logs
tail -f training.log

# Ctrl+B, D (detach)
# Close laptop, go home

# Next day: Reattach
tmux attach -t experiment_42
# Everything still running!
```

## Process Priorities and Nice Values

### Understanding Nice Values

**Nice** values control process priority (CPU scheduling).
- Range: -20 (highest priority) to +19 (lowest priority)
- Default: 0
- Lower nice value = higher priority = more CPU time
- Only root can set negative nice values

```bash
# View process nice values
ps -eo pid,ppid,ni,comm
#  PID  PPID  NI COMMAND
# 1234  1000   0 bash
# 5678  1234  10 python         # Lower priority
# 9012  1234 -10 python         # Higher priority (root set this)
```

### Starting with nice

```bash
# Start with lower priority (nice value +10)
nice -n 10 python train.py

# Start with higher priority (requires sudo for negative values)
sudo nice -n -10 python priority_job.py

# Maximum low priority (+19)
nice -n 19 python background_processing.py

# Check it worked
ps -eo pid,ni,comm | grep python
```

### Changing Priority with renice

```bash
# Lower priority of running process
renice +10 5678                 # Set nice value to 10 (PID 5678)
renice +10 -p 5678              # Same thing

# Increase priority (requires sudo)
sudo renice -10 5678            # Set nice value to -10

# Renice by user (all user's processes)
sudo renice +5 -u alice

# Renice by group
sudo renice +5 -g mlteam

# Renice multiple processes
renice +10 1234 5678 9012
```

### AI Infrastructure Use Cases

```bash
# Experimental training (low priority, don't interfere with production)
nice -n 15 python experimental_training.py &

# Production inference (high priority)
sudo nice -n -5 python production_inference.py &

# Data preprocessing (medium-low priority)
nice -n 10 python preprocess_dataset.py &

# Background model evaluation
nice -n 19 python evaluate_all_models.py > evaluation_results.txt &

# Adjust running training job if production workload arrives
TRAINING_PID=$(pgrep -f experimental_training.py)
renice +15 $TRAINING_PID         # Lower priority
```

### ionice - I/O Priority

Control disk I/O priority (separate from CPU nice).

```bash
# Check ionice classes
# 0 - None
# 1 - Real-time (requires root)
# 2 - Best-effort (default)
# 3 - Idle (only when no other I/O)

# Start with low I/O priority
ionice -c 3 python load_huge_dataset.py

# Set I/O priority for running process
ionice -c 2 -n 7 -p 5678
# Class 2 (best-effort), priority 7 (0-7 scale)

# Combine nice and ionice for data loading
nice -n 15 ionice -c 3 python data_pipeline.py &
```

## Service Management with systemd

Modern Linux systems use **systemd** as init system and service manager.

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

### systemctl - Service Control

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

```bash
# Create service file
sudo nano /etc/systemd/system/ml-inference.service
```

```ini
[Unit]
Description=ML Model Inference Service
After=network.target

[Service]
Type=simple
User=mlservice
Group=mlservice
WorkingDirectory=/opt/ml-inference
Environment="PATH=/opt/ml-inference/venv/bin"
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

**[Unit]** - General information
- `Description`: Service description
- `After`: Start after these units
- `Requires`: Hard dependencies
- `Wants`: Soft dependencies

**[Service]** - Service behavior
- `Type`: simple, forking, oneshot, notify
- `User/Group`: Run as specific user
- `WorkingDirectory`: Working directory
- `Environment`: Environment variables
- `ExecStart`: Command to start
- `ExecStop`: Command to stop
- `ExecReload`: Command to reload
- `Restart`: Restart policy (no, always, on-failure)
- `RestartSec`: Wait before restart

**[Install]** - Installation information
- `WantedBy`: Target to attach to

### Example: Training Job Scheduler

```ini
# /etc/systemd/system/ml-training@.service
[Unit]
Description=ML Training Job %i
After=network.target

[Service]
Type=oneshot
User=mluser
WorkingDirectory=/opt/ml-training
Environment="CUDA_VISIBLE_DEVICES=%i"
ExecStart=/opt/ml-training/venv/bin/python train.py --gpu %i --config /etc/ml-training/configs/%i.yaml
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
journalctl -u ml-inference --since "2023-10-15 14:00"
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

### Timers - Systemd Alternative to Cron

**Example: Daily Model Evaluation**

Create timer unit:
```ini
# /etc/systemd/system/ml-evaluation.timer
[Unit]
Description=Daily ML Model Evaluation

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Create service unit:
```ini
# /etc/systemd/system/ml-evaluation.service
[Unit]
Description=ML Model Evaluation

[Service]
Type=oneshot
User=mluser
ExecStart=/opt/ml-tools/evaluate_models.sh
StandardOutput=journal
```

**Activate**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable ml-evaluation.timer
sudo systemctl start ml-evaluation.timer

# Check timer status
systemctl list-timers
systemctl status ml-evaluation.timer
```

## Resource Limits and Control Groups

### ulimit - User Resource Limits

Prevent processes from consuming excessive resources.

```bash
# View current limits
ulimit -a
# core file size          (blocks, -c) 0
# data seg size           (kbytes, -d) unlimited
# scheduling priority             (-e) 0
# file size               (blocks, -f) unlimited
# pending signals                 (-i) 128394
# max locked memory       (kbytes, -l) 65536
# max memory size         (kbytes, -m) unlimited
# open files                      (-n) 1024
# pipe size            (512 bytes, -p) 8
# POSIX message queues     (bytes, -q) 819200
# real-time priority              (-r) 0
# stack size              (kbytes, -s) 8192
# cpu time               (seconds, -t) unlimited
# max user processes              (-u) 128394
# virtual memory          (kbytes, -v) unlimited
# file locks                      (-x) unlimited

# Set limits (current shell only)
ulimit -n 4096                  # Max open files
ulimit -u 500                   # Max user processes
ulimit -v 8388608               # Max virtual memory (8GB in KB)
```

**Permanent Limits** (`/etc/security/limits.conf`):
```bash
sudo nano /etc/security/limits.conf
```

```
# <domain>  <type>  <item>  <value>
alice       soft    nofile  4096
alice       hard    nofile  8192
@mlteam     soft    nproc   1000
@mlteam     hard    nproc   2000
*           soft    core    0
*           hard    memlock unlimited
```

**Apply immediately** (need to logout/login):
```bash
# Or use pam_limits
sudo pam-auth-update
```

### Control Groups (cgroups)

Linux kernel feature for resource isolation and limitation.

**View cgroup hierarchy**:
```bash
systemd-cgls
# ├─1 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
# ├─user.slice
# │ └─user-1000.slice
# │   ├─session-1.scope
# │   │ ├─1234 /bin/bash
# │   │ └─5678 python train.py
```

**Resource control in systemd units**:
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

**Apply limits to running services**:
```bash
# Temporarily limit service
sudo systemctl set-property ml-inference.service MemoryMax=8G
sudo systemctl set-property ml-inference.service CPUQuota=200%

# Make permanent (add to unit file)
sudo systemctl edit ml-inference.service
# Add in [Service] section
```

## Process Management for AI Workloads

### GPU Process Management

```bash
# List GPU processes
nvidia-smi

# Monitor GPU usage
watch -n 1 nvidia-smi

# Find processes using GPU
fuser -v /dev/nvidia0
lsof /dev/nvidia0

# Kill GPU process
nvidia-smi --query-compute-apps=pid --format=csv,noheader | xargs kill

# Set GPU for process
CUDA_VISIBLE_DEVICES=0 python train.py       # Use GPU 0
CUDA_VISIBLE_DEVICES=0,1 python train.py     # Use GPU 0,1
CUDA_VISIBLE_DEVICES="" python train.py      # Use CPU only
```

### Training Job Management Script

```bash
#!/bin/bash
# train-manager.sh - Manage ML training jobs

case "$1" in
    start)
        echo "Starting training job..."
        nohup nice -n 10 python train.py > logs/training_$(date +%Y%m%d_%H%M%S).log 2>&1 &
        echo $! > /tmp/training.pid
        echo "Training started (PID: $(cat /tmp/training.pid))"
        ;;
    stop)
        if [ -f /tmp/training.pid ]; then
            PID=$(cat /tmp/training.pid)
            echo "Stopping training (PID: $PID)..."
            kill $PID
            rm /tmp/training.pid
        else
            echo "No training job running"
        fi
        ;;
    status)
        if [ -f /tmp/training.pid ]; then
            PID=$(cat /tmp/training.pid)
            if ps -p $PID > /dev/null; then
                echo "Training running (PID: $PID)"
                ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd
            else
                echo "Training job crashed (stale PID file)"
                rm /tmp/training.pid
            fi
        else
            echo "No training job running"
        fi
        ;;
    logs)
        tail -f logs/training_*.log
        ;;
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        exit 1
        ;;
esac
```

### Multi-GPU Training Orchestration

```bash
#!/bin/bash
# multi-gpu-train.sh - Distribute training across GPUs

NUM_GPUS=4
for GPU in $(seq 0 $((NUM_GPUS-1))); do
    echo "Starting training on GPU $GPU"
    CUDA_VISIBLE_DEVICES=$GPU nohup python train.py \
        --gpu $GPU \
        --config configs/exp_gpu${GPU}.yaml \
        > logs/training_gpu${GPU}.log 2>&1 &
done

echo "Training started on $NUM_GPUS GPUs"
jobs -l
```

### Resource Monitoring During Training

```bash
#!/bin/bash
# monitor-training.sh - Monitor resources during training

INTERVAL=60  # seconds

while true; do
    echo "=== $(date) ===" >> monitoring.log

    # CPU and memory
    echo "--- System Resources ---" >> monitoring.log
    top -bn1 | head -5 >> monitoring.log

    # GPU
    echo "--- GPU Status ---" >> monitoring.log
    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total \
        --format=csv >> monitoring.log

    # Training process
    echo "--- Training Process ---" >> monitoring.log
    ps aux | grep [t]rain.py >> monitoring.log

    echo "" >> monitoring.log
    sleep $INTERVAL
done
```

## Summary and Key Takeaways

### Commands Mastered

**Process Viewing**:
- `ps aux` - View all processes
- `top` / `htop` - Interactive monitoring
- `pstree` - Process hierarchy
- `pgrep` - Find process IDs

**Process Management**:
- `kill` - Send signals to processes
- `killall` - Kill by name
- `pkill` - Kill by pattern
- `nice` - Start with priority
- `renice` - Change priority

**Job Control**:
- `&` - Run in background
- `Ctrl+Z` - Suspend
- `fg` / `bg` - Foreground/background
- `jobs` - List jobs
- `nohup` - Ignore hangups
- `screen` / `tmux` - Terminal multiplexers

**Service Management**:
- `systemctl` - Manage services
- `journalctl` - View logs

**Resource Limits**:
- `ulimit` - User limits
- `ionice` - I/O priority
- cgroups - Resource control

### Key Concepts

1. **Process Lifecycle**: Creation, running, termination, zombie states
2. **Signals**: Communication mechanism for process control
3. **Priorities**: Nice values control CPU scheduling
4. **Job Control**: Foreground, background, suspension
5. **Systemd**: Modern service management
6. **Resource Limits**: Prevent resource exhaustion

### AI/ML Best Practices

✅ Use `nice` for experimental workloads (lower priority)
✅ Use `screen`/`tmux` for long training jobs
✅ Monitor GPU processes with `nvidia-smi`
✅ Create systemd services for production inference
✅ Set resource limits to prevent OOM
✅ Log training output with timestamps
✅ Use `nohup` for remote training jobs
✅ Monitor resource usage during training

### Common Patterns

```bash
# Start low-priority training
nice -n 15 nohup python train.py > training.log 2>&1 &

# Monitor training
tail -f training.log & watch -n 1 nvidia-smi

# Kill stuck process
pkill -9 -f train.py

# Production inference service
sudo systemctl start ml-inference
journalctl -u ml-inference -f

# Multi-GPU distribution
for gpu in 0 1 2 3; do
    CUDA_VISIBLE_DEVICES=$gpu python train.py --gpu $gpu &
done
```

### Troubleshooting

**High CPU usage**:
```bash
top -o %CPU
# Identify process, check if expected, adjust nice value if needed
```

**Memory exhaustion**:
```bash
ps aux --sort=-%mem | head
free -h
# Check OOM killer logs: dmesg | grep -i oom
```

**Zombie processes**:
```bash
ps aux | grep defunct
# Find parent, kill parent (zombie will be cleaned up)
```

**Service won't start**:
```bash
systemctl status service-name
journalctl -u service-name -n 100
# Check permissions, dependencies, configuration
```

### Next Steps

In **Lecture 04: Shell Scripting**, you'll learn:
- Bash scripting fundamentals
- Variables, loops, and conditionals
- Automating infrastructure tasks
- Error handling and debugging
- Building deployment scripts

### Quick Reference

```bash
# Process viewing
ps aux                      # All processes
ps aux --sort=-%cpu         # By CPU
ps aux --sort=-%mem         # By memory
top                         # Interactive monitor
htop                        # Better interactive monitor

# Process control
kill PID                    # Graceful termination
kill -9 PID                 # Force termination
pkill -f pattern            # Kill by pattern
nice -n 10 command          # Start with low priority
renice +10 PID              # Change priority

# Job control
command &                   # Run in background
Ctrl+Z, bg                  # Suspend and background
fg %1                       # Bring job 1 to foreground
nohup command &             # Immune to hangups
tmux                        # Terminal multiplexer

# Services
systemctl status service    # Service status
systemctl start service     # Start service
journalctl -u service -f    # Follow logs

# GPU
nvidia-smi                  # GPU status
watch -n 1 nvidia-smi       # Monitor GPU
CUDA_VISIBLE_DEVICES=0 cmd  # Use specific GPU
```

---

**End of Lecture 03**

Continue to **Lecture 04: Shell Scripting** to learn how to automate process management and infrastructure tasks.
