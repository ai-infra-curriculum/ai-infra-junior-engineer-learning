# Exercise 04: Bash Scripting for ML Deployment Automation

## Overview

This exercise teaches you to write bash scripts for automating ML deployment workflows. You'll create scripts for model deployment, data pipeline automation, system monitoring, and backup operations. These are essential skills for building reliable, reproducible ML infrastructure.

## Learning Objectives

By completing this exercise, you will:
- Write structured bash scripts with proper syntax and best practices
- Use variables, functions, and control structures effectively
- Handle command-line arguments and user input
- Implement error handling and logging
- Create deployment automation scripts for ML models
- Build data processing pipelines with bash
- Develop monitoring and alerting scripts
- Write backup and restore scripts for ML infrastructure

## Prerequisites

- Completed Exercises 01-03
- Completed Lecture 05: Introduction to Shell Scripting
- Completed Lecture 06: Advanced Shell Scripting
- Comfortable with Linux command line
- Basic understanding of ML workflows
- Text editor (vim, nano, or VS Code)

## Time Required

- Estimated: 90 minutes
- Difficulty: Intermediate

## Part 1: Bash Scripting Fundamentals

### Step 1: Your First ML Automation Script

```bash
# Create workspace
mkdir -p ~/ml-scripting-lab
cd ~/ml-scripting-lab

# Create first script
cat > hello_ml.sh << 'EOF'
#!/bin/bash
# My first ML automation script

echo "Hello from ML Infrastructure!"
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
echo "Today's date: $(date)"

# Check if CUDA is available
if command -v nvidia-smi &> /dev/null; then
    echo "CUDA available: Yes"
    nvidia-smi --query-gpu=name --format=csv,noheader
else
    echo "CUDA available: No"
fi
EOF

chmod +x hello_ml.sh
./hello_ml.sh
```

**Script Structure Best Practices**:
```bash
cat > script_template.sh << 'EOF'
#!/bin/bash
###############################################################################
# Script Name: script_template.sh
# Description: Template for ML automation scripts
# Author: Your Name
# Date: 2024-10-18
# Version: 1.0
###############################################################################

set -euo pipefail  # Exit on error, undefined variables, pipe failures

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly LOG_FILE="/var/log/${SCRIPT_NAME%.sh}.log"

# Global variables
DEBUG=false
VERBOSE=false

###############################################################################
# Functions
###############################################################################

# Print usage information
usage() {
    cat << USAGE
Usage: $SCRIPT_NAME [OPTIONS]

Description:
    Brief description of what the script does

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -d, --debug     Enable debug mode

Examples:
    $SCRIPT_NAME --verbose
    $SCRIPT_NAME --debug

USAGE
    exit 1
}

# Log message to file and optionally to stdout
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Log info message
log_info() {
    log "INFO" "$@"
}

# Log error message
log_error() {
    log "ERROR" "$@" >&2
}

# Log debug message
log_debug() {
    if [ "$DEBUG" = true ]; then
        log "DEBUG" "$@"
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Cleanup function (called on exit)
cleanup() {
    log_info "Cleaning up..."
    # Add cleanup tasks here
}

# Error handler
error_handler() {
    local line_no=$1
    log_error "Script failed at line $line_no"
    cleanup
    exit 1
}

###############################################################################
# Main Script
###############################################################################

# Set up error handling
trap 'error_handler ${LINENO}' ERR
trap cleanup EXIT

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Main logic starts here
log_info "Script started"

# Your code here

log_info "Script completed successfully"
EOF

chmod +x script_template.sh
cat script_template.sh
```

### Step 2: Variables and Data Types

