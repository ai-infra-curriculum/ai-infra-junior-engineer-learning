# Exercise 08: System Automation and Maintenance for ML Infrastructure

## Overview

This hands-on exercise focuses on automating system maintenance tasks for ML infrastructure. You'll create automated backup scripts, set up monitoring alerts, configure log rotation, schedule cleanup tasks, and implement health checks—all critical skills for maintaining production ML systems.

## Learning Objectives

By completing this exercise, you will:
- Create automated backup scripts for ML artifacts
- Set up scheduled tasks using cron and systemd timers
- Implement system health checks and monitoring
- Configure log rotation for ML applications
- Build maintenance scripts for GPU servers
- Create alerting mechanisms for critical issues
- Document automation workflows
- Test and validate automated systems

## Prerequisites

- Completed exercises 01-07
- All lectures in Module 002, especially Lecture 04: System Administration Basics and Lecture 06: Advanced Shell Scripting
- Understanding of systemd and cron
- Access to a Linux system with sudo privileges
- Basic understanding of ML workflows

## Time Required

- Estimated: 120 minutes
- Difficulty: Intermediate to Advanced

---

## Part 1: Automated Model Backup System

### Task 1.1: Create Backup Script

Create a script that backs up ML models with versioning and retention policies.

```bash
# Create project directory
mkdir -p ~/ml-automation-lab/backups
cd ~/ml-automation-lab/backups

# Create backup script
cat > backup_models.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Configuration
MODEL_DIR="/opt/ml/models"
BACKUP_DIR="/backup/models"
RETENTION_DAYS=30
LOG_FILE="/var/log/ml-backup.log"
DATE=$(date +%Y%m%d_%H%M%S)

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "Starting model backup..."

# Create timestamped backup
BACKUP_NAME="models_backup_${DATE}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Backup with compression (exclude large temp files)
tar -czf "$BACKUP_PATH" \
    --exclude='*.tmp' \
    --exclude='checkpoints/temp' \
    -C "$(dirname $MODEL_DIR)" \
    "$(basename $MODEL_DIR)" 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    log "Backup completed successfully: $BACKUP_NAME (Size: $BACKUP_SIZE)"
else
    log "ERROR: Backup failed!"
    exit 1
fi

# Calculate checksum for integrity
CHECKSUM=$(sha256sum "$BACKUP_PATH" | awk '{print $1}')
echo "$CHECKSUM  $BACKUP_NAME" >> "${BACKUP_DIR}/checksums.txt"
log "Checksum: $CHECKSUM"

# Clean up old backups (keep last 30 days)
log "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "models_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
DELETED_COUNT=$(find "$BACKUP_DIR" -name "models_backup_*.tar.gz" -mtime +$RETENTION_DAYS | wc -l)
log "Deleted $DELETED_COUNT old backups"

# Upload to S3 (optional - uncomment if using AWS)
# aws s3 cp "$BACKUP_PATH" "s3://my-ml-backups/models/" --storage-class STANDARD_IA

log "Backup process completed"
EOF

chmod +x backup_models.sh
```

**Test the script:**

```bash
# Create test model directory
sudo mkdir -p /opt/ml/models/production
sudo mkdir -p /backup/models
sudo chown -R $USER:$USER /opt/ml /backup

# Create dummy model files
echo "model_v1.0" > /opt/ml/models/production/model.onnx
echo "config" > /opt/ml/models/production/config.yaml

# Run backup
./backup_models.sh

# Verify backup
ls -lh /backup/models/
cat /var/log/ml-backup.log
```

### Task 1.2: Schedule Daily Backups

Set up automated daily backups using cron:

```bash
# Open crontab
crontab -e

# Add this line (runs daily at 2 AM):
0 2 * * * /home/$USER/ml-automation-lab/backups/backup_models.sh

# Verify cron job
crontab -l
```

**Using systemd timer (alternative, recommended):**

