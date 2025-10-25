# Exercise 07: Real-World Troubleshooting Scenarios

## Overview

This exercise puts your Linux skills to the test with realistic ML infrastructure troubleshooting scenarios. You'll diagnose and fix common issues like disk full errors, permission problems, hung processes, memory issues, and network connectivity problems.

## Learning Objectives

By completing this exercise, you will:
- Diagnose system resource issues (disk, memory, CPU)
- Troubleshoot permission and ownership problems
- Handle runaway and stuck processes
- Debug network connectivity issues
- Resolve package dependency conflicts
- Fix GPU and CUDA-related problems
- Create systematic troubleshooting workflows
- Document solutions for future reference

## Prerequisites

- Completed all previous exercises (01-06)
- All lectures in Module 002
- Confidence with Linux command line
- Access to a test Linux system

## Time Required

- Estimated: 90 minutes
- Difficulty: Intermediate to Advanced

## Scenario 1: Disk Full Error

### Problem

```
Your ML training job fails with error: "OSError: [Errno 28] No space left on device"
The model was saving checkpoints to /var/ml/checkpoints/
```

### Investigation

```bash
mkdir -p ~/troubleshooting-lab/scenario1
cd ~/troubleshooting-lab/scenario1

cat > scenario1_investigate.sh << 'EOF'
#!/bin/bash
# Investigate disk space issue

echo "=== Scenario 1: Disk Full Error ==="
echo ""

echo "Step 1: Check disk usage"
df -h

echo ""
echo "Step 2: Identify large directories"
du -sh /var/* 2>/dev/null | sort -hr | head -10

echo ""
echo "Step 3: Find large files"
find /var -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -10

echo ""
echo "Step 4: Check ML checkpoint directory"
du -sh /var/ml/checkpoints/ 2>/dev/null || echo "Directory not accessible"
ls -lh /var/ml/checkpoints/ 2>/dev/null | head -10

echo ""
echo "Step 5: Check inode usage (sometimes runs out before disk space)"
df -i

echo ""
echo "Step 6: Find old checkpoint files"
find /var/ml/checkpoints -type f -mtime +7 2>/dev/null | wc -l
EOF

chmod +x scenario1_investigate.sh

cat > scenario1_solution.sh << 'EOF'
#!/bin/bash
# Solution: Clean up old checkpoints

echo "=== Solution: Free up disk space ==="
echo ""

# Simulate cleanup (don't actually delete in exercise)
cat << 'SOLUTION'
1. Remove old checkpoints (keep last 5)
   ls -t /var/ml/checkpoints/*.h5 | tail -n +6 | xargs rm

2. Compress old checkpoints instead of deleting
   find /var/ml/checkpoints -name "*.h5" -mtime +7 -exec gzip {} \;

3. Move to cheaper storage
   rsync -av /var/ml/checkpoints/ /mnt/archive/checkpoints/
   rm /var/ml/checkpoints/*.h5

4. Clean up temporary files
   rm -rf /tmp/*
   rm -rf ~/.cache/*

5. Clean up package caches
   sudo apt clean  # Ubuntu
   sudo yum clean all  # RHEL

6. Check Docker if installed
   docker system prune -a  # Remove unused containers/images

7. Set up log rotation
   sudo logrotate -f /etc/logrotate.conf

8. Implement automatic cleanup script
   # Add to crontab: daily cleanup of files older than 7 days
   0 2 * * * find /var/ml/checkpoints -mtime +7 -delete

Prevention:
-----------
- Implement checkpoint retention policy
- Monitor disk usage with alerting
- Use separate partition for ML data
- Implement automatic cleanup
- Compress old checkpoints
- Archive to object storage (S3, GCS)
SOLUTION

echo ""
echo "Implementation script:"
cat << 'SCRIPT'
#!/bin/bash
# cleanup_checkpoints.sh

CHECKPOINT_DIR="/var/ml/checkpoints"
KEEP_COUNT=5
ARCHIVE_DIR="/mnt/archive/checkpoints"
COMPRESS_DAYS=7

# Keep only last N checkpoints
ls -t $CHECKPOINT_DIR/*.h5 2>/dev/null | tail -n +$((KEEP_COUNT + 1)) | xargs rm -f

# Compress old checkpoints
find $CHECKPOINT_DIR -name "*.h5" -mtime +$COMPRESS_DAYS -exec gzip {} \;

# Archive compressed checkpoints
mkdir -p $ARCHIVE_DIR
find $CHECKPOINT_DIR -name "*.h5.gz" -exec mv {} $ARCHIVE_DIR/ \;

echo "Cleanup complete"
SCRIPT
EOF

chmod +x scenario1_solution.sh
```