```bash
cd ~/ml-scripting-lab

cat > variables_demo.sh << 'EOF'
#!/bin/bash
# Demonstrate variables in bash

# String variables
MODEL_NAME="resnet50"
VERSION="1.2.3"
AUTHOR="ML Team"

echo "Model: $MODEL_NAME"
echo "Version: $VERSION"
echo "Author: $AUTHOR"

# Numeric variables
EPOCHS=100
BATCH_SIZE=32
LEARNING_RATE=0.001

echo "Training for $EPOCHS epochs with batch size $BATCH_SIZE"

# Arrays
MODELS=("resnet50" "vgg16" "inception_v3" "mobilenet")
echo "Available models: ${MODELS[@]}"
echo "First model: ${MODELS[0]}"
echo "Number of models: ${#MODELS[@]}"

# Loop through array
echo "All models:"
for model in "${MODELS[@]}"; do
    echo "  - $model"
done

# Associative arrays (dictionaries)
declare -A MODEL_CONFIGS
MODEL_CONFIGS["resnet50"]="config/resnet50.yaml"
MODEL_CONFIGS["vgg16"]="config/vgg16.yaml"
MODEL_CONFIGS["inception_v3"]="config/inception_v3.yaml"

echo ""
echo "Model configurations:"
for model in "${!MODEL_CONFIGS[@]}"; do
    echo "  $model: ${MODEL_CONFIGS[$model]}"
done

# Command substitution
CURRENT_DATE=$(date +%Y-%m-%d)
HOSTNAME=$(hostname)
USER_COUNT=$(who | wc -l)

echo ""
echo "System info:"
echo "  Date: $CURRENT_DATE"
echo "  Host: $HOSTNAME"
echo "  Active users: $USER_COUNT"

# Environment variables
export ML_PROJECT_ROOT="$HOME/ml-projects"
export MODEL_REGISTRY="$ML_PROJECT_ROOT/models"
export DATA_DIR="$ML_PROJECT_ROOT/data"

echo ""
echo "Environment:"
echo "  ML_PROJECT_ROOT: $ML_PROJECT_ROOT"
echo "  MODEL_REGISTRY: $MODEL_REGISTRY"
echo "  DATA_DIR: $DATA_DIR"

# String manipulation
FULL_MODEL_NAME="${MODEL_NAME}_v${VERSION}"
echo ""
echo "Full model name: $FULL_MODEL_NAME"

# String length
echo "Length of model name: ${#MODEL_NAME}"

# Substring
echo "First 3 characters: ${MODEL_NAME:0:3}"

# String replacement
CONFIG_FILE="model.yaml.template"
FINAL_CONFIG="${CONFIG_FILE/.template/}"
echo "Final config: $FINAL_CONFIG"
EOF

chmod +x variables_demo.sh
./variables_demo.sh
```

### Step 3: Control Structures

```bash
cd ~/ml-scripting-lab

cat > control_structures.sh << 'EOF'
#!/bin/bash
# Demonstrate control structures

# If-else statements
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU detected"
        GPU_COUNT=$(nvidia-smi --query-gpu=name --format=csv,noheader | wc -l)
        echo "Number of GPUs: $GPU_COUNT"

        if [ $GPU_COUNT -gt 1 ]; then
            echo "Multi-GPU system detected"
        elif [ $GPU_COUNT -eq 1 ]; then
            echo "Single GPU system"
        fi
    else
        echo "No GPU detected - using CPU"
    fi
}

# Case statement
select_training_mode() {
    local mode=$1

    case $mode in
        "single-gpu")
            echo "Training on single GPU"
            ;;
        "multi-gpu")
            echo "Distributed training on multiple GPUs"
            ;;
        "cpu")
            echo "Training on CPU"
            ;;
        "tpu")
            echo "Training on TPU"
            ;;
        *)
            echo "Unknown training mode: $mode"
            return 1
            ;;
    esac
}

# For loops
echo "=== Testing different models ==="
MODELS=("resnet50" "vgg16" "mobilenet")
for model in "${MODELS[@]}"; do
    echo "Testing $model..."
    # Simulate testing
    sleep 1
    echo "$model: PASSED"
done

echo ""
echo "=== Processing datasets ==="
for i in {1..5}; do
    echo "Processing dataset $i/5"
    sleep 0.5
done

echo ""
echo "=== C-style for loop ==="
for ((epoch=1; epoch<=10; epoch++)); do
    accuracy=$(echo "scale=4; 1 - (1/$epoch)" | bc)
    echo "Epoch $epoch: accuracy=$accuracy"
done

# While loop
echo ""
echo "=== Waiting for model to be ready ==="
COUNTER=0
MAX_WAIT=5
while [ $COUNTER -lt $MAX_WAIT ]; do
    echo "Waiting... ($COUNTER/$MAX_WAIT)"
    sleep 1
    ((COUNTER++))
done
echo "Model ready!"

# Until loop
echo ""
echo "=== Training until convergence ==="
LOSS=10.0
ITERATION=0
until (( $(echo "$LOSS < 0.1" | bc -l) )); do
    ((ITERATION++))
    LOSS=$(echo "scale=2; $LOSS * 0.7" | bc)
    echo "Iteration $ITERATION: loss=$LOSS"
done
echo "Converged!"

# Run examples
echo ""
echo "=== GPU Check ==="
check_gpu

echo ""
echo "=== Training Mode Selection ==="
select_training_mode "single-gpu"
select_training_mode "multi-gpu"
select_training_mode "invalid"
EOF

chmod +x control_structures.sh
./control_structures.sh
```

## Part 2: Practical ML Deployment Scripts

### Step 4: Model Deployment Script