```bash
# Create service file
sudo tee /etc/systemd/system/ml-backup.service > /dev/null << 'EOF'
[Unit]
Description=ML Model Backup Service
After=network.target

[Service]
Type=oneshot
User=mluser
ExecStart=/home/mluser/ml-automation-lab/backups/backup_models.sh
StandardOutput=journal
StandardError=journal
EOF

# Create timer file
sudo tee /etc/systemd/system/ml-backup.timer > /dev/null << 'EOF'
[Unit]
Description=Run ML backup daily
Requires=ml-backup.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable ml-backup.timer
sudo systemctl start ml-backup.timer

# Check timer status
systemctl status ml-backup.timer
systemctl list-timers ml-backup.timer
```

---

## Part 2: GPU Health Monitoring

### Task 2.1: Create GPU Monitoring Script

Build a script to monitor GPU health and send alerts:

```bash
mkdir -p ~/ml-automation-lab/monitoring
cd ~/ml-automation-lab/monitoring

cat > monitor_gpus.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Configuration
TEMP_THRESHOLD=80  # Celsius
MEMORY_THRESHOLD=90  # Percent
ALERT_EMAIL="ml-ops@company.com"
LOG_FILE="/var/log/gpu-monitor.log"

# Check if nvidia-smi is available
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. GPU monitoring requires NVIDIA drivers."
    exit 1
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

send_alert() {
    local subject="$1"
    local message="$2"

    # Log alert
    log "ALERT: $subject - $message"

    # Send email (requires mailutils)
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
    fi

    # Send to syslog
    logger -t gpu-monitor -p user.warning "$subject: $message"
}

# Query GPU status
GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader | head -1)
log "Monitoring $GPU_COUNT GPU(s)..."

nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total \
    --format=csv,noheader | while IFS=',' read -r idx name temp util_gpu util_mem mem_used mem_total; do

    # Clean up whitespace
    temp=$(echo $temp | xargs)
    util_gpu=$(echo $util_gpu | xargs | sed 's/ %//')
    util_mem=$(echo $util_mem | xargs | sed 's/ %//')
    mem_used=$(echo $mem_used | xargs)
    mem_total=$(echo $mem_total | xargs)

    log "GPU $idx ($name): Temp=${temp}°C, GPU_Util=${util_gpu}%, Mem_Util=${util_mem}%, Mem=${mem_used}/${mem_total}"

    # Check temperature
    if [ "$temp" -gt "$TEMP_THRESHOLD" ]; then
        send_alert "GPU Temperature Alert" "GPU $idx temperature is ${temp}°C (threshold: ${TEMP_THRESHOLD}°C)"
    fi

    # Check memory utilization
    if [ "$util_mem" -gt "$MEMORY_THRESHOLD" ]; then
        send_alert "GPU Memory Alert" "GPU $idx memory utilization is ${util_mem}% (threshold: ${MEMORY_THRESHOLD}%)"
    fi
done

log "GPU monitoring check completed"
EOF

chmod +x monitor_gpus.sh
```

**Test the monitoring script:**

```bash
# Run manually
./monitor_gpus.sh

# Check logs
cat /var/log/gpu-monitor.log
```

### Task 2.2: Schedule GPU Monitoring

```bash
# Run every 5 minutes
crontab -e

# Add:
*/5 * * * * /home/$USER/ml-automation-lab/monitoring/monitor_gpus.sh
```

---

## Part 3: Automated Log Rotation

### Task 3.1: Configure Log Rotation for ML Applications

```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/ml-applications > /dev/null << 'EOF'
/var/log/ml-api/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 mluser mluser
    sharedscripts
    postrotate
        # Reload application to use new log file
        systemctl reload ml-api.service > /dev/null 2>&1 || true
    endscript
}

/var/log/ml-training/*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    size 100M
    create 0640 mluser mluser
}

/var/log/gpu-monitor.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

# Test logrotate configuration
sudo logrotate -d /etc/logrotate.d/ml-applications

# Force rotation (for testing)
sudo logrotate -f /etc/logrotate.d/ml-applications
```

---

## Part 4: Automated Cleanup Tasks

### Task 4.1: Create Cleanup Script