## Scenario 2: Permission Denied

### Problem

```
Training script fails: "PermissionError: [Errno 13] Permission denied: '/data/processed/train.csv'"
The file exists but the training process can't read it.
```

### Investigation & Solution

```bash
cd ~/troubleshooting-lab
mkdir scenario2
cd scenario2

cat > scenario2_debug.sh << 'EOF'
#!/bin/bash
# Debug permission issue

echo "=== Scenario 2: Permission Denied ==="
echo ""

# Simulate the environment
mkdir -p /tmp/ml_scenario2/data/processed
echo "sample,data" > /tmp/ml_scenario2/data/processed/train.csv
chmod 600 /tmp/ml_scenario2/data/processed/train.csv
chown root:root /tmp/ml_scenario2/data/processed/train.csv 2>/dev/null || true

DATA_FILE="/tmp/ml_scenario2/data/processed/train.csv"

echo "Step 1: Check if file exists"
ls -l $DATA_FILE 2>&1

echo ""
echo "Step 2: Check file permissions"
stat $DATA_FILE 2>&1

echo ""
echo "Step 3: Check ownership"
ls -l $DATA_FILE | awk '{print "Owner:", $3, "Group:", $4}'

echo ""
echo "Step 4: Check current user and groups"
echo "Current user: $(whoami)"
echo "Groups: $(groups)"

echo ""
echo "Step 5: Try to read file"
cat $DATA_FILE 2>&1 || echo "Cannot read file"

echo ""
echo "Step 6: Check parent directory permissions"
ls -ld $(dirname $DATA_FILE)

echo ""
echo "=== Solution ==="
cat << 'SOLUTION'
Possible fixes:

1. If you own the file:
   chmod 644 /data/processed/train.csv

2. If someone else owns it:
   sudo chown $(whoami) /data/processed/train.csv
   OR
   sudo chgrp mlteam /data/processed/train.csv
   chmod g+r /data/processed/train.csv

3. If running as service user:
   sudo chown ml-service:ml-service /data/processed/train.csv

4. Check parent directory:
   chmod 755 /data/processed

5. Use ACLs for fine-grained access:
   setfacl -m u:ml-user:r /data/processed/train.csv

Prevention:
-----------
- Set proper umask: umask 0002
- Use consistent ownership for ML directories
- Document permission requirements
- Use groups for team access
SOLUTION

# Cleanup
rm -rf /tmp/ml_scenario2
EOF

chmod +x scenario2_debug.sh
./scenario2_debug.sh
```

## Scenario 3: Process Hung/Not Responding

### Problem

```
Training process (PID 12345) has been running for 6 hours but isn't making progress.
GPU utilization is 0%, but process won't respond to Ctrl+C.
```

### Investigation & Solution