```bash
cd ~/ml-scripting-lab
mkdir deployment
cd deployment

cat > deploy_model.sh << 'EOF'
#!/bin/bash
###############################################################################
# Script Name: deploy_model.sh
# Description: Deploy ML model to production
# Usage: ./deploy_model.sh <model_path> <environment>
###############################################################################

set -euo pipefail

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_DIR="$SCRIPT_DIR/logs"
readonly BACKUP_DIR="$SCRIPT_DIR/backups"
readonly STAGING_DIR="$SCRIPT_DIR/staging"
readonly PRODUCTION_DIR="$SCRIPT_DIR/production"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$BACKUP_DIR" "$STAGING_DIR" "$PRODUCTION_DIR"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/deployment.log"
}

error_exit() {
    log "ERROR: $1"
    exit 1
}

# Validate model file
validate_model() {
    local model_path=$1

    log "Validating model: $model_path"

    # Check if file exists
    [ -f "$model_path" ] || error_exit "Model file not found: $model_path"

    # Check file size (should be > 1MB for real models)
    local size=$(stat -f%z "$model_path" 2>/dev/null || stat -c%s "$model_path" 2>/dev/null)
    [ $size -gt 1048576 ] || log "WARNING: Model file is small ($size bytes)"

    # Check file extension
    case "$model_path" in
        *.h5|*.pb|*.pth|*.onnx|*.pkl)
            log "Valid model format detected"
            ;;
        *)
            log "WARNING: Unusual model file extension"
            ;;
    esac

    log "Model validation passed"
    return 0
}

# Backup existing model
backup_current_model() {
    local env=$1

    if [ "$env" = "production" ]; then
        local prod_model="$PRODUCTION_DIR/current_model"

        if [ -f "$prod_model" ]; then
            local backup_name="model_backup_$(date +%Y%m%d_%H%M%S)"
            log "Backing up current production model to $backup_name"
            cp "$prod_model" "$BACKUP_DIR/$backup_name"
            log "Backup completed"
        else
            log "No existing production model to backup"
        fi
    fi
}

# Deploy to staging
deploy_to_staging() {
    local model_path=$1

    log "Deploying to staging environment"

    cp "$model_path" "$STAGING_DIR/current_model"
    chmod 644 "$STAGING_DIR/current_model"

    log "Model deployed to staging"
}

# Run validation tests
run_validation_tests() {
    log "Running validation tests..."

    # Simulate model validation
    log "  - Checking model integrity"
    sleep 1

    log "  - Running inference test"
    sleep 1

    log "  - Performance benchmarking"
    sleep 1

    log "All validation tests passed"
    return 0
}

# Promote to production
promote_to_production() {
    log "Promoting model to production"

    cp "$STAGING_DIR/current_model" "$PRODUCTION_DIR/current_model"
    chmod 444 "$PRODUCTION_DIR/current_model"  # Read-only

    # Create version metadata
    cat > "$PRODUCTION_DIR/metadata.json" << METADATA
{
    "deployed_at": "$(date -Iseconds)",
    "deployed_by": "$(whoami)",
    "hostname": "$(hostname)",
    "version": "$(date +%Y%m%d_%H%M%S)"
}
METADATA

    log "Model promoted to production"
}

# Rollback to previous version
rollback() {
    log "Rolling back to previous version"

    local latest_backup=$(ls -t "$BACKUP_DIR" | head -1)

    if [ -z "$latest_backup" ]; then
        error_exit "No backup available for rollback"
    fi

    log "Restoring from backup: $latest_backup"
    cp "$BACKUP_DIR/$latest_backup" "$PRODUCTION_DIR/current_model"

    log "Rollback completed"
}

# Send deployment notification
send_notification() {
    local status=$1
    local env=$2

    log "Sending deployment notification"

    # In production, this would send to Slack, email, etc.
    cat > "$LOG_DIR/notification.txt" << NOTIFICATION
Deployment Notification
=======================
Status: $status
Environment: $env
Time: $(date)
User: $(whoami)
Host: $(hostname)
NOTIFICATION

    log "Notification sent (simulated)"
}

# Main deployment workflow
deploy() {
    local model_path=$1
    local environment=$2

    log "========================================"
    log "Starting deployment workflow"
    log "Model: $model_path"
    log "Environment: $environment"
    log "========================================"

    # Validation
    validate_model "$model_path"

    # Backup current model
    backup_current_model "$environment"

    # Deploy to staging first
    deploy_to_staging "$model_path"

    # Run tests
    run_validation_tests || {
        error_exit "Validation tests failed"
    }

    # Deploy to production if requested
    if [ "$environment" = "production" ]; then
        log "Promoting to production..."
        promote_to_production
        send_notification "SUCCESS" "production"
    else
        send_notification "SUCCESS" "staging"
    fi

    log "========================================"
    log "Deployment completed successfully"
    log "========================================"
}

# Usage information
usage() {
    cat << USAGE
Usage: $0 <model_path> <environment>

Deploy ML model to specified environment

Arguments:
    model_path      Path to model file (.h5, .pb, .pth, etc.)
    environment     Target environment (staging or production)

Examples:
    $0 model.h5 staging
    $0 /path/to/model.pth production

Commands:
    rollback        Rollback to previous production version

USAGE
    exit 1
}

# Main script entry point
main() {
    # Check arguments
    if [ $# -eq 0 ]; then
        usage
    fi

    # Handle special commands
    if [ "$1" = "rollback" ]; then
        rollback
        exit 0
    fi

    # Require 2 arguments for deployment
    if [ $# -ne 2 ]; then
        usage
    fi

    local model_path=$1
    local environment=$2

    # Validate environment
    if [[ ! "$environment" =~ ^(staging|production)$ ]]; then
        error_exit "Invalid environment. Must be 'staging' or 'production'"
    fi

    # Execute deployment
    deploy "$model_path" "$environment"
}

# Run main function
main "$@"
EOF

chmod +x deploy_model.sh

# Test the deployment script
touch test_model.h5
dd if=/dev/zero of=test_model.h5 bs=1M count=10 2>/dev/null
./deploy_model.sh test_model.h5 staging
cat logs/deployment.log
```