```bash
mkdir -p ~/ml-automation-lab/cleanup
cd ~/ml-automation-lab/cleanup

cat > cleanup_ml_artifacts.sh << 'EOF'
#!/bin/bash
set -euo pipefail

LOG_FILE="/var/log/ml-cleanup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting ML artifact cleanup..."

# 1. Clean old experiment outputs (older than 30 days)
if [ -d "/opt/ml/experiments" ]; then
    OLD_EXPERIMENTS=$(find /opt/ml/experiments -type d -mtime +30 | wc -l)
    if [ "$OLD_EXPERIMENTS" -gt 0 ]; then
        log "Removing $OLD_EXPERIMENTS old experiment directories..."
        find /opt/ml/experiments -type d -mtime +30 -exec rm -rf {} +
    fi
fi

# 2. Clean old checkpoints (keep last 7 days)
if [ -d "/opt/ml/checkpoints" ]; then
    OLD_CHECKPOINTS=$(find /opt/ml/checkpoints -name "*.ckpt" -mtime +7 | wc -l)
    if [ "$OLD_CHECKPOINTS" -gt 0 ]; then
        log "Removing $OLD_CHECKPOINTS old checkpoint files..."
        find /opt/ml/checkpoints -name "*.ckpt" -mtime +7 -delete
    fi
fi

# 3. Clean Docker images (unused images older than 7 days)
if command -v docker &> /dev/null; then
    log "Cleaning unused Docker images..."
    docker image prune -a --filter "until=168h" -f
fi

# 4. Clean pip cache
log "Cleaning pip cache..."
pip cache purge 2>&1 | tee -a "$LOG_FILE"

# 5. Clean apt cache (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    log "Cleaning apt cache..."
    sudo apt-get clean
    sudo apt-get autoclean
fi

# 6. Report disk usage
log "Current disk usage:"
df -h / | tee -a "$LOG_FILE"

log "Cleanup completed"
EOF

chmod +x cleanup_ml_artifacts.sh
```

### Task 4.2: Schedule Weekly Cleanup

```bash
# Run every Sunday at 3 AM
crontab -e

# Add:
0 3 * * 0 /home/$USER/ml-automation-lab/cleanup/cleanup_ml_artifacts.sh
```

---

## Part 5: System Health Check Script

### Task 5.1: Comprehensive Health Check

```bash
mkdir -p ~/ml-automation-lab/health-check
cd ~/ml-automation-lab/health-check

cat > health_check.sh << 'EOF'
#!/bin/bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

echo "======================================"
echo "   ML Infrastructure Health Check"
echo "======================================"
echo ""

# 1. Disk Space
echo "1. Checking Disk Space..."
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    check_pass "Disk usage: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -lt 90 ]; then
    check_warn "Disk usage: ${DISK_USAGE}% (warning threshold)"
else
    check_fail "Disk usage: ${DISK_USAGE}% (critical!)"
fi

# 2. Memory
echo "2. Checking Memory..."
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')
if [ "$MEM_USAGE" -lt 85 ]; then
    check_pass "Memory usage: ${MEM_USAGE}%"
else
    check_warn "Memory usage: ${MEM_USAGE}% (high)"
fi

# 3. CPU Load
echo "3. Checking CPU Load..."
CPU_COUNT=$(nproc)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
LOAD_THRESHOLD=$(echo "$CPU_COUNT * 1.5" | bc)
if (( $(echo "$LOAD_AVG < $LOAD_THRESHOLD" | bc -l) )); then
    check_pass "Load average: $LOAD_AVG (CPUs: $CPU_COUNT)"
else
    check_warn "Load average: $LOAD_AVG (high for $CPU_COUNT CPUs)"
fi

# 4. Critical Services
echo "4. Checking Critical Services..."
SERVICES=("docker" "nginx")
for service in "${SERVICES[@]}"; do
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        check_pass "$service is running"
    else
        check_fail "$service is not running"
    fi
done

# 5. GPU Status (if available)
echo "5. Checking GPU Status..."
if command -v nvidia-smi &> /dev/null; then
    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader | head -1)
    check_pass "Found $GPU_COUNT GPU(s)"

    nvidia-smi --query-gpu=index,temperature.gpu,power.draw,power.limit \
        --format=csv,noheader | while IFS=',' read -r idx temp power_draw power_limit; do
        temp=$(echo $temp | xargs)
        power_draw=$(echo $power_draw | xargs | sed 's/ W//')
        power_limit=$(echo $power_limit | xargs | sed 's/ W//')

        if [ "$temp" -lt 75 ]; then
            check_pass "  GPU $idx: ${temp}°C, Power: ${power_draw}W/${power_limit}W"
        else
            check_warn "  GPU $idx: ${temp}°C (warm), Power: ${power_draw}W/${power_limit}W"
        fi
    done
else
    check_warn "nvidia-smi not found (no GPU or drivers not installed)"
fi

# 6. Network Connectivity
echo "6. Checking Network Connectivity..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    check_pass "Internet connectivity OK"
else
    check_fail "No internet connectivity"
fi

# 7. Recent Errors in Logs
echo "7. Checking Recent Errors..."
ERROR_COUNT=$(journalctl --since "1 hour ago" -p err | wc -l)
if [ "$ERROR_COUNT" -lt 10 ]; then
    check_pass "Recent errors: $ERROR_COUNT (last hour)"
else
    check_warn "Recent errors: $ERROR_COUNT (last hour - investigate)"
fi

echo ""
echo "======================================"
echo "   Health Check Complete"
echo "======================================"
EOF

chmod +x health_check.sh
```