```bash
cd ~/troubleshooting-lab
mkdir scenario3
cd scenario3

cat > scenario3_debug.sh << 'EOF'
#!/bin/bash
# Debug hung process

echo "=== Scenario 3: Hung Process ==="
echo ""

# For demonstration, use current shell's PID
DEMO_PID=$$

echo "Investigating hung process (demo PID: $DEMO_PID)"
echo ""

echo "Step 1: Check if process exists"
ps -p $DEMO_PID

echo ""
echo "Step 2: Check process state"
ps -p $DEMO_PID -o pid,stat,time,cmd

echo ""
echo "Step 3: Check what process is waiting for"
cat /proc/$DEMO_PID/stack 2>/dev/null || echo "Stack not readable"

echo ""
echo "Step 4: Check open files"
lsof -p $DEMO_PID 2>/dev/null | head -10 || echo "lsof not available"

echo ""
echo "Step 5: Check system calls (strace)"
echo "Command: sudo strace -p $DEMO_PID"

echo ""
echo "Step 6: Check I/O wait"
iostat -x 1 2 2>/dev/null || echo "iostat not available"

echo ""
echo "=== Solution Steps ==="
cat << 'SOLUTION'
1. Try graceful termination first:
   kill -TERM 12345
   # Wait 10 seconds
   sleep 10

2. If still running, send SIGKILL:
   kill -9 12345

3. If process becomes zombie:
   # Find parent process
   ps -o ppid= -p 12345
   # Kill parent to reap zombie
   kill -9 <parent_pid>

4. Check for deadlock or I/O wait:
   # If in D state (uninterruptible sleep)
   # Usually waiting for I/O - check disk/network

5. Debug with strace (if possible):
   sudo strace -p 12345
   # Shows what system calls are hanging

Common causes:
--------------
- Network I/O timeout (waiting for remote data)
- Disk I/O wait (slow storage, bad disk)
- Deadlock in code
- Waiting for GPU that's busy
- Waiting for locked file/resource

Prevention:
-----------
- Implement timeouts in code
- Monitor process state
- Use watchdog timers
- Log progress regularly
- Handle signals properly
SOLUTION
EOF

chmod +x scenario3_debug.sh
./scenario3_debug.sh
```

## Scenario 4: Out of Memory (OOM)

### Problem

```
Training process is killed unexpectedly with "Killed" message
dmesg shows: "Out of memory: Kill process 12345 (python)"
```

### Investigation & Solution

```bash
cd ~/troubleshooting-lab
mkdir scenario4
cd scenario4

cat > scenario4_debug.sh << 'EOF'
#!/bin/bash
# Debug OOM issue

echo "=== Scenario 4: Out of Memory ==="
echo ""

echo "Step 1: Check for OOM kills in system log"
sudo dmesg | grep -i "out of memory" | tail -10

echo ""
echo "Step 2: Check current memory usage"
free -h

echo ""
echo "Step 3: Check swap usage"
swapon -s

echo ""
echo "Step 4: Find memory-hungry processes"
ps aux --sort=-%mem | head -10

echo ""
echo "Step 5: Check memory limits for user"
ulimit -a | grep -i mem

echo ""
echo "Step 6: Check OOM killer logs"
journalctl -k | grep -i "killed process" | tail -5

echo ""
echo "=== Solution ==="
cat << 'SOLUTION'
Immediate fixes:
----------------
1. Reduce batch size in training:
   # In training config
   batch_size = 16  # instead of 32

2. Enable swap if not present:
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   # Add to /etc/fstab for persistence
   /swapfile none swap sw 0 0

3. Free up memory:
   # Drop caches (safe)
   sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches

4. Use gradient accumulation:
   # Simulate larger batch size without memory
   accumulation_steps = 4
   batch_size = 8  # effective batch = 8 * 4 = 32

5. Use mixed precision training:
   # Reduces memory usage by 50%
   from tensorflow import keras
   keras.mixed_precision.set_global_policy('mixed_float16')

6. Enable memory growth (TensorFlow):
   import tensorflow as tf
   gpus = tf.config.list_physical_devices('GPU')
   for gpu in gpus:
       tf.config.experimental.set_memory_growth(gpu, True)

7. Set memory limits:
   # Limit process memory
   ulimit -v 8000000  # 8GB in KB

Long-term fixes:
----------------
- Add more RAM
- Use distributed training
- Implement data generators (don't load all at once)
- Profile memory usage
- Use sparse data structures
- Optimize model architecture
- Monitor memory usage continuously

Prevention:
-----------
- Profile memory before full training run
- Start with small dataset to test
- Monitor memory during training
- Set up alerts for high memory usage
- Document memory requirements
SOLUTION
EOF

chmod +x scenario4_debug.sh
./scenario4_debug.sh
```

## Scenario 5: CUDA/GPU Not Available

### Problem

```
Training script reports: "No CUDA-capable device is detected"
But nvidia-smi shows GPU is present
```

### Investigation & Solution

