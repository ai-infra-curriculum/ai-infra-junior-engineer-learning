# Exercise 03: Process Management for ML Training Jobs

## Overview

This exercise teaches you how to manage Linux processes in the context of ML infrastructure. You'll learn to monitor training jobs, control GPU processes, manage system services, and handle long-running ML workloads. These skills are essential for running efficient, reliable ML infrastructure.

## Learning Objectives

By completing this exercise, you will:
- Monitor running processes with ps, top, and htop
- Manage process lifecycle (start, stop, pause, resume, kill)
- Use job control for background and foreground processes
- Monitor GPU processes with nvidia-smi
- Manage system services with systemctl
- Handle stuck or runaway ML training processes
- Implement resource monitoring for ML workloads
- Use screen and tmux for persistent training sessions

## Prerequisites

- Completed Exercises 01-02
- Completed Lecture 04: System Administration Basics
- Access to a Linux system
- Basic Python knowledge (for ML training examples)
- Optional: NVIDIA GPU for GPU monitoring sections
- At least 2GB RAM and 2 CPU cores

## Time Required

- Estimated: 75-90 minutes
- Difficulty: Intermediate

## Part 1: Understanding Processes

### Step 1: Exploring Running Processes

```bash
# Create workspace
mkdir -p ~/ml-process-management
cd ~/ml-process-management

# View your current processes
ps
# Shows: PID TTY TIME CMD

# View all processes for current user
ps -u $(whoami)

# View all processes on system
ps aux
# a = all users, u = user-oriented format, x = include processes without TTY

# View process tree (hierarchical)
ps auxf
# or
pstree

# View detailed process information
ps -ef
# -e = all processes, -f = full format

# Find specific processes
ps aux | grep python
ps aux | grep bash

# Save process snapshot for analysis
ps aux > process_snapshot.txt
head -20 process_snapshot.txt
```

**Analysis Tasks**:

1. Identify the process with highest CPU usage:
   ```bash
   ps aux --sort=-%cpu | head -10
   ```

2. Identify the process with highest memory usage:
   ```bash
   ps aux --sort=-%mem | head -10
   ```

3. Count total running processes:
   ```bash
   ps aux | wc -l
   ```

4. Find all Python processes:
   ```bash
   ps aux | grep python | grep -v grep
   ```

**Understanding ps Output**:
```bash
cat > ps_reference.txt << 'EOF'
PS OUTPUT COLUMNS
=================

USER    = User who owns the process
PID     = Process ID (unique identifier)
%CPU    = CPU usage percentage
%MEM    = Memory usage percentage
VSZ     = Virtual memory size (KB)
RSS     = Resident set size - physical memory (KB)
TTY     = Terminal type (? = no terminal)
STAT    = Process state
START   = Start time
TIME    = CPU time consumed
COMMAND = Command with arguments

PROCESS STATES (STAT):
R = Running
S = Sleeping (waiting for event)
D = Uninterruptible sleep (usually I/O)
T = Stopped
Z = Zombie (terminated but not reaped)
< = High priority
N = Low priority
L = Has pages locked in memory
s = Session leader
+ = Foreground process group

Examples:
Ss  = Sleeping session leader
R+  = Running in foreground
S<  = Sleeping with high priority
EOF

cat ps_reference.txt
```

### Step 2: Real-Time Process Monitoring

```bash
# Use top for real-time monitoring
# (Run in separate terminal, press 'q' to quit)
echo "Run: top"
echo "Interactive commands in top:"
echo "  P = Sort by CPU"
echo "  M = Sort by memory"
echo "  k = Kill process"
echo "  r = Renice (change priority)"
echo "  h = Help"
echo "  q = Quit"

# Create a top reference
cat > top_reference.txt << 'EOF'
TOP COMMAND REFERENCE
=====================

Starting top:
-------------
top              Normal mode
top -u username  Show specific user
top -p PID       Monitor specific PID
top -d 2         Update every 2 seconds
top -b -n 1      Batch mode, 1 iteration (for scripts)

Interactive Commands:
--------------------
P    Sort by CPU usage
M    Sort by memory usage
T    Sort by time
k    Kill a process (prompts for PID)
r    Renice (change priority)
u    Filter by user
c    Toggle command line display
V    Tree view
1    Toggle individual CPU cores
h    Help
q    Quit

Understanding Display:
---------------------
Top section (system overview):
  - Uptime, users, load average
  - Tasks (running, sleeping, stopped, zombie)
  - CPU usage (us=user, sy=system, ni=nice, id=idle, wa=I/O wait)
  - Memory and swap usage

Process section:
  - PID: Process ID
  - USER: Owner
  - PR: Priority
  - NI: Nice value
  - VIRT: Virtual memory
  - RES: Resident memory
  - SHR: Shared memory
  - S: Status
  - %CPU: CPU usage
  - %MEM: Memory usage
  - TIME+: CPU time
  - COMMAND: Process name
EOF

cat top_reference.txt

# Better alternative: htop (if available)
# Install: sudo apt install htop
echo "If available, use htop for better interface"
echo "Features: Color coding, mouse support, tree view, easier navigation"

# Log top output for later analysis
top -b -n 1 > top_snapshot.txt
head -30 top_snapshot.txt
```