### Step 5: Data Pipeline Automation

```bash
cd ~/ml-scripting-lab
mkdir data_pipeline
cd data_pipeline

cat > process_data.sh << 'EOF'
#!/bin/bash
###############################################################################
# Script Name: process_data.sh
# Description: Automated data processing pipeline for ML
# Usage: ./process_data.sh [options]
###############################################################################

set -euo pipefail

# Configuration
readonly DATA_RAW="data/raw"
readonly DATA_PROCESSED="data/processed"
readonly DATA_VALIDATED="data/validated"
readonly LOG_DIR="logs"

mkdir -p "$DATA_RAW" "$DATA_PROCESSED" "$DATA_VALIDATED" "$LOG_DIR"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_DIR/pipeline.log"
}

# Download data (simulated)
download_data() {
    log "Downloading raw data..."

    # Simulate downloading multiple files
    for i in {1..5}; do
        local filename="dataset_$(date +%Y%m%d)_part${i}.csv"
        log "  Downloading $filename"

        # Create dummy data
        cat > "$DATA_RAW/$filename" << DATA
id,feature1,feature2,label
1,0.5,0.8,0
2,0.3,0.6,1
3,0.7,0.4,0
4,0.2,0.9,1
5,0.6,0.5,0
DATA

        sleep 1
    done

    log "Download completed"
}

# Validate data quality
validate_data() {
    log "Validating data quality..."

    local error_count=0

    for file in "$DATA_RAW"/*.csv; do
        [ -f "$file" ] || continue

        local filename=$(basename "$file")
        log "  Validating $filename"

        # Check file size
        local size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        if [ $size -eq 0 ]; then
            log "    ERROR: Empty file"
            ((error_count++))
            continue
        fi

        # Check header
        local header=$(head -1 "$file")
        if [[ ! "$header" =~ ^id,.*label$ ]]; then
            log "    WARNING: Unexpected header format"
        fi

        # Check row count
        local row_count=$(($(wc -l < "$file") - 1))
        log "    Rows: $row_count"

        if [ $row_count -lt 1 ]; then
            log "    ERROR: No data rows"
            ((error_count++))
        fi
    done

    if [ $error_count -gt 0 ]; then
        log "Validation failed with $error_count errors"
        return 1
    fi

    log "Validation passed"
    return 0
}

# Clean and preprocess data
preprocess_data() {
    log "Preprocessing data..."

    for file in "$DATA_RAW"/*.csv; do
        [ -f "$file" ] || continue

        local filename=$(basename "$file")
        local output="$DATA_PROCESSED/$filename"

        log "  Processing $filename"

        # Remove duplicates, sort, etc. (simulated with simple copy)
        # In reality, this would use awk, sed, or call Python script
        grep -v '^$' "$file" | sort -u > "$output"

        log "    Output: $output"
    done

    log "Preprocessing completed"
}

# Merge datasets
merge_datasets() {
    log "Merging datasets..."

    local merged_file="$DATA_PROCESSED/merged_dataset.csv"

    # Write header
    head -1 "$DATA_PROCESSED/dataset_$(date +%Y%m%d)_part1.csv" > "$merged_file"

    # Append all data (skip headers)
    for file in "$DATA_PROCESSED"/dataset_*.csv; do
        [ -f "$file" ] || continue
        tail -n +2 "$file" >> "$merged_file"
    done

    local total_rows=$(($(wc -l < "$merged_file") - 1))
    log "Merged dataset created with $total_rows rows"
    log "Output: $merged_file"
}

# Split into train/val/test
split_dataset() {
    log "Splitting dataset into train/val/test..."

    local input="$DATA_PROCESSED/merged_dataset.csv"
    local header=$(head -1 "$input")

    # Get total rows (excluding header)
    local total=$(($(wc -l < "$input") - 1))

    # Calculate splits (70% train, 15% val, 15% test)
    local train_rows=$((total * 70 / 100))
    local val_rows=$((total * 15 / 100))

    log "  Total rows: $total"
    log "  Train: $train_rows"
    log "  Val: $val_rows"
    log "  Test: $((total - train_rows - val_rows))"

    # Create train set
    {
        echo "$header"
        tail -n +2 "$input" | head -$train_rows
    } > "$DATA_PROCESSED/train.csv"

    # Create val set
    {
        echo "$header"
        tail -n +2 "$input" | tail -n +$((train_rows + 1)) | head -$val_rows
    } > "$DATA_PROCESSED/val.csv"

    # Create test set
    {
        echo "$header"
        tail -n +2 "$input" | tail -n +$((train_rows + val_rows + 1))
    } > "$DATA_PROCESSED/test.csv"

    log "Dataset split completed"
}

# Generate statistics
generate_stats() {
    log "Generating statistics..."

    local stats_file="$DATA_PROCESSED/statistics.txt"

    {
        echo "Data Processing Statistics"
        echo "=========================="
        echo "Generated: $(date)"
        echo ""

        for dataset in train val test; do
            local file="$DATA_PROCESSED/$dataset.csv"
            if [ -f "$file" ]; then
                local rows=$(($(wc -l < "$file") - 1))
                local size=$(du -h "$file" | cut -f1)
                echo "$dataset:"
                echo "  Rows: $rows"
                echo "  Size: $size"
                echo ""
            fi
        done
    } > "$stats_file"

    cat "$stats_file"
    log "Statistics saved to $stats_file"
}

# Cleanup old data
cleanup_old_data() {
    local days=${1:-7}

    log "Cleaning up data older than $days days..."

    # Find and remove old files
    local count=0
    while IFS= read -r file; do
        log "  Removing: $file"
        rm "$file"
        ((count++))
    done < <(find "$DATA_RAW" -type f -mtime +$days)

    log "Removed $count old files"
}

# Main pipeline
run_pipeline() {
    log "========================================"
    log "Starting data processing pipeline"
    log "========================================"

    download_data

    validate_data || {
        log "ERROR: Validation failed, aborting pipeline"
        exit 1
    }

    preprocess_data
    merge_datasets
    split_dataset
    generate_stats

    log "========================================"
    log "Pipeline completed successfully"
    log "========================================"
}

# Usage
usage() {
    cat << USAGE
Usage: $0 [command]

Data processing pipeline for ML

Commands:
    run         Run full pipeline (default)
    download    Download data only
    validate    Validate data only
    process     Process data only
    stats       Generate statistics
    cleanup     Clean up old data

Examples:
    $0 run
    $0 validate
    $0 cleanup

USAGE
    exit 1
}

# Main
main() {
    local command=${1:-run}

    case $command in
        run)
            run_pipeline
            ;;
        download)
            download_data
            ;;
        validate)
            validate_data
            ;;
        process)
            preprocess_data
            merge_datasets
            split_dataset
            ;;
        stats)
            generate_stats
            ;;
        cleanup)
            cleanup_old_data
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
EOF

chmod +x process_data.sh
./process_data.sh run
```