```bash
cd ~/troubleshooting-lab
mkdir scenario5
cd scenario5

cat > scenario5_debug.sh << 'EOF'
#!/bin/bash
# Debug CUDA availability issue

echo "=== Scenario 5: CUDA Not Available ==="
echo ""

echo "Step 1: Check if GPU is detected by system"
lspci | grep -i nvidia || echo "No NVIDIA GPU found by lspci"

echo ""
echo "Step 2: Check NVIDIA driver"
nvidia-smi 2>&1 || echo "nvidia-smi failed - driver issue?"

echo ""
echo "Step 3: Check CUDA installation"
nvcc --version 2>&1 || echo "nvcc not found - CUDA not installed?"

echo ""
echo "Step 4: Check CUDA library path"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
ldconfig -p | grep cuda || echo "CUDA libraries not in ldconfig"

echo ""
echo "Step 5: Check Python CUDA packages"
python3 << 'PYTHON'
try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
    print(f"CUDA available: {tf.test.is_built_with_cuda()}")
    print(f"GPU devices: {tf.config.list_physical_devices('GPU')}")
except ImportError:
    print("TensorFlow not installed")

try:
    import torch
    print(f"\nPyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CUDA version: {torch.version.cuda}")
except ImportError:
    print("PyTorch not installed")
PYTHON

echo ""
echo "Step 6: Check for driver/CUDA version mismatch"
echo "Driver version (from nvidia-smi):"
nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null
echo ""
echo "CUDA version:"
nvcc --version 2>/dev/null | grep release

echo ""
echo "=== Solution ==="
cat << 'SOLUTION'
Common causes and fixes:

1. Driver not loaded:
   sudo modprobe nvidia
   # Check if loaded
   lsmod | grep nvidia

2. Driver/CUDA version mismatch:
   # Check compatibility matrix:
   # https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/
   # Reinstall matching versions

3. Wrong CUDA package for framework:
   # TensorFlow
   pip install tensorflow[and-cuda]  # TF 2.13+

   # PyTorch - install with correct CUDA version
   pip install torch --index-url https://download.pytorch.org/whl/cu118

4. Library path not set:
   export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
   export PATH=/usr/local/cuda/bin:$PATH
   # Add to ~/.bashrc for persistence

5. Permissions issue:
   # Add user to video group
   sudo usermod -aG video $USER
   # Log out and back in

6. Docker container needs GPU access:
   docker run --gpus all ...
   # Or install nvidia-docker2

7. Virtual environment issue:
   # Reinstall CUDA-enabled packages in venv
   pip install --upgrade --force-reinstall tensorflow[and-cuda]

8. Multiple CUDA versions:
   # Set specific version
   export CUDA_HOME=/usr/local/cuda-11.8
   export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

Verification:
-------------
# TensorFlow
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# PyTorch
python3 -c "import torch; print(torch.cuda.is_available())"

# CUDA sample
cd /usr/local/cuda/samples/1_Utilities/deviceQuery
sudo make
./deviceQuery
SOLUTION
EOF

chmod +x scenario5_debug.sh
./scenario5_debug.sh
```

## Scenario 6: Network Connectivity Issues

### Problem

```
Training script can't download dataset: "ConnectionError: Failed to establish connection"
wget and curl to the URL also fail
```

### Investigation & Solution