## Part 2: Process Control and Job Management

### Step 3: Background and Foreground Jobs

```bash
cd ~/ml-process-management

# Create a simple long-running script
cat > long_running_task.sh << 'EOF'
#!/bin/bash
# Simulate long-running ML task

for i in {1..60}; do
    echo "Processing epoch $i/60..."
    sleep 1
done
echo "Training complete!"
EOF

chmod +x long_running_task.sh

# Run in foreground (blocks terminal)
# ./long_running_task.sh

# Run in background with &
./long_running_task.sh &
# Note the job number [1] and PID

# List background jobs
jobs
# Shows: [1]+ Running

# Bring job to foreground
# fg %1
# Press Ctrl+Z to suspend

# Resume in background
# bg %1

# Create example workflow
cat > job_control_demo.sh << 'EOF'
#!/bin/bash
# Demonstrate job control

echo "Starting multiple background jobs..."

# Start job 1
(for i in {1..30}; do echo "Job 1: $i"; sleep 1; done) &
JOB1_PID=$!
echo "Started Job 1 (PID: $JOB1_PID)"

# Start job 2
(for i in {1..30}; do echo "Job 2: $i"; sleep 1; done) &
JOB2_PID=$!
echo "Started Job 2 (PID: $JOB2_PID)"

# List jobs
echo ""
echo "Current jobs:"
jobs

# Wait for all background jobs
wait
echo "All jobs completed"
EOF

chmod +x job_control_demo.sh
./job_control_demo.sh

# Job control reference
cat > job_control_reference.txt << 'EOF'
JOB CONTROL REFERENCE
=====================

Start jobs:
-----------
command &              Run in background
nohup command &        Run immune to hangups (continues after logout)
command </dev/null &   Run with no stdin

Control jobs:
-------------
jobs                   List background jobs
jobs -l                List with PIDs
fg                     Bring last job to foreground
fg %1                  Bring job 1 to foreground
bg                     Resume last suspended job in background
bg %1                  Resume job 1 in background

Signals:
--------
Ctrl+C                 Interrupt (SIGINT) - terminate foreground job
Ctrl+Z                 Suspend (SIGTSTP) - pause foreground job
Ctrl+D                 EOF - end of input

Job notation:
-------------
%1                     Job 1
%+                     Current job
%-                     Previous job
%?string               Job with 'string' in command
%%                     Current job (same as %+)

Examples:
---------
./train.py &           Run training in background
jobs                   List jobs
fg %1                  Bring to foreground
Ctrl+Z                 Suspend
bg %1                  Continue in background
kill %1                Terminate job 1
EOF

cat job_control_reference.txt
```

### Step 4: Process Signals and Termination

```bash
cd ~/ml-process-management

# Create test process
cat > signal_test.py << 'EOF'
#!/usr/bin/env python3
"""Test process for signal handling"""

import signal
import sys
import time

def signal_handler(signum, frame):
    print(f"\nReceived signal {signum}")
    if signum == signal.SIGTERM:
        print("Graceful shutdown...")
        sys.exit(0)
    elif signum == signal.SIGINT:
        print("Interrupted by user")
        sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

print(f"Process started (PID: {os.getpid()})")
print("Running... (Press Ctrl+C to interrupt)")

try:
    while True:
        print(f"Working... {time.time()}")
        time.sleep(2)
except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit(0)
EOF

chmod +x signal_test.py

# Kill command reference
cat > kill_reference.txt << 'EOF'
KILL COMMAND REFERENCE
======================

Basic usage:
------------
kill PID               Send SIGTERM (terminate gracefully)
kill -9 PID            Send SIGKILL (force kill)
kill -15 PID           Send SIGTERM (same as kill PID)
kill %1                Kill job 1
killall process_name   Kill all processes by name
pkill pattern          Kill processes matching pattern

Common signals:
---------------
Signal  Number  Description
------  ------  -----------
SIGHUP    1     Hangup (reload config)
SIGINT    2     Interrupt (Ctrl+C)
SIGQUIT   3     Quit (with core dump)
SIGKILL   9     Force kill (cannot be caught)
SIGTERM  15     Terminate gracefully (default)
SIGCONT  18     Continue if stopped
SIGSTOP  19     Stop process (cannot be caught)
SIGTSTP  20     Stop (Ctrl+Z)

Usage examples:
---------------
kill -l                List all signals
kill -15 1234          Gracefully terminate PID 1234
kill -9 1234           Force kill PID 1234
kill -TERM 1234        Same as kill -15
killall python         Kill all python processes
pkill -f "train.py"    Kill processes with "train.py" in command
pkill -u username      Kill all processes for user

Best practices:
---------------
1. Try SIGTERM first (kill -15)
2. Wait a few seconds
3. If process doesn't exit, use SIGKILL (kill -9)
4. Use killall/pkill carefully (affects multiple processes)

For ML training:
----------------
# Graceful shutdown (saves checkpoint)
kill -TERM <training_pid>

# Force kill (if hung)
kill -9 <training_pid>

# Kill all training jobs
pkill -f "train.py"
EOF

cat kill_reference.txt

# Demonstrate kill commands
cat > kill_demo.sh << 'EOF'
#!/bin/bash
# Demonstrate process termination

# Start test process
sleep 60 &
TEST_PID=$!
echo "Started test process (PID: $TEST_PID)"

# Verify it's running
ps -p $TEST_PID
echo ""

# Wait a moment
sleep 2

# Send SIGTERM
echo "Sending SIGTERM..."
kill -15 $TEST_PID

# Check if terminated
sleep 1
if ps -p $TEST_PID > /dev/null 2>&1; then
    echo "Process still running, force killing..."
    kill -9 $TEST_PID
else
    echo "Process terminated gracefully"
fi

# Verify termination
sleep 1
if ps -p $TEST_PID > /dev/null 2>&1; then
    echo "Process still exists (shouldn't happen)"
else
    echo "Process successfully terminated"
fi
EOF

chmod +x kill_demo.sh
./kill_demo.sh
```