### Step 6: System Monitoring Script

```bash
cd ~/ml-scripting-lab
mkdir monitoring
cd monitoring

cat > monitor_system.sh << 'EOF'
#!/bin/bash
###############################################################################
# Script Name: monitor_system.sh
# Description: Monitor system resources and ML training jobs
# Usage: ./monitor_system.sh [interval]
###############################################################################

set -euo pipefail

# Configuration
readonly LOG_DIR="logs"
readonly ALERT_FILE="$LOG_DIR/alerts.log"
readonly METRICS_FILE="$LOG_DIR/metrics.csv"

mkdir -p "$LOG_DIR"

# Thresholds
readonly CPU_THRESHOLD=80
readonly MEM_THRESHOLD=85
readonly DISK_THRESHOLD=90
readonly GPU_THRESHOLD=90

# Initialize metrics file
init_metrics() {
    if [ ! -f "$METRICS_FILE" ]; then
        echo "timestamp,cpu_usage,mem_usage,disk_usage,gpu_usage" > "$METRICS_FILE"
    fi
}

# Log alert
alert() {
    local level=$1
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" >> "$ALERT_FILE"
    echo "ALERT [$level]: $*"
}

# Check CPU usage
check_cpu() {
    # Get CPU usage (100 - idle)
    local cpu_idle=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d'%' -f1)
    local cpu_usage=$(echo "100 - $cpu_idle" | bc)

    echo "$cpu_usage"

    if (( $(echo "$cpu_usage > $CPU_THRESHOLD" | bc -l) )); then
        alert "WARNING" "High CPU usage: ${cpu_usage}%"
    fi
}

# Check memory usage
check_memory() {
    local mem_total=$(free | grep Mem | awk '{print $2}')
    local mem_used=$(free | grep Mem | awk '{print $3}')
    local mem_usage=$(echo "scale=2; ($mem_used / $mem_total) * 100" | bc)

    echo "$mem_usage"

    if (( $(echo "$mem_usage > $MEM_THRESHOLD" | bc -l) )); then
        alert "WARNING" "High memory usage: ${mem_usage}%"
    fi
}

# Check disk usage
check_disk() {
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)

    echo "$disk_usage"

    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        alert "CRITICAL" "High disk usage: ${disk_usage}%"
    fi
}

# Check GPU usage
check_gpu() {
    if ! command -v nvidia-smi &> /dev/null; then
        echo "N/A"
        return
    fi

    local gpu_usage=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)

    echo "$gpu_usage"

    if [ "$gpu_usage" -gt "$GPU_THRESHOLD" ]; then
        alert "INFO" "High GPU usage: ${gpu_usage}%"
    fi
}

# Check training processes
check_training_processes() {
    echo ""
    echo "Training Processes:"
    echo "==================="

    local count=0
    while IFS= read -r pid; do
        local cmd=$(ps -p "$pid" -o cmd --no-headers)
        local cpu=$(ps -p "$pid" -o %cpu --no-headers)
        local mem=$(ps -p "$pid" -o %mem --no-headers)

        echo "PID $pid: $cmd"
        echo "  CPU: ${cpu}%  MEM: ${mem}%"
        ((count++))
    done < <(pgrep -f "train\.py|train_|python.*train" 2>/dev/null || true)

    if [ $count -eq 0 ]; then
        echo "No training processes found"
    fi
}

# Collect metrics
collect_metrics() {
    local cpu=$(check_cpu)
    local mem=$(check_memory)
    local disk=$(check_disk)
    local gpu=$(check_gpu)
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log to CSV
    echo "$timestamp,$cpu,$mem,$disk,$gpu" >> "$METRICS_FILE"
}

# Display dashboard
display_dashboard() {
    clear
    echo "========================================"
    echo "    ML System Monitoring Dashboard"
    echo "========================================"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""

    echo "System Resources:"
    echo "-----------------"

    local cpu=$(check_cpu)
    printf "CPU Usage:    %6.2f%%\n" "$cpu"

    local mem=$(check_memory)
    printf "Memory Usage: %6.2f%%\n" "$mem"

    local disk=$(check_disk)
    printf "Disk Usage:   %6s%%\n" "$disk"

    local gpu=$(check_gpu)
    if [ "$gpu" != "N/A" ]; then
        printf "GPU Usage:    %6s%%\n" "$gpu"
    fi

    check_training_processes

    echo ""
    echo "Recent Alerts:"
    echo "--------------"
    if [ -f "$ALERT_FILE" ]; then
        tail -5 "$ALERT_FILE" 2>/dev/null || echo "No alerts"
    else
        echo "No alerts"
    fi

    echo ""
    echo "========================================"
    echo "Press Ctrl+C to stop monitoring"
}

# Continuous monitoring
monitor_continuous() {
    local interval=${1:-5}

    echo "Starting continuous monitoring (interval: ${interval}s)"

    init_metrics

    while true; do
        display_dashboard
        collect_metrics
        sleep "$interval"
    done
}

# Generate report
generate_report() {
    local report_file="$LOG_DIR/report_$(date +%Y%m%d_%H%M%S).txt"

    {
        echo "System Monitoring Report"
        echo "========================"
        echo "Generated: $(date)"
        echo ""

        echo "Current Status:"
        echo "---------------"
        echo "CPU Usage: $(check_cpu)%"
        echo "Memory Usage: $(check_memory)%"
        echo "Disk Usage: $(check_disk)%"
        echo "GPU Usage: $(check_gpu)%"

        echo ""
        echo "Recent Metrics (last 10 samples):"
        echo "----------------------------------"
        tail -10 "$METRICS_FILE"

        echo ""
        echo "Recent Alerts:"
        echo "--------------"
        tail -20 "$ALERT_FILE" 2>/dev/null || echo "No alerts"

    } > "$report_file"

    cat "$report_file"
    echo ""
    echo "Report saved to: $report_file"
}

# Usage
usage() {
    cat << USAGE
Usage: $0 [command] [options]

System monitoring for ML infrastructure

Commands:
    monitor [interval]  Start continuous monitoring (default: 5s)
    check               Single check of all resources
    report              Generate monitoring report
    alerts              Show recent alerts

Examples:
    $0 monitor          Monitor with 5s interval
    $0 monitor 10       Monitor with 10s interval
    $0 check            One-time check
    $0 report           Generate report

USAGE
    exit 1
}

# Main
main() {
    local command=${1:-monitor}
    shift || true

    case $command in
        monitor)
            monitor_continuous "$@"
            ;;
        check)
            display_dashboard
            collect_metrics
            ;;
        report)
            generate_report
            ;;
        alerts)
            tail -20 "$ALERT_FILE" 2>/dev/null || echo "No alerts"
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
EOF

chmod +x monitor_system.sh

# Run a single check
./monitor_system.sh check
```