```bash
cd ~/troubleshooting-lab
mkdir scenario6
cd scenario6

cat > scenario6_debug.sh << 'EOF'
#!/bin/bash
# Debug network connectivity

echo "=== Scenario 6: Network Connectivity ==="
echo ""

URL="https://example.com/dataset.tar.gz"

echo "Step 1: Check network interface"
ip addr show

echo ""
echo "Step 2: Check default route"
ip route show

echo ""
echo "Step 3: Check DNS resolution"
nslookup example.com || echo "DNS resolution failed"

echo ""
echo "Step 4: Ping gateway"
GATEWAY=$(ip route | grep default | awk '{print $3}')
ping -c 3 $GATEWAY 2>&1 || echo "Cannot reach gateway"

echo ""
echo "Step 5: Ping external server"
ping -c 3 8.8.8.8 || echo "Cannot reach internet"

echo ""
echo "Step 6: Check DNS servers"
cat /etc/resolv.conf

echo ""
echo "Step 7: Test HTTP connection"
curl -I $URL 2>&1 || echo "HTTP request failed"

echo ""
echo "Step 8: Check firewall rules"
sudo iptables -L 2>/dev/null || echo "iptables not accessible"

echo ""
echo "Step 9: Check proxy settings"
echo "HTTP_PROXY: $HTTP_PROXY"
echo "HTTPS_PROXY: $HTTPS_PROXY"
echo "NO_PROXY: $NO_PROXY"

echo ""
echo "=== Solution ==="
cat << 'SOLUTION'
Diagnosis and fixes:

1. DNS not working:
   # Temporary fix
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

   # Permanent fix (Ubuntu)
   sudo nano /etc/systemd/resolved.conf
   # Add: DNS=8.8.8.8 1.1.1.1
   sudo systemctl restart systemd-resolved

2. No internet connectivity:
   # Check network service
   sudo systemctl status NetworkManager
   sudo systemctl restart NetworkManager

3. Firewall blocking:
   # Check if firewall is active
   sudo ufw status
   # Allow outbound HTTPS
   sudo ufw allow out 443/tcp

4. Proxy required:
   # Set proxy
   export HTTP_PROXY=http://proxy.example.com:8080
   export HTTPS_PROXY=http://proxy.example.com:8080
   # Add to ~/.bashrc

   # For Python requests
   pip install requests[socks]

5. SSL certificate issues:
   # Temporary bypass (NOT for production)
   curl -k $URL
   # Python
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context

   # Proper fix - update certificates
   sudo update-ca-certificates

6. Download from alternative mirror:
   # Use different CDN/mirror
   # Or download manually and transfer

7. Rate limiting:
   # Add delays between requests
   # Use resumable downloads
   wget -c $URL  # Continue interrupted download

8. Timeout issues:
   # Increase timeout
   curl --connect-timeout 30 --max-time 600 $URL
   # Python requests
   requests.get(url, timeout=600)

Prevention:
-----------
- Test network before starting training
- Implement retry logic with exponential backoff
- Cache datasets locally
- Use multiple download mirrors
- Monitor network connectivity
SOLUTION
EOF

chmod +x scenario6_debug.sh
./scenario6_debug.sh
```

## Comprehensive Troubleshooting Checklist