## Part 3: ML Training Process Management

### Step 5: Simulating ML Training Processes

```bash
cd ~/ml-process-management
mkdir ml_training_sim
cd ml_training_sim

# Create realistic ML training simulator
cat > train_model.py << 'EOF'
#!/usr/bin/env python3
"""Simulated ML training process"""

import time
import sys
import signal
import json
import os
from datetime import datetime

class TrainingSimulator:
    def __init__(self, epochs=100, checkpoint_interval=10):
        self.epochs = epochs
        self.checkpoint_interval = checkpoint_interval
        self.current_epoch = 0
        self.running = True

        # Register signal handlers
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        signal.signal(signal.SIGINT, self.graceful_shutdown)

    def graceful_shutdown(self, signum, frame):
        print(f"\n[{datetime.now()}] Received signal {signum}")
        print(f"Saving checkpoint at epoch {self.current_epoch}...")
        self.save_checkpoint()
        print("Shutdown complete")
        sys.exit(0)

    def save_checkpoint(self):
        checkpoint = {
            'epoch': self.current_epoch,
            'timestamp': str(datetime.now()),
            'status': 'checkpoint'
        }
        with open(f'checkpoint_epoch_{self.current_epoch}.json', 'w') as f:
            json.dump(checkpoint, f, indent=2)
        print(f"Checkpoint saved: checkpoint_epoch_{self.current_epoch}.json")

    def train(self):
        print(f"Starting training for {self.epochs} epochs")
        print(f"PID: {os.getpid()}")
        print(f"Checkpoint interval: {self.checkpoint_interval} epochs")
        print("-" * 50)

        for epoch in range(1, self.epochs + 1):
            self.current_epoch = epoch

            # Simulate training
            print(f"Epoch {epoch}/{self.epochs} - Loss: {1.0/epoch:.4f} - Acc: {(1-1.0/epoch):.4f}")
            time.sleep(1)  # Simulate epoch time

            # Periodic checkpoint
            if epoch % self.checkpoint_interval == 0:
                self.save_checkpoint()

        print("-" * 50)
        print("Training complete!")

        # Save final model
        final_model = {
            'epochs': self.epochs,
            'final_accuracy': (1 - 1.0/self.epochs),
            'timestamp': str(datetime.now())
        }
        with open('final_model.json', 'w') as f:
            json.dump(final_model, f, indent=2)
        print("Final model saved: final_model.json")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='ML Training Simulator')
    parser.add_argument('--epochs', type=int, default=100, help='Number of epochs')
    parser.add_argument('--checkpoint-interval', type=int, default=10, help='Checkpoint interval')
    args = parser.parse_args()

    trainer = TrainingSimulator(epochs=args.epochs, checkpoint_interval=args.checkpoint_interval)
    trainer.train()
EOF

chmod +x train_model.py

# Create process management wrapper
cat > manage_training.sh << 'EOF'
#!/bin/bash
# Training process management wrapper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/training.pid"

mkdir -p "$LOG_DIR"

start_training() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Training already running (PID: $PID)"
            return 1
        fi
    fi

    echo "Starting training..."
    nohup python3 "$SCRIPT_DIR/train_model.py" --epochs 60 \
        > "$LOG_DIR/training.log" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"
    echo "Training started (PID: $PID)"
    echo "Log: $LOG_DIR/training.log"
}

stop_training() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No training process found"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Training process not running"
        rm "$PID_FILE"
        return 1
    fi

    echo "Stopping training (PID: $PID)..."
    kill -TERM $PID

    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null 2>&1; then
            echo "Training stopped gracefully"
            rm "$PID_FILE"
            return 0
        fi
        sleep 1
    done

    # Force kill if still running
    echo "Force stopping..."
    kill -9 $PID
    rm "$PID_FILE"
    echo "Training stopped (forced)"
}

status_training() {
    if [ ! -f "$PID_FILE" ]; then
        echo "Status: Not running"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Status: Running (PID: $PID)"
        echo ""
        ps -p $PID -o pid,ppid,%cpu,%mem,etime,cmd
        echo ""
        echo "Latest log entries:"
        tail -5 "$LOG_DIR/training.log"
    else
        echo "Status: Stopped (stale PID file)"
        rm "$PID_FILE"
    fi
}

tail_log() {
    if [ -f "$LOG_DIR/training.log" ]; then
        tail -f "$LOG_DIR/training.log"
    else
        echo "No log file found"
    fi
}

case "$1" in
    start)
        start_training
        ;;
    stop)
        stop_training
        ;;
    restart)
        stop_training
        sleep 2
        start_training
        ;;
    status)
        status_training
        ;;
    log)
        tail_log
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|log}"
        exit 1
        ;;
esac
EOF

chmod +x manage_training.sh

# Test the training manager
echo "=== Training Process Manager Demo ==="
./manage_training.sh start
sleep 5
./manage_training.sh status
sleep 3
./manage_training.sh stop
```

