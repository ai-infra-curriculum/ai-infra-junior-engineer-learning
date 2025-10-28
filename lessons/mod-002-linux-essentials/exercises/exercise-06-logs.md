# Exercise 06: Log File Analysis for ML Systems

## Overview

This exercise teaches you to analyze log files from ML training systems, troubleshoot issues, and extract insights from logs. You'll work with application logs, system logs, and training metrics to diagnose problems and monitor ML workloads.

## Learning Objectives

By completing this exercise, you will:
- Read and analyze different types of log files
- Use grep, awk, sed for log parsing
- Monitor logs in real-time with tail
- Analyze system logs with journalctl
- Extract training metrics from logs
- Identify error patterns and root causes
- Create log analysis scripts
- Set up log rotation and retention

## Prerequisites

- Completed Exercises 01-05
- Completed Lecture 07: Text Processing Tools
- Understanding of Linux command line
- Basic regex knowledge
- Text editor familiarity

## Time Required

- Estimated: 60-75 minutes
- Difficulty: Intermediate

## Part 1: Understanding Log Files

### Step 1: Common Log Locations

```bash
mkdir -p ~/log-analysis-lab
cd ~/log-analysis-lab

cat > log_locations.md << 'EOF'
# Common Linux Log Locations

## System Logs
```
/var/log/syslog          System messages (Debian/Ubuntu)
/var/log/messages        System messages (RHEL/CentOS)
/var/log/auth.log        Authentication logs
/var/log/kern.log        Kernel logs
/var/log/dmesg           Boot messages
/var/log/boot.log        Boot process logs
```

## Application Logs
```
/var/log/apache2/        Apache web server
/var/log/nginx/          Nginx web server
/var/log/mysql/          MySQL database
/var/log/postgresql/     PostgreSQL database
```

## Journal (systemd)
```
journalctl               View all logs
journalctl -u service    Service-specific logs
journalctl -f            Follow logs (like tail -f)
```

## ML Application Logs (typical)
```
/var/log/ml/training/    Training logs
/var/log/ml/inference/   Inference logs
/var/log/ml/api/         API logs
~/ml-projects/*/logs/    Project-specific logs
```

## Log Levels
```
DEBUG    Detailed debug information
INFO     Informational messages
WARNING  Warning messages
ERROR    Error messages
CRITICAL Critical failures
```
EOF

cat log_locations.md

# Create sample log files
mkdir -p sample_logs

# Training log
cat > sample_logs/training.log << 'EOF'
2024-10-18 10:00:00 INFO Starting training session
2024-10-18 10:00:01 INFO Loading dataset from /data/train
2024-10-18 10:00:05 INFO Dataset loaded: 50000 samples
2024-10-18 10:00:06 INFO Model architecture: ResNet50
2024-10-18 10:00:10 INFO Epoch 1/100 - loss: 2.3012 - accuracy: 0.1234 - val_loss: 2.1234 - val_accuracy: 0.1567
2024-10-18 10:01:30 INFO Epoch 2/100 - loss: 1.8765 - accuracy: 0.3456 - val_loss: 1.7890 - val_accuracy: 0.3789
2024-10-18 10:02:45 WARNING Learning rate: 0.001 may be too high
2024-10-18 10:03:00 INFO Epoch 3/100 - loss: 1.5432 - accuracy: 0.4567 - val_loss: 1.4567 - val_accuracy: 0.4890
2024-10-18 10:04:15 ERROR CUDA out of memory - reducing batch size from 32 to 16
2024-10-18 10:04:20 INFO Resuming training with batch size 16
2024-10-18 10:05:30 INFO Epoch 4/100 - loss: 1.2345 - accuracy: 0.5678 - val_loss: 1.1890 - val_accuracy: 0.5901
2024-10-18 10:06:45 INFO Checkpoint saved to /models/checkpoints/epoch_4.h5
2024-10-18 10:07:00 INFO Epoch 5/100 - loss: 1.0123 - accuracy: 0.6345 - val_loss: 0.9876 - val_accuracy: 0.6512
2024-10-18 10:08:15 WARNING Validation loss increased - possible overfitting
2024-10-18 10:08:30 INFO Early stopping triggered
2024-10-18 10:08:31 INFO Training completed in 8 minutes 31 seconds
2024-10-18 10:08:32 INFO Best model saved to /models/final/best_model.h5
2024-10-18 10:08:33 INFO Final metrics - loss: 1.0123 - accuracy: 0.6345
EOF

# API log
cat > sample_logs/api.log << 'EOF'
2024-10-18 10:00:00 INFO [API] Server started on port 8080
2024-10-18 10:05:23 INFO [REQUEST] GET /predict - IP: 192.168.1.100 - User-Agent: curl/7.68.0
2024-10-18 10:05:23 INFO [RESPONSE] 200 - Prediction: class_2 - Confidence: 0.876 - Duration: 45ms
2024-10-18 10:06:45 INFO [REQUEST] POST /predict/batch - IP: 192.168.1.101 - User-Agent: python-requests/2.28.0
2024-10-18 10:06:46 INFO [RESPONSE] 200 - Batch size: 100 - Duration: 1234ms
2024-10-18 10:08:12 WARNING [REQUEST] GET /predict - IP: 192.168.1.102 - Rate limit: 90/100
2024-10-18 10:08:12 ERROR [RESPONSE] 400 - Invalid input format - Duration: 5ms
2024-10-18 10:10:01 ERROR [REQUEST] POST /predict - IP: 192.168.1.103 - Authentication failed
2024-10-18 10:10:01 ERROR [RESPONSE] 401 - Unauthorized - Duration: 2ms
2024-10-18 10:12:34 INFO [REQUEST] GET /health - IP: 192.168.1.100
2024-10-18 10:12:34 INFO [RESPONSE] 200 - Status: healthy - Model loaded: true - GPU available: true
EOF

# Error log
cat > sample_logs/errors.log << 'EOF'
2024-10-18 09:45:12 ERROR Failed to load model from /models/missing_model.h5: File not found
2024-10-18 10:04:15 ERROR CUDA out of memory: Tried to allocate 2.50 GiB (GPU 0; 7.79 GiB total capacity)
2024-10-18 10:08:12 ERROR Invalid input shape: expected (224, 224, 3), got (256, 256, 3)
2024-10-18 10:10:01 ERROR Authentication failed for user: test_user - Invalid API key
2024-10-18 11:23:45 ERROR Database connection failed: Connection refused (localhost:5432)
2024-10-18 12:15:30 ERROR Disk I/O error: No space left on device (/var/log partition full)
2024-10-18 13:45:22 ERROR Failed to deserialize input: JSONDecodeError at line 15, column 23
2024-10-18 14:30:11 ERROR Model inference timeout: Request exceeded 30s limit
2024-10-18 15:12:45 ERROR Segmentation fault in preprocessing module (core dumped)
2024-10-18 16:20:33 ERROR Network timeout: Failed to download dataset from https://example.com/data.zip
EOF
```

### Step 2: Basic Log Reading

```bash
cd ~/log-analysis-lab

cat > read_logs.sh << 'EOF'
#!/bin/bash
# Basic log reading commands

LOG_DIR="sample_logs"

echo "=== View entire log ==="
cat $LOG_DIR/training.log

echo ""
echo "=== View with line numbers ==="
cat -n $LOG_DIR/training.log

echo ""
echo "=== View first 5 lines ==="
head -5 $LOG_DIR/training.log

echo ""
echo "=== View last 5 lines ==="
tail -5 $LOG_DIR/training.log

echo ""
echo "=== View specific line range (lines 5-10) ==="
sed -n '5,10p' $LOG_DIR/training.log

echo ""
echo "=== Follow log in real-time (simulated) ==="
echo "Command: tail -f $LOG_DIR/training.log"
echo "(Press Ctrl+C to stop)"
EOF

chmod +x read_logs.sh
```

## Part 2: Log Filtering with grep

### Step 3: Finding Errors and Patterns

```bash
cd ~/log-analysis-lab

cat > grep_logs.sh << 'EOF'
#!/bin/bash
# Filter logs with grep

LOG_DIR="sample_logs"

echo "=== Find all ERROR messages ==="
grep "ERROR" $LOG_DIR/training.log

echo ""
echo "=== Find ERROR or WARNING ==="
grep -E "ERROR|WARNING" $LOG_DIR/training.log

echo ""
echo "=== Count errors ==="
echo "Total errors: $(grep -c "ERROR" $LOG_DIR/errors.log)"

echo ""
echo "=== Find errors with context ==="
echo "Showing 2 lines before and after each error:"
grep -C 2 "ERROR" $LOG_DIR/training.log

echo ""
echo "=== Case-insensitive search ==="
grep -i "cuda" $LOG_DIR/training.log

echo ""
echo "=== Invert match (exclude INFO) ==="
grep -v "INFO" $LOG_DIR/training.log

echo ""
echo "=== Find lines with accuracy > 0.5 ==="
grep "accuracy: 0\.[5-9]" $LOG_DIR/training.log

echo ""
echo "=== Extract epoch numbers ==="
grep -o "Epoch [0-9]*" $LOG_DIR/training.log

echo ""
echo "=== Search multiple files ==="
grep -r "ERROR" $LOG_DIR/

echo ""
echo "=== Show only filenames with matches ==="
grep -l "CUDA" $LOG_DIR/*

echo ""
echo "=== Highlight matches (with color) ==="
grep --color=always "ERROR" $LOG_DIR/training.log
EOF

chmod +x grep_logs.sh
./grep_logs.sh
```

### Step 4: Advanced Log Parsing with awk

```bash
cd ~/log-analysis-lab

cat > awk_logs.sh << 'EOF'
#!/bin/bash
# Parse logs with awk

LOG_DIR="sample_logs"

echo "=== Extract timestamps and messages ==="
awk '{print $1, $2, $4, $5, $6}' $LOG_DIR/training.log

echo ""
echo "=== Extract only ERROR messages ==="
awk '/ERROR/ {print $0}' $LOG_DIR/training.log

echo ""
echo "=== Count log levels ==="
echo "Log level statistics:"
awk '{print $3}' $LOG_DIR/training.log | sort | uniq -c

echo ""
echo "=== Extract metrics from training logs ==="
echo "Epoch metrics:"
awk '/Epoch [0-9]+\/100/ {
    match($0, /loss: ([0-9.]+)/, loss);
    match($0, /accuracy: ([0-9.]+)/, acc);
    print "Epoch", $5, "Loss:", loss[1], "Accuracy:", acc[1]
}' $LOG_DIR/training.log

echo ""
echo "=== Calculate average response time ==="
awk -F'Duration: |ms' '/Duration/ {
    sum += $(NF-1);
    count++
}
END {
    if (count > 0)
        print "Average response time:", sum/count, "ms"
}' $LOG_DIR/api.log

echo ""
echo "=== Extract API endpoints ==="
awk '/REQUEST/ {
    match($0, /(GET|POST|PUT|DELETE) ([^ ]+)/, m);
    print m[1], m[2]
}' $LOG_DIR/api.log | sort | uniq -c

echo ""
echo "=== Count errors by type ==="
awk -F': ' '/ERROR/ {
    print $2
}' $LOG_DIR/errors.log | sort | uniq -c | sort -rn
EOF

chmod +x awk_logs.sh
./awk_logs.sh
```

## Part 3: Training Metrics Extraction

### Step 5: Extract and Visualize Metrics

```bash
cd ~/log-analysis-lab

cat > extract_metrics.sh << 'EOF'
#!/bin/bash
# Extract training metrics from logs

LOG_FILE="sample_logs/training.log"
OUTPUT_CSV="training_metrics.csv"

echo "Extracting training metrics..."

# Create CSV header
echo "epoch,loss,accuracy,val_loss,val_accuracy" > $OUTPUT_CSV

# Extract metrics using awk
awk '/Epoch [0-9]+\/100/ {
    match($0, /Epoch ([0-9]+)/, epoch);
    match($0, /loss: ([0-9.]+)/, loss);
    match($0, /accuracy: ([0-9.]+)/, acc);
    match($0, /val_loss: ([0-9.]+)/, val_loss);
    match($0, /val_accuracy: ([0-9.]+)/, val_acc);

    printf "%d,%.4f,%.4f,%.4f,%.4f\n",
        epoch[1], loss[1], acc[1], val_loss[1], val_acc[1]
}' $LOG_FILE >> $OUTPUT_CSV

echo "Metrics saved to: $OUTPUT_CSV"
cat $OUTPUT_CSV

# Generate statistics
echo ""
echo "=== Training Statistics ==="
awk -F',' 'NR>1 {
    loss_sum += $2;
    acc_sum += $3;
    count++
    if ($2 < best_loss || best_loss == 0) best_loss = $2;
    if ($3 > best_acc) best_acc = $3;
}
END {
    print "Total epochs:", count;
    printf "Average loss: %.4f\n", loss_sum/count;
    printf "Average accuracy: %.4f\n", acc_sum/count;
    printf "Best loss: %.4f\n", best_loss;
    printf "Best accuracy: %.4f\n", best_acc;
}' $OUTPUT_CSV
EOF

chmod +x extract_metrics.sh
./extract_metrics.sh

# Create Python visualization script
cat > visualize_metrics.py << 'EOF'
#!/usr/bin/env python3
"""Visualize training metrics from CSV"""

import csv
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Read metrics
epochs = []
loss = []
accuracy = []
val_loss = []
val_accuracy = []

with open('training_metrics.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        epochs.append(int(row['epoch']))
        loss.append(float(row['loss']))
        accuracy.append(float(row['accuracy']))
        val_loss.append(float(row['val_loss']))
        val_accuracy.append(float(row['val_accuracy']))

# Create plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# Loss plot
ax1.plot(epochs, loss, label='Training Loss', marker='o')
ax1.plot(epochs, val_loss, label='Validation Loss', marker='s')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Training and Validation Loss')
ax1.legend()
ax1.grid(True)

# Accuracy plot
ax2.plot(epochs, accuracy, label='Training Accuracy', marker='o')
ax2.plot(epochs, val_accuracy, label='Validation Accuracy', marker='s')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Training and Validation Accuracy')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('training_metrics.png', dpi=150)
print("Plot saved to: training_metrics.png")
EOF

chmod +x visualize_metrics.py
```

## Part 4: Error Pattern Analysis

### Step 6: Identify Common Issues

```bash
cd ~/log-analysis-lab

cat > analyze_errors.sh << 'EOF'
#!/bin/bash
# Analyze error patterns in logs

LOG_DIR="sample_logs"

echo "=== Error Analysis Report ==="
echo "Generated: $(date)"
echo ""

# Count total errors
echo "Total Errors:"
grep -c "ERROR" $LOG_DIR/*.log

echo ""
echo "=== Error Distribution by File ==="
for file in $LOG_DIR/*.log; do
    count=$(grep -c "ERROR" "$file" 2>/dev/null || echo 0)
    echo "  $(basename $file): $count errors"
done

echo ""
echo "=== Top 5 Error Types ==="
grep "ERROR" $LOG_DIR/*.log | \
    sed 's/.*ERROR //' | \
    cut -d':' -f1 | \
    sort | uniq -c | \
    sort -rn | head -5

echo ""
echo "=== Errors by Hour ==="
grep "ERROR" $LOG_DIR/*.log | \
    awk '{print $2}' | \
    cut -d':' -f1 | \
    sort | uniq -c

echo ""
echo "=== Critical Issues (CUDA/Memory/Disk) ==="
grep -E "CUDA|memory|disk|space" -i $LOG_DIR/*.log

echo ""
echo "=== Authentication Failures ==="
grep -i "auth.*fail\|unauthorized" $LOG_DIR/*.log

echo ""
echo "=== Database Issues ==="
grep -i "database\|connection.*fail" $LOG_DIR/*.log

echo ""
echo "=== Timeout Issues ==="
grep -i "timeout" $LOG_DIR/*.log
EOF

chmod +x analyze_errors.sh
./analyze_errors.sh
```

## Part 5: System Log Analysis

### Step 7: Working with journalctl

```bash
cd ~/log-analysis-lab

cat > journalctl_reference.md << 'EOF'
# journalctl Reference

## Basic Commands

```bash
# View all logs
journalctl

# Follow logs (like tail -f)
journalctl -f

# View logs for specific service
journalctl -u docker
journalctl -u nginx

# View logs since specific time
journalctl --since "2024-10-18 10:00:00"
journalctl --since "1 hour ago"
journalctl --since today
journalctl --since yesterday

# View logs until specific time
journalctl --until "2024-10-18 12:00:00"

# Time range
journalctl --since "2024-10-18 10:00:00" --until "2024-10-18 12:00:00"

# Last N lines
journalctl -n 100         # Last 100 lines
journalctl -n 50 -f       # Last 50 and follow

# Priority filtering
journalctl -p err         # Errors only
journalctl -p warning     # Warnings and above
journalctl -p debug       # All messages

# By process
journalctl _PID=1234
journalctl _COMM=python3

# Output format
journalctl -o json        # JSON format
journalctl -o json-pretty # Pretty JSON
journalctl -o verbose     # Verbose format
journalctl -o cat         # Concise output

# Boot logs
journalctl -b             # Current boot
journalctl -b -1          # Previous boot
journalctl --list-boots   # List all boots

# Disk usage
journalctl --disk-usage

# Verify logs
journalctl --verify
```

## Examples for ML Systems

```bash
# Monitor training service
journalctl -u ml-training.service -f

# Find CUDA errors
journalctl -p err | grep -i cuda

# API service errors today
journalctl -u ml-api --since today -p err

# Check system issues during training
journalctl --since "2024-10-18 10:00:00" --until "2024-10-18 11:00:00" -p warning

# Export logs
journalctl -u ml-training --since today > training_logs.txt
```
EOF

cat journalctl_reference.md
```

## Part 6: Log Rotation and Retention

### Step 8: Configure Log Rotation

```bash
cd ~/log-analysis-lab

cat > logrotate_example.conf << 'EOF'
# Log rotation configuration for ML application
# Place in /etc/logrotate.d/ml-app

/var/log/ml/training/*.log {
    daily                    # Rotate daily
    rotate 7                 # Keep 7 days of logs
    compress                 # Compress old logs
    delaycompress            # Don't compress most recent
    missingok                # Don't error if log missing
    notifempty               # Don't rotate if empty
    create 0640 mluser mluser  # Create new log with permissions
    sharedscripts            # Run postrotate once
    postrotate
        # Reload application to use new log file
        systemctl reload ml-training || true
    endscript
}

/var/log/ml/api/*.log {
    size 100M                # Rotate when > 100MB
    rotate 10                # Keep 10 rotations
    compress
    delaycompress
    missingok
    notifempty
    create 0640 mluser mluser
    postrotate
        systemctl reload ml-api || true
    endscript
}

/var/log/ml/errors.log {
    weekly                   # Rotate weekly
    rotate 12                # Keep 12 weeks
    compress
    delaycompress
    missingok
    notifempty
    create 0600 mluser mluser  # More restrictive for errors
}
EOF

cat > log_rotation_guide.md << 'EOF'
# Log Rotation Setup

## Install logrotate (if not installed)
```bash
sudo apt install logrotate  # Ubuntu/Debian
sudo yum install logrotate  # RHEL/CentOS
```

## Create configuration
```bash
sudo nano /etc/logrotate.d/ml-app
# Paste configuration from logrotate_example.conf
```

## Test configuration
```bash
# Test without rotating
sudo logrotate -d /etc/logrotate.d/ml-app

# Force rotation (for testing)
sudo logrotate -f /etc/logrotate.d/ml-app
```

## View rotation status
```bash
cat /var/lib/logrotate/status
```

## Manual rotation script
```bash
#!/bin/bash
# rotate_logs.sh

LOG_DIR="/var/log/ml"
ARCHIVE_DIR="/var/log/ml/archive"
RETENTION_DAYS=30

mkdir -p "$ARCHIVE_DIR"

# Rotate logs older than 1 day
find "$LOG_DIR" -name "*.log" -type f -mtime +1 -exec gzip {} \;

# Move compressed logs to archive
find "$LOG_DIR" -name "*.log.gz" -type f -exec mv {} "$ARCHIVE_DIR/" \;

# Delete old archives
find "$ARCHIVE_DIR" -name "*.log.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "Log rotation complete"
```
EOF

cat log_rotation_guide.md
```

## Part 7: Comprehensive Log Analysis Tool

### Step 9: Create Log Analysis Script

```bash
cd ~/log-analysis-lab

cat > log_analyzer.sh << 'EOF'
#!/bin/bash
###############################################################################
# Comprehensive Log Analyzer for ML Systems
###############################################################################

set -euo pipefail

# Configuration
LOG_DIR="${1:-sample_logs}"
REPORT_FILE="analysis_report_$(date +%Y%m%d_%H%M%S).txt"

# Generate report
{
    echo "========================================="
    echo "    ML System Log Analysis Report"
    echo "========================================="
    echo "Generated: $(date)"
    echo "Log Directory: $LOG_DIR"
    echo ""

    # Summary statistics
    echo "=== Summary Statistics ==="
    echo "Total log files: $(find "$LOG_DIR" -name "*.log" -type f | wc -l)"
    echo "Total log size: $(du -sh "$LOG_DIR" | cut -f1)"
    echo ""

    # Error statistics
    echo "=== Error Statistics ==="
    total_errors=$(grep -r "ERROR" "$LOG_DIR" 2>/dev/null | wc -l || echo 0)
    total_warnings=$(grep -r "WARNING" "$LOG_DIR" 2>/dev/null | wc -l || echo 0)
    echo "Total errors: $total_errors"
    echo "Total warnings: $total_warnings"
    echo ""

    # Top errors
    echo "=== Top 10 Error Types ==="
    grep -rh "ERROR" "$LOG_DIR" 2>/dev/null | \
        sed 's/.*ERROR //' | \
        cut -d':' -f1 | \
        sort | uniq -c | \
        sort -rn | head -10 || echo "No errors found"
    echo ""

    # Timeline
    echo "=== Error Timeline (by hour) ==="
    grep -rh "ERROR" "$LOG_DIR" 2>/dev/null | \
        awk '{print $2}' | \
        cut -d':' -f1 | \
        sort | uniq -c | \
        awk '{printf "%s:00 - %d errors\n", $2, $1}' || echo "No errors"
    echo ""

    # Critical issues
    echo "=== Critical Issues ==="
    echo "CUDA/GPU errors:"
    grep -ri "cuda\|gpu" "$LOG_DIR" 2>/dev/null | grep -i "error" | wc -l

    echo "Memory errors:"
    grep -ri "memory\|oom" "$LOG_DIR" 2>/dev/null | grep -i "error" | wc -l

    echo "Disk errors:"
    grep -ri "disk\|space" "$LOG_DIR" 2>/dev/null | grep -i "error" | wc -l

    echo ""

    # Performance metrics
    echo "=== Performance Metrics ==="
    if grep -q "Duration:" "$LOG_DIR"/*.log 2>/dev/null; then
        echo "API Response Times:"
        awk -F'Duration: |ms' '/Duration/ {
            sum += $(NF-1);
            count++;
            if ($(NF-1) < min || min == 0) min = $(NF-1);
            if ($(NF-1) > max) max = $(NF-1);
        }
        END {
            if (count > 0) {
                printf "  Average: %.2f ms\n", sum/count;
                printf "  Min: %.2f ms\n", min;
                printf "  Max: %.2f ms\n", max;
            }
        }' "$LOG_DIR"/*.log
    fi
    echo ""

    # Training metrics (if available)
    if grep -q "Epoch" "$LOG_DIR"/*.log 2>/dev/null; then
        echo "=== Training Metrics ==="
        echo "Total epochs completed:"
        grep -rh "Epoch [0-9]*/[0-9]*" "$LOG_DIR" | wc -l

        echo ""
        echo "Final metrics:"
        grep -h "Final metrics" "$LOG_DIR"/*.log 2>/dev/null || echo "Not available"
    fi
    echo ""

    # Recommendations
    echo "=== Recommendations ==="
    if [ $total_errors -gt 10 ]; then
        echo "⚠ High error count - investigate error patterns"
    fi

    if grep -riq "out of memory\|oom" "$LOG_DIR" 2>/dev/null; then
        echo "⚠ Memory issues detected - consider reducing batch size"
    fi

    if grep -riq "timeout" "$LOG_DIR" 2>/dev/null; then
        echo "⚠ Timeout issues detected - check network/system resources"
    fi

    if grep -riq "cuda.*error" "$LOG_DIR" 2>/dev/null; then
        echo "⚠ CUDA errors detected - verify GPU drivers and CUDA installation"
    fi

    echo ""
    echo "========================================="
    echo "End of Report"
    echo "========================================="

} | tee "$REPORT_FILE"

echo ""
echo "Report saved to: $REPORT_FILE"
EOF

chmod +x log_analyzer.sh
./log_analyzer.sh
```

## Validation

```bash
cd ~/log-analysis-lab

cat > validate_exercise.sh << 'EOF'
#!/bin/bash

echo "=== Exercise 06 Validation ==="
echo ""

PASS=0
FAIL=0

# Check sample logs created
if [ -d "sample_logs" ] && [ $(ls sample_logs/*.log 2>/dev/null | wc -l) -ge 3 ]; then
    echo "✓ Sample logs created"
    ((PASS++))
else
    echo "✗ Sample logs missing"
    ((FAIL++))
fi

# Check scripts
for script in grep_logs.sh awk_logs.sh extract_metrics.sh analyze_errors.sh log_analyzer.sh; do
    if [ -x "$script" ]; then
        echo "✓ Script: $script"
        ((PASS++))
    else
        echo "✗ Script missing/not executable: $script"
        ((FAIL++))
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
EOF

chmod +x validate_exercise.sh
./validate_exercise.sh
```

## Troubleshooting

**Problem**: Permission denied reading system logs
- **Solution**: Use sudo: `sudo cat /var/log/syslog`
- Or add user to adm group: `sudo usermod -aG adm $USER`

**Problem**: grep is slow on large logs
- **Solution**: Use `--line-buffered` for real-time or compress old logs

**Problem**: Can't parse timestamp format
- **Solution**: Adjust awk field separators or use date command

## Reflection Questions

1. What log levels should you monitor in production?
2. How would you set up real-time alerting on errors?
3. Why is log rotation important?
4. How can you correlate logs across multiple services?
5. What metrics can you extract from training logs?

## Next Steps

- **Exercise 07**: Troubleshooting Scenarios
- **Module 003**: Containerization with Docker

## Additional Resources

- rsyslog documentation: https://www.rsyslog.com/doc/
- journalctl manual: https://www.freedesktop.org/software/systemd/man/journalctl.html
- Log analysis best practices: https://www.loggly.com/ultimate-guide/analyzing-linux-logs/

---

**Congratulations!** You've mastered log file analysis for ML systems!