```bash
cd ~/troubleshooting-lab

cat > troubleshooting_checklist.md << 'EOF'
# ML Infrastructure Troubleshooting Checklist

## Before Starting Troubleshooting

1. [ ] What changed recently?
2. [ ] Can you reproduce the issue?
3. [ ] What error message do you see?
4. [ ] When did it last work?
5. [ ] Check recent logs

## System Resources

### Disk Space
- [ ] Check disk usage: `df -h`
- [ ] Find large files: `du -sh /* | sort -hr`
- [ ] Check inodes: `df -i`
- [ ] Clean up temp files: `rm -rf /tmp/*`

### Memory
- [ ] Check memory: `free -h`
- [ ] Check swap: `swapon -s`
- [ ] Find memory hogs: `ps aux --sort=-%mem | head`
- [ ] Check for OOM kills: `dmesg | grep -i "out of memory"`

### CPU
- [ ] Check load: `uptime`
- [ ] Find CPU hogs: `top` or `htop`
- [ ] Check per-core usage: `mpstat -P ALL`

### GPU
- [ ] Check GPU status: `nvidia-smi`
- [ ] Check GPU processes: `nvidia-smi pmon`
- [ ] Check CUDA: `nvcc --version`

## Process Issues

- [ ] Check if running: `ps aux | grep process_name`
- [ ] Check process state: `ps -p PID -o state`
- [ ] Check what it's waiting for: `cat /proc/PID/stack`
- [ ] Check open files: `lsof -p PID`
- [ ] Try graceful kill: `kill -TERM PID`
- [ ] Force kill if needed: `kill -9 PID`

## Permissions

- [ ] Check file permissions: `ls -l file`
- [ ] Check ownership: `stat file`
- [ ] Check user groups: `groups`
- [ ] Check directory permissions: `ls -ld dir/`
- [ ] Check ACLs: `getfacl file`

## Network

- [ ] Check interface: `ip addr`
- [ ] Check routing: `ip route`
- [ ] Test DNS: `nslookup example.com`
- [ ] Test connectivity: `ping 8.8.8.8`
- [ ] Test port: `telnet host port`
- [ ] Check listening ports: `netstat -tulpn`

## Logs

- [ ] Check application logs: `tail -f /var/log/app.log`
- [ ] Check system logs: `journalctl -xe`
- [ ] Check for errors: `grep -i error /var/log/syslog`
- [ ] Check dmesg: `dmesg | tail`

## ML-Specific

- [ ] Verify dataset path exists
- [ ] Check dataset integrity
- [ ] Verify model architecture
- [ ] Check framework version compatibility
- [ ] Verify CUDA/cuDNN versions match
- [ ] Check batch size vs available memory
- [ ] Verify input data shape
- [ ] Check for NaN/Inf in data

## Docker (if applicable)

- [ ] Check containers: `docker ps -a`
- [ ] Check logs: `docker logs container_name`
- [ ] Check resources: `docker stats`
- [ ] Check network: `docker network ls`
- [ ] Check volumes: `docker volume ls`

## Recovery Actions

- [ ] Restart service: `sudo systemctl restart service`
- [ ] Reload configuration: `sudo systemctl reload service`
- [ ] Clear caches
- [ ] Reboot if necessary (last resort)
- [ ] Restore from backup

## Documentation

- [ ] Document the issue
- [ ] Document the solution
- [ ] Update runbook
- [ ] Share with team
- [ ] Create preventive measures
EOF

cat troubleshooting_checklist.md
```

## Validation

```bash
cd ~/troubleshooting-lab

cat > validate_exercise.sh << 'EOF'
#!/bin/bash

echo "=== Exercise 07 Validation ==="
echo ""

PASS=0
FAIL=0

# Check all scenarios created
for i in {1..6}; do
    if [ -d "scenario$i" ]; then
        echo "✓ Scenario $i directory created"
        ((PASS++))
    else
        echo "✗ Scenario $i missing"
        ((FAIL++))
    fi
done

# Check debug scripts
for i in {1..6}; do
    script="scenario$i/scenario${i}_debug.sh"
    if [ -x "$script" ]; then
        echo "✓ Script: scenario$i debug"
        ((PASS++))
    else
        echo "✗ Script missing: $script"
        ((FAIL++))
    fi
done

# Check checklist
if [ -f "troubleshooting_checklist.md" ]; then
    echo "✓ Troubleshooting checklist created"
    ((PASS++))
else
    echo "✗ Checklist missing"
    ((FAIL++))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -eq 0 ]; then
    echo "✓ Exercise complete!"
else
    echo "✗ Some components missing"
fi
EOF

chmod +x validate_exercise.sh
./validate_exercise.sh
```

## Summary

You've now worked through 7 common troubleshooting scenarios:

1. **Disk Full** - Cleanup and space management
2. **Permission Denied** - Ownership and access control
3. **Hung Process** - Process state diagnosis
4. **Out of Memory** - Memory management
5. **CUDA Not Available** - GPU troubleshooting
6. **Network Issues** - Connectivity debugging

## Key Takeaways

1. Always check logs first
2. Verify basic assumptions (file exists, permissions, resources)
3. Use systematic approach (isolate, identify, fix, verify)
4. Document solutions for future reference
5. Implement preventive measures
6. Test fixes in safe environment first

## Reflection Questions

1. What's your systematic approach to troubleshooting?
2. How do you prioritize multiple issues?
3. When do you ask for help vs continue debugging?
4. How do you prevent recurring issues?
5. What tools are most valuable for troubleshooting?

## Next Steps

- **Module 003**: Docker and Containerization
- Practice these scenarios on test systems
- Build your own troubleshooting runbook
- Share knowledge with your team

## Additional Resources

- Linux troubleshooting guide: https://www.redhat.com/sysadmin/
- Performance tuning: https://www.brendangregg.com/linuxperf.html
- ML debugging guide: https://fullstackdeeplearning.com/

---

**Congratulations!** You've completed all Linux Essentials exercises! You're now equipped to handle real-world ML infrastructure challenges.