### Step 6: Monitoring ML Training Resources

```bash
cd ~/ml-process-management/ml_training_sim

# Create resource monitoring script
cat > monitor_resources.sh << 'EOF'
#!/bin/bash
# Monitor training process resources

PID_FILE="training.pid"
OUTPUT_FILE="resource_usage.csv"

# Create CSV header
echo "timestamp,cpu_percent,mem_percent,mem_rss_mb,mem_vsz_mb" > "$OUTPUT_FILE"

monitor_process() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No training process found"
        return 1
    fi

    PID=$(cat "$PID_FILE")

    if ! ps -p $PID > /dev/null 2>&1; then
        echo "Process not running"
        return 1
    fi

    echo "Monitoring PID: $PID"
    echo "Press Ctrl+C to stop monitoring"
    echo ""

    printf "%-20s %8s %8s %12s %12s\n" "TIME" "CPU%" "MEM%" "RSS(MB)" "VSZ(MB)"
    printf "%-20s %8s %8s %12s %12s\n" "----" "----" "----" "-------" "-------"

    while ps -p $PID > /dev/null 2>&1; do
        # Get process stats
        STATS=$(ps -p $PID -o %cpu,%mem,rss,vsz --no-headers)
        CPU=$(echo $STATS | awk '{print $1}')
        MEM=$(echo $STATS | awk '{print $2}')
        RSS=$(echo $STATS | awk '{print $3/1024}')  # Convert to MB
        VSZ=$(echo $STATS | awk '{print $4/1024}')  # Convert to MB

        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

        # Display
        printf "%-20s %7.1f%% %7.1f%% %11.1f %11.1f\n" \
            "$TIMESTAMP" "$CPU" "$MEM" "$RSS" "$VSZ"

        # Log to CSV
        echo "$TIMESTAMP,$CPU,$MEM,$RSS,$VSZ" >> "$OUTPUT_FILE"

        sleep 2
    done

    echo ""
    echo "Process ended"
    echo "Resource usage logged to: $OUTPUT_FILE"
}

monitor_process
EOF

chmod +x monitor_resources.sh

# Create resource analysis script
cat > analyze_resources.py << 'EOF'
#!/usr/bin/env python3
"""Analyze resource usage from monitoring data"""

import csv
import sys
from datetime import datetime

def analyze_resource_usage(csv_file):
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return

    cpu_values = []
    mem_values = []
    rss_values = []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cpu_values.append(float(row['cpu_percent']))
                mem_values.append(float(row['mem_percent']))
                rss_values.append(float(row['mem_rss_mb']))
            except (ValueError, KeyError):
                continue

    if not cpu_values:
        print("No data to analyze")
        return

    print("Resource Usage Analysis")
    print("=" * 50)
    print(f"Duration: {len(cpu_values) * 2} seconds ({len(cpu_values)} samples)")
    print()
    print("CPU Usage:")
    print(f"  Average: {sum(cpu_values)/len(cpu_values):.2f}%")
    print(f"  Maximum: {max(cpu_values):.2f}%")
    print(f"  Minimum: {min(cpu_values):.2f}%")
    print()
    print("Memory Usage:")
    print(f"  Average: {sum(mem_values)/len(mem_values):.2f}%")
    print(f"  Maximum: {max(mem_values):.2f}%")
    print(f"  Minimum: {min(mem_values):.2f}%")
    print()
    print("Memory (RSS):")
    print(f"  Average: {sum(rss_values)/len(rss_values):.2f} MB")
    print(f"  Maximum: {max(rss_values):.2f} MB")
    print(f"  Minimum: {min(rss_values):.2f} MB")

if __name__ == "__main__":
    import os
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "resource_usage.csv"
    analyze_resource_usage(csv_file)
EOF

chmod +x analyze_resources.py
```

## Part 4: GPU Process Management

### Step 7: Monitoring GPU Processes