### Step 7: Backup and Restore Script

```bash
cd ~/ml-scripting-lab
mkdir backup_restore
cd backup_restore

cat > backup_ml_project.sh << 'EOF'
#!/bin/bash
###############################################################################
# Script Name: backup_ml_project.sh
# Description: Backup and restore ML projects
# Usage: ./backup_ml_project.sh [backup|restore|list]
###############################################################################

set -euo pipefail

# Configuration
readonly BACKUP_ROOT="$HOME/ml-backups"
readonly PROJECT_ROOT="${ML_PROJECT_ROOT:-$HOME/ml-projects}"
readonly LOG_FILE="$BACKUP_ROOT/backup.log"

mkdir -p "$BACKUP_ROOT"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Create backup
create_backup() {
    local project_name=${1:-}

    if [ -z "$project_name" ]; then
        log "ERROR: Project name required"
        return 1
    fi

    local project_path="$PROJECT_ROOT/$project_name"

    if [ ! -d "$project_path" ]; then
        log "ERROR: Project not found: $project_path"
        return 1
    fi

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_name="${project_name}_${timestamp}.tar.gz"
    local backup_path="$BACKUP_ROOT/$backup_name"

    log "Creating backup: $backup_name"
    log "Source: $project_path"

    # Create compressed backup (excluding large files)
    tar -czf "$backup_path" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.ipynb_checkpoints' \
        --exclude='data/raw/*' \
        --exclude='models/checkpoints/*' \
        --exclude='.git' \
        -C "$PROJECT_ROOT" \
        "$project_name"

    local backup_size=$(du -h "$backup_path" | cut -f1)
    log "Backup created: $backup_path ($backup_size)"

    # Create metadata
    cat > "$backup_path.meta" << META
{
    "project": "$project_name",
    "timestamp": "$timestamp",
    "source": "$project_path",
    "size": "$backup_size",
    "created_by": "$(whoami)",
    "hostname": "$(hostname)"
}
META

    # Keep only last 5 backups per project
    cleanup_old_backups "$project_name"

    log "Backup completed successfully"
}

# Cleanup old backups
cleanup_old_backups() {
    local project_name=$1
    local keep_count=5

    log "Cleaning up old backups for $project_name (keeping last $keep_count)"

    local count=0
    while IFS= read -r backup; do
        ((count++))
        if [ $count -gt $keep_count ]; then
            log "  Removing old backup: $(basename "$backup")"
            rm -f "$backup" "$backup.meta"
        fi
    done < <(ls -t "$BACKUP_ROOT/${project_name}"_*.tar.gz 2>/dev/null || true)
}

# List backups
list_backups() {
    local project_name=${1:-}

    echo "Available Backups:"
    echo "=================="

    if [ -n "$project_name" ]; then
        local pattern="${project_name}_*.tar.gz"
    else
        local pattern="*.tar.gz"
    fi

    local found=0
    while IFS= read -r backup; do
        found=1
        local name=$(basename "$backup")
        local size=$(du -h "$backup" | cut -f1)
        local date=$(stat -c%y "$backup" 2>/dev/null | cut -d' ' -f1 || \
                     stat -f%Sm -t '%Y-%m-%d' "$backup" 2>/dev/null)

        echo "$name"
        echo "  Size: $size"
        echo "  Date: $date"

        if [ -f "$backup.meta" ]; then
            echo "  Metadata: $(cat "$backup.meta")"
        fi
        echo ""
    done < <(ls -t "$BACKUP_ROOT"/$pattern 2>/dev/null || true)

    if [ $found -eq 0 ]; then
        echo "No backups found"
    fi
}

# Restore backup
restore_backup() {
    local backup_name=$1
    local restore_path=${2:-$PROJECT_ROOT}

    local backup_path="$BACKUP_ROOT/$backup_name"

    if [ ! -f "$backup_path" ]; then
        log "ERROR: Backup not found: $backup_path"
        return 1
    fi

    log "Restoring backup: $backup_name"
    log "Destination: $restore_path"

    # Extract project name from backup
    local project_name=$(echo "$backup_name" | sed 's/_[0-9]\{8\}_[0-9]\{6\}\.tar\.gz$//')

    # Check if project already exists
    if [ -d "$restore_path/$project_name" ]; then
        log "WARNING: Project already exists at $restore_path/$project_name"
        read -p "Overwrite? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            log "Restore cancelled"
            return 1
        fi

        # Backup existing project before overwriting
        log "Creating safety backup of existing project"
        mv "$restore_path/$project_name" "$restore_path/${project_name}.bak.$(date +%s)"
    fi

    # Extract backup
    log "Extracting backup..."
    tar -xzf "$backup_path" -C "$restore_path"

    log "Restore completed successfully"
    log "Project restored to: $restore_path/$project_name"
}

# Verify backup integrity
verify_backup() {
    local backup_name=$1
    local backup_path="$BACKUP_ROOT/$backup_name"

    log "Verifying backup: $backup_name"

    # Test archive integrity
    if tar -tzf "$backup_path" > /dev/null 2>&1; then
        log "Backup integrity: OK"
        return 0
    else
        log "ERROR: Backup is corrupted"
        return 1
    fi
}

# Usage
usage() {
    cat << USAGE
Usage: $0 <command> [options]

Backup and restore ML projects

Commands:
    backup <project>           Create backup of project
    restore <backup> [path]    Restore backup
    list [project]             List available backups
    verify <backup>            Verify backup integrity

Examples:
    $0 backup my-ml-project
    $0 list
    $0 list my-ml-project
    $0 restore my-ml-project_20241018_120000.tar.gz
    $0 verify my-ml-project_20241018_120000.tar.gz

USAGE
    exit 1
}

# Main
main() {
    if [ $# -eq 0 ]; then
        usage
    fi

    local command=$1
    shift

    case $command in
        backup)
            create_backup "$@"
            ;;
        restore)
            restore_backup "$@"
            ;;
        list)
            list_backups "$@"
            ;;
        verify)
            verify_backup "$@"
            ;;
        *)
            usage
            ;;
    esac
}

main "$@"
EOF

chmod +x backup_ml_project.sh

# Test backup functionality
mkdir -p ~/ml-projects/test-project
echo "Test content" > ~/ml-projects/test-project/README.md
./backup_ml_project.sh backup test-project
./backup_ml_project.sh list
```