**Run the health check:**

```bash
./health_check.sh
```

---

## Part 6: Integration and Testing

### Task 6.1: Create Master Automation Script

```bash
cat > ~/ml-automation-lab/run_all_maintenance.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "========================================"
echo " ML Infrastructure Automated Maintenance"
echo "========================================"
echo ""

# Run health check first
echo "Running health check..."
~/ml-automation-lab/health-check/health_check.sh
echo ""

# GPU monitoring
echo "Checking GPU status..."
~/ml-automation-lab/monitoring/monitor_gpus.sh
echo ""

# Backup (if needed)
echo "Running backup..."
~/ml-automation-lab/backups/backup_models.sh
echo ""

# Cleanup
echo "Running cleanup..."
~/ml-automation-lab/cleanup/cleanup_ml_artifacts.sh
echo ""

echo "All maintenance tasks completed!"
EOF

chmod +x ~/ml-automation-lab/run_all_maintenance.sh
```

### Task 6.2: Test All Automations

```bash
# Run all maintenance tasks
~/ml-automation-lab/run_all_maintenance.sh

# Verify cron jobs
crontab -l

# Check systemd timers
systemctl list-timers

# Review logs
tail -50 /var/log/ml-backup.log
tail -50 /var/log/gpu-monitor.log
tail -50 /var/log/ml-cleanup.log
```

---

## Deliverables

Submit the following:

1. **Scripts**:
   - `backup_models.sh` - Working backup script with logging
   - `monitor_gpus.sh` - GPU monitoring with alerts
   - `cleanup_ml_artifacts.sh` - Cleanup automation
   - `health_check.sh` - System health validation

2. **Configuration Files**:
   - Cron configuration (`crontab -l` output)
   - Systemd timer and service files
   - Logrotate configuration

3. **Documentation**:
   - README explaining each automation
   - Troubleshooting guide for common issues
   - Runbook for responding to alerts

4. **Evidence**:
   - Screenshots of successful script executions
   - Log file samples
   - Health check output

---

## Challenge Questions

1. **Monitoring**: How would you extend the GPU monitoring to track metrics in Prometheus?

2. **Backup Strategy**: What's the 3-2-1 backup rule and how does your script comply?

3. **Alerting**: How would you integrate with PagerDuty or Slack for critical alerts?

4. **Scaling**: How would you modify these scripts to work across 100 GPU servers?

5. **Testing**: How would you test your backup/restore process without disrupting production?

---

## Additional Resources

- [Cron Best Practices](https://www.man7.org/linux/man-pages/man5/crontab.5.html)
- [systemd Timers](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [Logrotate Documentation](https://linux.die.net/man/8/logrotate)
- [Bash Scripting Best Practices](https://google.github.io/styleguide/shellguide.html)
- [NVIDIA Management Library (NVML)](https://developer.nvidia.com/nvidia-management-library-nvml)

---

**Congratulations!** You've built a complete automation suite for ML infrastructure maintenance. These scripts form the foundation of production ML operations.