```bash
cd ~/ml-process-management
mkdir gpu_management
cd gpu_management

# Create GPU monitoring reference
cat > gpu_monitoring_reference.txt << 'EOF'
GPU PROCESS MONITORING (NVIDIA)
===============================

nvidia-smi Commands:
--------------------
nvidia-smi                     Show GPU status
nvidia-smi -l 1                Continuous monitoring (1 sec interval)
nvidia-smi --query-gpu=...     Custom queries
nvidia-smi pmon                Process monitoring
nvidia-smi dmon                Device monitoring

Query GPU Information:
----------------------
nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu --format=csv

nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

List GPU Processes:
-------------------
nvidia-smi pmon -c 10          Monitor processes (10 iterations)
nvidia-smi pmon -s u           Show utilization only

Kill GPU Process:
-----------------
# Find process using GPU
nvidia-smi

# Kill by PID
kill -15 <PID>
# or force kill
kill -9 <PID>

Monitor Specific GPU:
---------------------
nvidia-smi -i 0                GPU 0 only
nvidia-smi -i 0,1              GPUs 0 and 1

Set GPU Persistence:
--------------------
# Keeps GPU initialized (faster job starts)
sudo nvidia-smi -pm 1

Examples:
---------
# Watch GPU usage
watch -n 1 nvidia-smi

# Log GPU stats
nvidia-smi --query-gpu=timestamp,name,utilization.gpu,memory.used --format=csv -l 5 > gpu_log.csv

# Find process using most GPU memory
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | sort -k2 -rn | head -1
EOF

cat gpu_monitoring_reference.txt

# Create GPU monitoring script (works if NVIDIA GPU present)
cat > monitor_gpu.sh << 'EOF'
#!/bin/bash
# Monitor GPU usage for ML training

# Check if nvidia-smi exists
if ! command -v nvidia-smi &> /dev/null; then
    echo "nvidia-smi not found. GPU monitoring not available."
    echo "This script requires an NVIDIA GPU with drivers installed."
    exit 1
fi

echo "=== GPU Monitoring ==="
echo ""

# Show GPU information
echo "GPU Information:"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv

echo ""
echo "Current GPU Usage:"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv

echo ""
echo "GPU Processes:"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv

echo ""
echo "Starting continuous monitoring (Press Ctrl+C to stop)..."
echo "Update interval: 2 seconds"
nvidia-smi -l 2
EOF

chmod +x monitor_gpu.sh

# Create GPU process management script
cat > gpu_process_manager.sh << 'EOF'
#!/bin/bash
# Manage GPU processes

list_gpu_processes() {
    if ! command -v nvidia-smi &> /dev/null; then
        echo "nvidia-smi not available"
        return 1
    fi

    echo "=== GPU Processes ==="
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
}

kill_gpu_process() {
    local pid=$1

    if [ -z "$pid" ]; then
        echo "Usage: $0 kill <PID>"
        return 1
    fi

    # Verify process is using GPU
    if nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -q "^$pid$"; then
        echo "Stopping GPU process $pid..."
        kill -TERM $pid
        sleep 2

        if ps -p $pid > /dev/null 2>&1; then
            echo "Process still running, force killing..."
            kill -9 $pid
        else
            echo "Process stopped"
        fi
    else
        echo "PID $pid not found in GPU processes"
        return 1
    fi
}

case "$1" in
    list)
        list_gpu_processes
        ;;
    kill)
        kill_gpu_process "$2"
        ;;
    monitor)
        ./monitor_gpu.sh
        ;;
    *)
        echo "Usage: $0 {list|kill <PID>|monitor}"
        exit 1
        ;;
esac
EOF

chmod +x gpu_process_manager.sh
```

## Part 5: System Services with systemctl

### Step 8: Managing System Services

```bash
cd ~/ml-process-management
mkdir service_management
cd service_management

# Create systemd reference
cat > systemd_reference.txt << 'EOF'
SYSTEMD SERVICE MANAGEMENT
==========================

Basic Commands:
---------------
systemctl status service_name     Check service status
systemctl start service_name      Start service
systemctl stop service_name       Stop service
systemctl restart service_name    Restart service
systemctl reload service_name     Reload configuration
systemctl enable service_name     Enable at boot
systemctl disable service_name    Disable at boot

System State:
-------------
systemctl list-units              List all units
systemctl list-units --failed     List failed units
systemctl list-unit-files         List unit files
systemctl is-active service       Check if active
systemctl is-enabled service      Check if enabled

Service Logs:
-------------
journalctl -u service_name        View service logs
journalctl -u service -f          Follow logs
journalctl -u service -n 50       Last 50 lines
journalctl --since "1 hour ago"   Recent logs
journalctl --since today          Today's logs

Common ML-Related Services:
---------------------------
docker                  Docker daemon
nvidia-persistenced     NVIDIA persistence daemon
ssh                     SSH server
cron                    Scheduled tasks

Examples:
---------
# Check Docker status
systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable Docker at boot
sudo systemctl enable docker

# View Docker logs
journalctl -u docker -n 100

# Restart SSH
sudo systemctl restart sshd
EOF

cat systemd_reference.txt

# Create example service unit file
cat > ml-training.service << 'EOF'
[Unit]
Description=ML Training Service
After=network.target

[Service]
Type=simple
User=mluser
WorkingDirectory=/opt/ml/training
ExecStart=/usr/bin/python3 /opt/ml/training/train.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
CPUQuota=200%
MemoryLimit=8G

# Environment
Environment="CUDA_VISIBLE_DEVICES=0"
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
EOF

cat > systemd_service_guide.md << 'EOF'
# Creating Systemd Services for ML Training

## Service Unit File Structure

Location: `/etc/systemd/system/service-name.service`

```ini
[Unit]
Description=Service description
After=network.target          # Start after network