## Validation

```bash
cd ~/ml-scripting-lab

cat > validate_exercise.sh << 'EOF'
#!/bin/bash

echo "=== Exercise 04 Validation ==="
echo ""

PASS=0
FAIL=0

# Check directories
for dir in deployment data_pipeline monitoring backup_restore; do
    if [ -d "$dir" ]; then
        echo "✓ Directory: $dir"
        ((PASS++))
    else
        echo "✗ Missing: $dir"
        ((FAIL++))
    fi
done

# Check scripts
scripts=(
    "deployment/deploy_model.sh"
    "data_pipeline/process_data.sh"
    "monitoring/monitor_system.sh"
    "backup_restore/backup_ml_project.sh"
)

for script in "${scripts[@]}"; do
    if [ -x "$script" ]; then
        echo "✓ Script executable: $script"
        ((PASS++))
    else
        echo "✗ Not executable: $script"
        ((FAIL++))
    fi
done

echo ""
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -eq 0 ]; then
    echo "✓ All validations passed!"
else
    echo "✗ Some validations failed"
fi
EOF

chmod +x validate_exercise.sh
./validate_exercise.sh
```

## Troubleshooting

**Problem**: Script has syntax errors
- **Solution**: Check with `bash -n script.sh`
- Use ShellCheck: `shellcheck script.sh`

**Problem**: Permission denied
- **Solution**: Make executable: `chmod +x script.sh`

**Problem**: Variable not found
- **Solution**: Check variable definition and scope
- Use `set -u` to catch undefined variables

**Problem**: Command not found in script
- **Solution**: Use full paths or check PATH
- Test: `command -v command_name`

## Reflection Questions

1. Why use `set -euo pipefail` at the start of scripts?
2. When should you use functions vs inline code?
3. How do you handle errors gracefully in bash scripts?
4. What's the benefit of logging to files?
5. How can you make scripts more maintainable?

## Next Steps

- **Exercise 05**: Package Management
- **Exercise 06**: Log Analysis
- **Lecture 05**: Advanced Shell Scripting

## Additional Resources

- Bash Guide: https://mywiki.wooledge.org/BashGuide
- ShellCheck: https://www.shellcheck.net/
- Advanced Bash-Scripting Guide: https://tldp.org/LDP/abs/html/

---

**Congratulations!** You've mastered bash scripting for ML deployment automation!