[Service]
Type=simple                   # Service type
User=username                 # Run as user
WorkingDirectory=/path        # Working directory
ExecStart=/path/to/command    # Command to run
Restart=on-failure            # Restart policy
RestartSec=10                 # Restart delay

# Resource limits
CPUQuota=200%                 # Max 2 CPUs
MemoryLimit=8G                # Max 8GB RAM

# Environment variables
Environment="VAR=value"

[Install]
WantedBy=multi-user.target    # Enable target
```

## Installation Steps

1. Create service file:
   ```bash
   sudo nano /etc/systemd/system/ml-training.service
   ```

2. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable service:
   ```bash
   sudo systemctl enable ml-training
   ```

4. Start service:
   ```bash
   sudo systemctl start ml-training
   ```

5. Check status:
   ```bash
   sudo systemctl status ml-training
   ```

## Useful Commands

```bash
# View logs
journalctl -u ml-training -f

# Restart service
sudo systemctl restart ml-training

# Stop service
sudo systemctl stop ml-training

# Disable service
sudo systemctl disable ml-training
```

## Best Practices

1. Run as dedicated user (not root)
2. Set resource limits
3. Configure restart policy
4. Use environment variables for configuration
5. Log to journal for centralized logging
6. Test service before enabling at boot
EOF

cat systemd_service_guide.md
```

## Part 6: Persistent Sessions with screen and tmux

### Step 9: Using screen for Long-Running Training

```bash
cd ~/ml-process-management
mkdir persistent_sessions
cd persistent_sessions

# Create screen reference
cat > screen_reference.txt << 'EOF'
SCREEN REFERENCE
================

Screen allows persistent terminal sessions that survive disconnection.

Starting Screen:
----------------
screen                  Start new session
screen -S name          Start named session
screen -ls              List sessions
screen -r               Reattach to session
screen -r name          Reattach to named session
screen -d name          Detach session
screen -X -S name quit  Kill named session

Inside Screen Session:
----------------------
Ctrl+a d                Detach from session
Ctrl+a c                Create new window
Ctrl+a n                Next window
Ctrl+a p                Previous window
Ctrl+a "                List windows
Ctrl+a 0-9              Switch to window 0-9
Ctrl+a k                Kill current window
Ctrl+a [                Enter copy mode (scroll back)
Ctrl+a ]                Paste
Ctrl+a ?                Help

ML Training Workflow:
---------------------
# Start training in screen
screen -S training
python train.py --epochs 100
# Ctrl+a d to detach

# Reattach later
screen -r training

# Check from outside
screen -ls

Examples:
---------
# Multiple experiments
screen -S exp001
python train.py --config exp001.yaml
# Ctrl+a d

screen -S exp002
python train.py --config exp002.yaml
# Ctrl+a d

# List running experiments
screen -ls

# Reattach to specific experiment
screen -r exp001
EOF

cat screen_reference.txt

# Create tmux reference (more modern alternative)
cat > tmux_reference.txt << 'EOF'
TMUX REFERENCE
==============

Tmux is a modern screen alternative with more features.

Starting Tmux:
--------------
tmux                    Start new session
tmux new -s name        Start named session
tmux ls                 List sessions
tmux attach             Attach to last session
tmux attach -t name     Attach to named session
tmux kill-session -t name  Kill session

Inside Tmux (Prefix: Ctrl+b):
------------------------------
Ctrl+b d                Detach from session
Ctrl+b c                Create new window
Ctrl+b n                Next window
Ctrl+b p                Previous window
Ctrl+b w                List windows
Ctrl+b 0-9              Switch to window 0-9
Ctrl+b &                Kill window
Ctrl+b %                Split pane vertically
Ctrl+b "                Split pane horizontally
Ctrl+b arrow            Navigate panes
Ctrl+b [                Enter copy mode
Ctrl+b ?                Help

ML Training Workflow:
---------------------
# Start training session
tmux new -s training
python train.py --epochs 100
# Ctrl+b d to detach

# Reattach later
tmux attach -t training

# Multiple panes for monitoring
tmux new -s monitor
# Ctrl+b % to split vertically
# In left pane: python train.py
# In right pane: nvidia-smi -l 1

Examples:
---------
# Create experiment session
tmux new -s exp001

# Split into 3 panes
# Ctrl+b % (split vertical)
# Ctrl+b " (split horizontal in right pane)

# Pane 1: Training
python train.py

# Pane 2: GPU monitoring
nvidia-smi -l 2

# Pane 3: Resource monitoring
htop

# Detach: Ctrl+b d
# Reattach: tmux attach -t exp001
EOF

cat tmux_reference.txt

# Create practical training launcher
cat > launch_training.sh << 'EOF'
#!/bin/bash
# Launch training in persistent session

EXPERIMENT_NAME="${1:-experiment}"
TRAINING_SCRIPT="${2:-train.py}"
SESSION_TYPE="${3:-tmux}"  # tmux or screen

if [ "$SESSION_TYPE" = "tmux" ]; then
    if ! command -v tmux &> /dev/null; then
        echo "tmux not installed. Using screen."
        SESSION_TYPE="screen"
    fi
fi

echo "Launching training: $EXPERIMENT_NAME"
echo "Script: $TRAINING_SCRIPT"
echo "Session type: $SESSION_TYPE"
echo ""

if [ "$SESSION_TYPE" = "tmux" ]; then
    # Launch with tmux
    tmux new-session -d -s "$EXPERIMENT_NAME"
    tmux send-keys -t "$EXPERIMENT_NAME" "cd $(pwd)" C-m
    tmux send-keys -t "$EXPERIMENT_NAME" "python3 $TRAINING_SCRIPT" C-m

    echo "Training started in tmux session: $EXPERIMENT_NAME"
    echo "Attach with: tmux attach -t $EXPERIMENT_NAME"
    echo "Detach with: Ctrl+b d"
else
    # Launch with screen
    screen -dmS "$EXPERIMENT_NAME" bash -c "cd $(pwd) && python3 $TRAINING_SCRIPT"

    echo "Training started in screen session: $EXPERIMENT_NAME"
    echo "Attach with: screen -r $EXPERIMENT_NAME"
    echo "Detach with: Ctrl+a d"
fi

echo ""
echo "List sessions:"
if [ "$SESSION_TYPE" = "tmux" ]; then
    tmux ls
else
    screen -ls
fi
EOF

chmod +x launch_training.sh
```

## Part 7: Troubleshooting and Recovery

### Step 10: Handling Problematic Processes

```bash
cd ~/ml-process-management
mkdir troubleshooting
cd troubleshooting

# Create troubleshooting guide
cat > process_troubleshooting.md << 'EOF'
# Process Troubleshooting Guide

## Problem: Process Won't Stop

### Symptoms
- `kill -15 PID` doesn't terminate process
- Process shows as running but unresponsive

### Solutions

1. Try graceful shutdown:
   ```bash
   kill -TERM <PID>
   wait 10 seconds
   ```

2. If still running, force kill:
   ```bash
   kill -9 <PID>
   ```

3. Check if it's a zombie process:
   ```bash
   ps aux | grep <PID>
   # If status shows Z, it's a zombie
   # Kill parent process to reap zombie
   ps -o ppid= -p <PID>
   kill -9 <PPID>
   ```

## Problem: Process Consuming 100% CPU

### Diagnosis
```bash
# Find CPU hogs
top -o %CPU
# or
ps aux --sort=-%cpu | head -10
```

### Solutions

1. Lower process priority:
   ```bash
   renice +10 <PID>
   # +10 = lower priority (nice value 10)
   ```

2. Limit CPU with cpulimit:
   ```bash
   cpulimit -p <PID> -l 50
   # Limit to 50% of one CPU
   ```

3. Kill if necessary:
   ```bash
   kill -15 <PID>
   ```

## Problem: Out of Memory (OOM)

### Symptoms
- Process killed unexpectedly
- "Killed" message in logs
- dmesg shows OOM killer messages

### Diagnosis
```bash
# Check for OOM kills in system log
dmesg | grep -i "killed process"
journalctl -k | grep -i "out of memory"

# Check memory usage
free -h
ps aux --sort=-%mem | head -10
```

### Solutions

1. Reduce batch size or model size
2. Enable swap (if not already):
   ```bash
   sudo swapon -s
   ```
3. Monitor memory before running:
   ```bash
   free -h
   ```

## Problem: Training Process Stuck

### Diagnosis
```bash
# Check process state
ps aux | grep <PID>
# Look at STAT column
# D = uninterruptible sleep (usually I/O)
# S = sleeping
# R = running

# Check what process is waiting for
sudo cat /proc/<PID>/stack

# Check I/O wait
iostat -x 1

# Check if waiting on network
netstat -anp | grep <PID>
```

### Solutions

1. If I/O wait:
   - Check disk space: `df -h`
   - Check disk performance: `iostat -x 1`
   - Check for filesystem issues

2. If network wait:
   - Check network connectivity
   - Verify remote services are responding

3. Last resort - force kill:
   ```bash
   kill -9 <PID>
   ```

## Problem: Too Many Processes

### Diagnosis
```bash
# Count processes per user
ps aux | awk '{print $1}' | sort | uniq -c | sort -rn

# Find process limit
ulimit -u
```

### Solutions

1. Kill unnecessary processes:
   ```bash
   pkill -u username process_name
   ```

2. Increase user process limit (temporary):
   ```bash
   ulimit -u 4096
   ```

## Problem: Can't Find Process

### Solutions

1. Search by name:
   ```bash
   pgrep -a python
   ps aux | grep train
   ```

2. Search by port:
   ```bash
   lsof -i :8080
   netstat -tulpn | grep 8080
   ```

3. Search by file:
   ```bash
   lsof /path/to/file
   ```
EOF

cat process_troubleshooting.md

# Create diagnostic script
cat > diagnose_process.sh << 'EOF'
#!/bin/bash
# Comprehensive process diagnostic

PID=$1

if [ -z "$PID" ]; then
    echo "Usage: $0 <PID>"
    exit 1
fi

if ! ps -p $PID > /dev/null 2>&1; then
    echo "Process $PID not found"
    exit 1
fi

echo "=== Process Diagnostics for PID: $PID ==="
echo ""

echo "Process Information:"
ps -p $PID -o pid,ppid,user,%cpu,%mem,vsz,rss,stat,start,time,command

echo ""
echo "Process Tree:"
pstree -p $PID

echo ""
echo "Open Files:"
lsof -p $PID 2>/dev/null | head -20

echo ""
echo "Network Connections:"
lsof -i -a -p $PID 2>/dev/null

echo ""
echo "Resource Limits:"
cat /proc/$PID/limits 2>/dev/null

echo ""
echo "Environment Variables:"
cat /proc/$PID/environ 2>/dev/null | tr '\0' '\n' | head -10

echo ""
echo "Current Working Directory:"
readlink /proc/$PID/cwd 2>/dev/null

echo ""
echo "Command Line:"
cat /proc/$PID/cmdline 2>/dev/null | tr '\0' ' '
echo ""
EOF

chmod +x diagnose_process.sh
```

## Final Validation

```bash
cd ~/ml-process-management

cat > validate_exercise.sh << 'EOF'
#!/bin/bash
# Validate Exercise 03 completion

echo "=== Exercise 03 Validation ==="
echo ""

PASS=0
FAIL=0

# Check directories
for dir in ml_training_sim gpu_management service_management persistent_sessions troubleshooting; do
    if [ -d "$dir" ]; then
        echo "✓ Directory exists: $dir"
        ((PASS++))
    else
        echo "✗ Missing directory: $dir"
        ((FAIL++))
    fi
done

# Check scripts
for script in ml_training_sim/manage_training.sh ml_training_sim/monitor_resources.sh; do
    if [ -x "$script" ]; then
        echo "✓ Script executable: $script"
        ((PASS++))
    else
        echo "✗ Script not executable: $script"
        ((FAIL++))
    fi
done

# Check understanding
echo ""
echo "Knowledge Check:"
echo "1. Can you explain the difference between kill -15 and kill -9?"
echo "2. What does the STAT column 'D' mean in ps output?"
echo "3. How do you detach from a screen session?"

echo ""
echo "=== Results ==="
echo "Passed: $PASS"
echo "Failed: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo "✓ All validations passed!"
    exit 0
else
    echo "✗ Some validations failed"
    exit 1
fi
EOF

chmod +x validate_exercise.sh
./validate_exercise.sh
```

## Troubleshooting

**Problem**: Can't kill process with regular kill
- **Solution**: Use `kill -9 <PID>` for force kill
- Check if you own the process: `ps -p <PID> -o user=`

**Problem**: Process becomes zombie (Z state)
- **Solution**: Kill parent process or wait for parent to reap
- Find parent: `ps -o ppid= -p <PID>`

**Problem**: screen/tmux not installed
- **Solution**: Install with package manager
- `sudo apt install screen tmux`

**Problem**: nvidia-smi not found
- **Solution**: Install NVIDIA drivers
- Or skip GPU sections if no NVIDIA GPU

**Problem**: Permission denied for systemctl
- **Solution**: Use sudo: `sudo systemctl start service`
- Or work with user services: `systemctl --user`

## Reflection Questions

1. When would you use kill -9 vs kill -15?
2. How can you monitor a training job after disconnecting from SSH?
3. What's the benefit of using systemd for ML services?
4. How would you limit CPU/memory for a training process?
5. What tools would you use to diagnose a hung process?
6. Why is graceful shutdown important for ML training?

## Next Steps

After completing this exercise:
- **Exercise 04**: Shell Scripting - Automate process management
- **Exercise 05**: Package Management - Install ML software stacks
- **Lecture 04**: Shell Scripting Basics

## Additional Resources

- Process Management: https://www.digitalocean.com/community/tutorials/process-management-in-linux
- systemd Guide: https://www.digitalocean.com/community/tutorials/systemd-essentials-working-with-services-units-and-the-journal
- Screen Tutorial: https://linuxize.com/post/how-to-use-linux-screen/
- Tmux Guide: https://tmuxcheatsheet.com/

---

**Congratulations!** You've mastered Linux process management for ML infrastructure. You can now monitor, control, and troubleshoot training jobs effectively.
