# Lecture 04: Shell Scripting for Automation

## Table of Contents
1. [Introduction](#introduction)
2. [Bash Script Basics](#bash-script-basics)
3. [Variables and Data Types](#variables-and-data-types)
4. [Control Structures](#control-structures)
5. [Functions](#functions)
6. [Command-Line Arguments](#command-line-arguments)
7. [Error Handling and Debugging](#error-handling-and-debugging)
8. [Practical Automation Scripts](#practical-automation-scripts)
9. [Best Practices](#best-practices)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Shell scripting is the AI infrastructure engineer's superpower. Automate deployment, monitor training jobs, manage datasets, provision environments, and orchestrate complex workflows—all with Bash scripts.

This lecture teaches you to write robust, maintainable shell scripts for AI infrastructure automation.

### Learning Objectives

By the end of this lecture, you will:
- Write and execute Bash scripts
- Use variables, arrays, and string manipulation
- Implement control structures (if, for, while, case)
- Create reusable functions
- Process command-line arguments
- Handle errors gracefully
- Debug scripts effectively
- Automate common AI infrastructure tasks

### Prerequisites
- Lectures 01-03 (Linux fundamentals, permissions, processes)
- Comfort with command-line basics
- Text editor familiarity (nano, vim, or VS Code)

### Why Shell Scripting for AI Infrastructure?

**Automation**: Deploy models, provision environments, orchestrate training
**Consistency**: Same process every time, no manual errors
**Efficiency**: Automate repetitive tasks, save hours daily
**Integration**: Glue together different tools and services
**Documentation**: Scripts serve as executable documentation

## Bash Script Basics

### Creating Your First Script

```bash
#!/bin/bash
# hello.sh - My first script

echo "Hello, AI Infrastructure!"
echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Date: $(date)"
```

### Shebang (#!)

The first line tells the system which interpreter to use:

```bash
#!/bin/bash              # Use bash
#!/bin/sh                # Use sh (POSIX compatible)
#!/usr/bin/env python3   # Use python3 (finds in PATH)
#!/usr/bin/env bash      # Use bash (portable)
```

**Recommendation**: Use `#!/bin/bash` for bash-specific features, `#!/bin/sh` for POSIX portability.

### Making Scripts Executable

```bash
# Create script
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, World!"
EOF

# Make executable
chmod +x hello.sh

# Run it
./hello.sh
# Hello, World!

# Or run with bash explicitly
bash hello.sh
```

### Script Structure

```bash
#!/bin/bash

#############################################
# Script Name: deploy-model.sh
# Description: Deploy ML model to production
# Author: Alice Johnson
# Date: 2023-10-15
# Version: 1.0
#############################################

# Exit on error
set -e

# Global variables
MODEL_PATH="/models/production"
LOG_FILE="/var/log/deployment.log"

# Functions
function log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

function deploy_model() {
    log_message "Deploying model..."
    # Deployment logic here
}

# Main execution
main() {
    log_message "Starting deployment"
    deploy_model
    log_message "Deployment complete"
}

# Run main function
main "$@"
```

### Comments

```bash
# Single line comment

: '
Multi-line comment
Everything here is ignored
Useful for documentation blocks
'

# Inline comment
echo "Output" # This prints output
```

## Variables and Data Types

### Variable Assignment

```bash
# No spaces around =
NAME="Alice"
AGE=25
MODEL_PATH="/models/resnet50.h5"

# Using variables
echo $NAME
echo "My name is $NAME"
echo "Model: ${MODEL_PATH}"

# Command substitution
CURRENT_DATE=$(date +%Y-%m-%d)
NUM_FILES=$(ls | wc -l)
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)

# Arithmetic
COUNT=5
COUNT=$((COUNT + 1))        # COUNT is now 6
TOTAL=$((5 * 10))           # TOTAL is 50
```

### Variable Naming Conventions

```bash
# Constants (uppercase)
readonly MAX_RETRIES=3
readonly DEFAULT_GPU=0

# Regular variables (lowercase or mixed)
model_name="resnet50"
dataPath="/data/imagenet"

# Environment variables (uppercase)
export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH="/opt/ml-project/src"
```

### String Operations

```bash
# Length
NAME="Alice"
echo ${#NAME}               # 5

# Substring
TEXT="Hello, World!"
echo ${TEXT:0:5}            # Hello
echo ${TEXT:7}              # World!

# Replace
FILENAME="model_v1.h5"
echo ${FILENAME/v1/v2}      # model_v2.h5
echo ${FILENAME/.h5/.pt}    # model_v1.pt

# Replace all occurrences
PATH_STR="/path/to/model"
echo ${PATH_STR//\//\\}     # \path\to\model

# Default values
echo ${VAR:-default}        # Use 'default' if VAR unset
echo ${VAR:=default}        # Set VAR to 'default' if unset

# Uppercase/lowercase (Bash 4+)
NAME="alice"
echo ${NAME^}               # Alice (first letter)
echo ${NAME^^}              # ALICE (all letters)
echo ${NAME,}               # lowercase first
echo ${NAME,,}              # lowercase all
```

### Arrays

```bash
# Declare array
MODELS=("resnet50" "vgg16" "inception")
GPUS=(0 1 2 3)

# Access elements
echo ${MODELS[0]}           # resnet50
echo ${MODELS[1]}           # vgg16
echo ${MODELS[@]}           # All elements
echo ${#MODELS[@]}          # Array length (3)

# Add element
MODELS+=("mobilenet")

# Iterate array
for model in "${MODELS[@]}"; do
    echo "Model: $model"
done

# Array slicing
echo ${MODELS[@]:1:2}       # vgg16 inception (start at 1, take 2)

# Associative arrays (Bash 4+)
declare -A MODEL_PATHS
MODEL_PATHS["resnet50"]="/models/resnet50.h5"
MODEL_PATHS["vgg16"]="/models/vgg16.h5"

echo ${MODEL_PATHS["resnet50"]}    # /models/resnet50.h5

# Iterate associative array
for model in "${!MODEL_PATHS[@]}"; do
    echo "$model -> ${MODEL_PATHS[$model]}"
done
```

### Environment Variables

```bash
# Set environment variable
export MODEL_PATH="/models/production"
export PYTHONPATH="/opt/ml-project/src:$PYTHONPATH"

# Use in script
echo $HOME                  # User home directory
echo $PATH                  # Executable search path
echo $USER                  # Current username
echo $PWD                   # Current directory
echo $HOSTNAME              # System hostname
echo $RANDOM                # Random number

# Common practice: Set defaults
MODEL_PATH=${MODEL_PATH:-/models/default}
GPU_ID=${GPU_ID:-0}
```

## Control Structures

### If Statements

```bash
# Basic if
if [ -f "model.h5" ]; then
    echo "Model file exists"
fi

# If-else
if [ -d "/data/imagenet" ]; then
    echo "Dataset found"
else
    echo "Dataset not found"
    exit 1
fi

# If-elif-else
if [ $GPU_COUNT -eq 0 ]; then
    echo "No GPUs available"
elif [ $GPU_COUNT -eq 1 ]; then
    echo "One GPU available"
else
    echo "$GPU_COUNT GPUs available"
fi

# Multiple conditions (AND)
if [ -f "model.h5" ] && [ -f "config.yaml" ]; then
    echo "Model and config found"
fi

# Multiple conditions (OR)
if [ ! -f "model.h5" ] || [ ! -f "config.yaml" ]; then
    echo "Missing model or config"
fi
```

### Test Operators

**File Tests**:
```bash
[ -e file ]         # Exists
[ -f file ]         # Is regular file
[ -d dir ]          # Is directory
[ -L link ]         # Is symbolic link
[ -r file ]         # Is readable
[ -w file ]         # Is writable
[ -x file ]         # Is executable
[ -s file ]         # File size > 0
[ file1 -nt file2 ] # file1 newer than file2
[ file1 -ot file2 ] # file1 older than file2
```

**String Tests**:
```bash
[ -z "$str" ]       # String is empty
[ -n "$str" ]       # String is not empty
[ "$s1" = "$s2" ]   # Strings are equal
[ "$s1" != "$s2" ]  # Strings are not equal
[[ "$s1" == "$s2" ]]  # Strings match (pattern allowed)
[[ "$s1" =~ regex ]]  # String matches regex
```

**Numeric Tests**:
```bash
[ $a -eq $b ]       # Equal
[ $a -ne $b ]       # Not equal
[ $a -lt $b ]       # Less than
[ $a -le $b ]       # Less than or equal
[ $a -gt $b ]       # Greater than
[ $a -ge $b ]       # Greater than or equal
```

**Advanced with [[ ]]**:
```bash
# Pattern matching
if [[ "$filename" == *.h5 ]]; then
    echo "Keras model file"
fi

# Regex matching
if [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Valid semantic version"
fi

# Logical operators
if [[ -f "model.h5" && -f "weights.h5" ]]; then
    echo "Both files found"
fi
```

### Loops

**For Loop**:
```bash
# Iterate list
for model in resnet50 vgg16 inception; do
    echo "Processing $model"
done

# Iterate array
MODELS=("resnet50" "vgg16" "inception")
for model in "${MODELS[@]}"; do
    python evaluate.py --model "$model"
done

# C-style for loop
for ((i=0; i<10; i++)); do
    echo "Iteration $i"
done

# Iterate files
for file in *.h5; do
    echo "Model file: $file"
done

# Iterate range
for i in {1..5}; do
    echo "Number $i"
done

for i in {0..10..2}; do
    echo "Even number: $i"
done
```

**While Loop**:
```bash
# Basic while
COUNT=0
while [ $COUNT -lt 5 ]; do
    echo "Count: $COUNT"
    COUNT=$((COUNT + 1))
done

# Read file line by line
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt

# Infinite loop
while true; do
    echo "Monitoring..."
    sleep 60
done

# While with process
ps aux | grep python | while read line; do
    echo "Python process: $line"
done
```

**Until Loop**:
```bash
# Run until condition is true
COUNT=0
until [ $COUNT -ge 5 ]; do
    echo "Count: $COUNT"
    COUNT=$((COUNT + 1))
done
```

**Break and Continue**:
```bash
# Break out of loop
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break
    fi
    echo $i
done

# Skip iteration
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue
    fi
    echo $i
done
```

### Case Statements

```bash
# Basic case
ACTION=$1
case "$ACTION" in
    start)
        echo "Starting service..."
        ;;
    stop)
        echo "Stopping service..."
        ;;
    restart)
        echo "Restarting service..."
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

# Pattern matching
case "$filename" in
    *.h5)
        echo "Keras model"
        ;;
    *.pt|*.pth)
        echo "PyTorch model"
        ;;
    *.onnx)
        echo "ONNX model"
        ;;
    *)
        echo "Unknown model format"
        ;;
esac

# Multiple patterns per case
case "$env" in
    dev|development)
        CONFIG="config.dev.yaml"
        ;;
    prod|production)
        CONFIG="config.prod.yaml"
        ;;
    test|testing)
        CONFIG="config.test.yaml"
        ;;
esac
```

## Functions

### Defining Functions

```bash
# Method 1
function greet() {
    echo "Hello, $1!"
}

# Method 2 (POSIX)
greet() {
    echo "Hello, $1!"
}

# Call function
greet "Alice"
# Hello, Alice!
```

### Function Arguments

```bash
function deploy_model() {
    local model_path=$1
    local environment=$2
    local gpu_id=${3:-0}    # Default to 0 if not provided

    echo "Deploying $model_path to $environment on GPU $gpu_id"
}

deploy_model "/models/resnet50.h5" "production" 2
```

### Return Values

```bash
# Return exit code (0-255)
function check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        return 0  # Success
    else
        return 1  # Failure
    fi
}

if check_gpu; then
    echo "GPU available"
else
    echo "No GPU"
fi

# Return string via echo
function get_model_name() {
    local path=$1
    basename "$path" .h5
}

MODEL_NAME=$(get_model_name "/models/resnet50.h5")
echo $MODEL_NAME  # resnet50
```

### Local Variables

```bash
function calculate() {
    local a=$1
    local b=$2
    local result=$((a + b))
    echo $result
}

GLOBAL_VAR="global"

function test_scope() {
    local LOCAL_VAR="local"
    echo "Inside function: $GLOBAL_VAR, $LOCAL_VAR"
}

test_scope
echo "Outside function: $GLOBAL_VAR"
# LOCAL_VAR not accessible here
```

### Practical Functions

```bash
# Logging function
function log() {
    local level=$1
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $@" | tee -a "$LOG_FILE"
}

log INFO "Starting deployment"
log ERROR "Deployment failed"

# Error handling function
function die() {
    log ERROR "$@"
    exit 1
}

# Check if command exists
function command_exists() {
    command -v "$1" &> /dev/null
}

if ! command_exists nvidia-smi; then
    die "nvidia-smi not found. Please install NVIDIA drivers."
fi

# Retry function
function retry() {
    local retries=$1
    shift
    local count=0

    until "$@"; do
        count=$((count + 1))
        if [ $count -ge $retries ]; then
            return 1
        fi
        log WARN "Command failed. Retry $count/$retries..."
        sleep 5
    done
    return 0
}

retry 3 curl -f https://api.example.com/health
```

## Command-Line Arguments

### Positional Parameters

```bash
#!/bin/bash
# script.sh

echo "Script name: $0"
echo "First argument: $1"
echo "Second argument: $2"
echo "All arguments: $@"
echo "Number of arguments: $#"

# Example usage:
# ./script.sh model.h5 config.yaml
# Script name: ./script.sh
# First argument: model.h5
# Second argument: config.yaml
# All arguments: model.h5 config.yaml
# Number of arguments: 2
```

### Shifting Arguments

```bash
#!/bin/bash

while [ $# -gt 0 ]; do
    echo "Processing: $1"
    shift
done

# ./script.sh a b c d
# Processing: a
# Processing: b
# Processing: c
# Processing: d
```

### Parsing Options with getopts

```bash
#!/bin/bash
# train.sh - Training script with options

usage() {
    echo "Usage: $0 [-m MODEL] [-g GPU] [-e EPOCHS] [-h]"
    echo "  -m MODEL    Model architecture (default: resnet50)"
    echo "  -g GPU      GPU ID (default: 0)"
    echo "  -e EPOCHS   Number of epochs (default: 100)"
    echo "  -h          Show this help"
    exit 1
}

# Defaults
MODEL="resnet50"
GPU=0
EPOCHS=100

# Parse options
while getopts "m:g:e:h" opt; do
    case $opt in
        m) MODEL="$OPTARG" ;;
        g) GPU="$OPTARG" ;;
        e) EPOCHS="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Shift past processed options
shift $((OPTIND - 1))

echo "Model: $MODEL"
echo "GPU: $GPU"
echo "Epochs: $EPOCHS"
echo "Remaining args: $@"

# Example usage:
# ./train.sh -m vgg16 -g 2 -e 50 extra_arg
# Model: vgg16
# GPU: 2
# Epochs: 50
# Remaining args: extra_arg
```

### Advanced Argument Parsing

```bash
#!/bin/bash

# Long options with manual parsing
while [ $# -gt 0 ]; do
    case "$1" in
        --model=*)
            MODEL="${1#*=}"
            ;;
        --gpu=*)
            GPU="${1#*=}"
            ;;
        --epochs=*)
            EPOCHS="${1#*=}"
            ;;
        --model|--gpu|--epochs)
            echo "Error: $1 requires a value"
            exit 1
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Usage:
# ./script.sh --model=resnet50 --gpu=2 --epochs=100
```

## Error Handling and Debugging

### Exit Codes

```bash
# Exit with code
exit 0    # Success
exit 1    # General error
exit 2    # Misuse of command

# Check last command exit code
ls /nonexistent
echo $?   # Non-zero (error)

ls /tmp
echo $?   # 0 (success)

# Use in conditionals
if grep -q "pattern" file.txt; then
    echo "Pattern found"
else
    echo "Pattern not found"
fi
```

### Set Options

```bash
#!/bin/bash

# Exit on error
set -e
# Any command that fails will exit the script

# Exit on undefined variable
set -u
# Using undefined variable is an error

# Fail on pipe errors
set -o pipefail
# In pipeline, return code of last failed command

# Debugging mode
set -x
# Print each command before executing

# Combine all
set -euxo pipefail

# Example with set -e
set -e
command1  # If this fails, script exits
command2  # Never reached if command1 failed
command3

# Disable temporarily
set +e
command_that_might_fail
if [ $? -ne 0 ]; then
    echo "Command failed, but continuing"
fi
set -e
```

### Error Handling Patterns

```bash
# Check command success
if ! command; then
    echo "Command failed"
    exit 1
fi

# Logical operators
command1 && command2  # Run command2 only if command1 succeeds
command1 || command2  # Run command2 only if command1 fails

mkdir /tmp/test || die "Failed to create directory"

# Trap errors
function cleanup() {
    echo "Cleaning up..."
    rm -rf /tmp/temp_*
}

trap cleanup EXIT    # Run cleanup on script exit
trap cleanup ERR     # Run cleanup on error

# Comprehensive error handling
function safe_run() {
    local cmd=$1
    if ! eval "$cmd"; then
        log ERROR "Command failed: $cmd"
        return 1
    fi
    return 0
}

safe_run "python train.py" || die "Training failed"
```

### Debugging Techniques

```bash
# Debug output
set -x                # Enable debugging
set +x                # Disable debugging

# Conditional debugging
DEBUG=${DEBUG:-0}
function debug() {
    if [ "$DEBUG" = "1" ]; then
        echo "[DEBUG] $@" >&2
    fi
}

debug "Processing file: $filename"

# Use with:
# DEBUG=1 ./script.sh

# Check syntax without running
bash -n script.sh

# Verbose output
bash -v script.sh

# Trace execution
bash -x script.sh

# Combination
bash -xv script.sh

# Inline debugging
echo "Debug: variable=$variable" >&2
echo "Debug: At line $LINENO" >&2
```

### Input Validation

```bash
function validate_file() {
    local file=$1
    if [ -z "$file" ]; then
        die "File path not provided"
    fi
    if [ ! -f "$file" ]; then
        die "File not found: $file"
    fi
    if [ ! -r "$file" ]; then
        die "File not readable: $file"
    fi
}

validate_file "$MODEL_PATH"

# Numeric validation
function validate_number() {
    local num=$1
    if ! [[ "$num" =~ ^[0-9]+$ ]]; then
        die "Invalid number: $num"
    fi
}

validate_number "$EPOCHS"
```

## Practical Automation Scripts

### Model Deployment Script

```bash
#!/bin/bash
set -euo pipefail

# deploy-model.sh - Deploy ML model to production

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/model-deployment.log"
readonly MODEL_DIR="/models/production"
readonly BACKUP_DIR="/models/backup"

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

function die() {
    log "ERROR: $@"
    exit 1
}

function backup_current_model() {
    log "Backing up current model..."
    if [ -f "$MODEL_DIR/current_model.h5" ]; then
        local backup_name="model_$(date +%Y%m%d_%H%M%S).h5"
        cp "$MODEL_DIR/current_model.h5" "$BACKUP_DIR/$backup_name"
        log "Backup saved: $BACKUP_DIR/$backup_name"
    fi
}

function deploy_model() {
    local new_model=$1

    log "Validating model: $new_model"
    if [ ! -f "$new_model" ]; then
        die "Model file not found: $new_model"
    fi

    backup_current_model

    log "Deploying new model..."
    cp "$new_model" "$MODEL_DIR/current_model.h5"

    log "Restarting inference service..."
    systemctl restart ml-inference || die "Failed to restart service"

    log "Deployment complete!"
}

# Main
if [ $# -ne 1 ]; then
    echo "Usage: $0 <model_path>"
    exit 1
fi

deploy_model "$1"
```

### Training Automation Script

```bash
#!/bin/bash
set -euo pipefail

# train-automation.sh - Automate ML training pipeline

readonly EXPERIMENTS_DIR="/experiments"
readonly DATA_DIR="/data/processed"
readonly LOG_DIR="/logs"

function setup_environment() {
    local exp_name=$1
    local exp_dir="$EXPERIMENTS_DIR/$exp_name"

    mkdir -p "$exp_dir"/{checkpoints,logs,results}
    mkdir -p "$LOG_DIR"

    echo "$exp_dir"
}

function prepare_data() {
    log "Preparing data..."
    if [ ! -d "$DATA_DIR" ]; then
        log "Processing raw data..."
        python scripts/preprocess.py --input /data/raw --output "$DATA_DIR"
    fi
}

function train_model() {
    local exp_name=$1
    local config=$2
    local gpu=$3

    local exp_dir=$(setup_environment "$exp_name")

    log "Starting training: $exp_name"
    log "Config: $config"
    log "GPU: $gpu"

    prepare_data

    CUDA_VISIBLE_DEVICES=$gpu python train.py \
        --config "$config" \
        --output "$exp_dir" \
        --log-file "$exp_dir/logs/training.log" \
        2>&1 | tee "$LOG_DIR/${exp_name}_$(date +%Y%m%d_%H%M%S).log"

    log "Training completed: $exp_name"
}

function evaluate_model() {
    local exp_dir=$1

    log "Evaluating model..."
    python evaluate.py \
        --model "$exp_dir/checkpoints/best_model.h5" \
        --data "$DATA_DIR/test" \
        --output "$exp_dir/results/evaluation.json"
}

# Parse arguments and run
EXPERIMENT_NAME=${1:-"experiment_$(date +%Y%m%d_%H%M%S)"}
CONFIG=${2:-"configs/default.yaml"}
GPU=${3:-0}

train_model "$EXPERIMENT_NAME" "$CONFIG" "$GPU"
evaluate_model "$EXPERIMENTS_DIR/$EXPERIMENT_NAME"
```

### System Health Check Script

```bash
#!/bin/bash

# health-check.sh - Check system resources for ML workloads

readonly WARN_CPU=80
readonly WARN_MEM=85
readonly WARN_DISK=90
readonly WARN_GPU_MEM=85

function check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local cpu_int=${cpu_usage%.*}

    if [ $cpu_int -gt $WARN_CPU ]; then
        echo "WARNING: High CPU usage: ${cpu_usage}%"
        return 1
    fi
    echo "OK: CPU usage: ${cpu_usage}%"
    return 0
}

function check_memory() {
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')

    if [ $mem_usage -gt $WARN_MEM ]; then
        echo "WARNING: High memory usage: ${mem_usage}%"
        return 1
    fi
    echo "OK: Memory usage: ${mem_usage}%"
    return 0
}

function check_disk() {
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ $disk_usage -gt $WARN_DISK ]; then
        echo "WARNING: High disk usage: ${disk_usage}%"
        return 1
    fi
    echo "OK: Disk usage: ${disk_usage}%"
    return 0
}

function check_gpu() {
    if ! command -v nvidia-smi &> /dev/null; then
        echo "SKIP: nvidia-smi not found"
        return 0
    fi

    local gpu_count=$(nvidia-smi --list-gpus | wc -l)
    echo "INFO: Found $gpu_count GPU(s)"

    nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total \
        --format=csv,noheader | while IFS=, read idx name util mem_used mem_total; do
        local mem_pct=$(awk "BEGIN {printf \"%.0f\", ($mem_used/$mem_total)*100}")
        echo "GPU $idx ($name): ${util}% utilization, ${mem_pct}% memory"

        if [ $mem_pct -gt $WARN_GPU_MEM ]; then
            echo "WARNING: High GPU memory usage on GPU $idx"
        fi
    done
}

function main() {
    echo "=== System Health Check $(date) ==="
    echo ""

    local status=0

    check_cpu || status=1
    check_memory || status=1
    check_disk || status=1
    check_gpu || status=1

    echo ""
    if [ $status -eq 0 ]; then
        echo "Overall status: HEALTHY"
    else
        echo "Overall status: WARNING"
    fi

    return $status
}

main "$@"
```

## Best Practices

### Script Template

```bash
#!/bin/bash

################################################################################
# Script Name: template.sh
# Description: Script template with best practices
# Author: Your Name
# Date: $(date +%Y-%m-%d)
# Version: 1.0
################################################################################

# Strict mode
set -euo pipefail
IFS=$'\n\t'

# Global variables
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly LOG_FILE="${LOG_FILE:-/var/log/${SCRIPT_NAME%.sh}.log}"

# Functions
function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

function die() {
    log "ERROR: $@"
    exit 1
}

function usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Description of what this script does.

OPTIONS:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output

EXAMPLES:
    $SCRIPT_NAME --help
    $SCRIPT_NAME --verbose

EOF
    exit 0
}

function cleanup() {
    log "Cleaning up..."
    # Cleanup code here
}

# Trap cleanup on exit
trap cleanup EXIT INT TERM

# Main function
function main() {
    log "Starting $SCRIPT_NAME"

    # Main logic here

    log "Completed successfully"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        *)
            die "Unknown option: $1"
            ;;
    esac
done

# Execute main
main "$@"
```

### Best Practices Summary

✅ **Use strict mode**: `set -euo pipefail`
✅ **Quote variables**: `"$variable"` not `$variable`
✅ **Use functions**: Modular, reusable code
✅ **Handle errors**: Check return codes, use trap
✅ **Log everything**: Timestamp all output
✅ **Validate input**: Check arguments before using
✅ **Use readonly**: For constants
✅ **Use local**: For function variables
✅ **Document code**: Comments and usage functions
✅ **Test scripts**: Run with `-n` for syntax check

❌ **Avoid**:
- Global variables when local will do
- Bare `$*` or `$@` (always quote)
- Parsing `ls` output
- Using `cd` without checking
- Ignoring errors
- Hard-coded paths (use variables)

## Summary and Key Takeaways

### Commands and Syntax Mastered

**Script Basics**:
- `#!/bin/bash` - Shebang
- `chmod +x` - Make executable
- `set -euo pipefail` - Strict mode

**Variables**:
- `VAR=value` - Assignment
- `$VAR` or `${VAR}` - Reference
- `readonly` - Constants
- `local` - Function-scoped

**Control Flow**:
- `if [ condition ]; then ... fi`
- `for item in list; do ... done`
- `while [ condition ]; do ... done`
- `case $var in ... esac`

**Functions**:
- `function name() { ... }`
- `return` - Exit code
- `echo` - Return value

**Debugging**:
- `set -x` - Trace mode
- `bash -n` - Syntax check
- `echo` - Debug output

### Key Concepts

1. **Automation**: Scripts eliminate manual, repetitive tasks
2. **Reliability**: Consistent execution, no human error
3. **Documentation**: Executable documentation of processes
4. **Error Handling**: Graceful failure and recovery
5. **Modularity**: Functions for reusable code blocks

### AI Infrastructure Applications

- Automate model deployment pipelines
- Orchestrate multi-GPU training jobs
- Monitor system and GPU resources
- Manage datasets and preprocessing
- Health checks and alerting
- Backup and disaster recovery
- Environment provisioning

### Next Steps

In **Lecture 05: Package Management and System Updates**, you'll learn:
- Using apt, yum, and dnf package managers
- Installing ML frameworks and dependencies
- Managing Python packages and virtual environments
- System updates and security patches
- Building from source when necessary

### Quick Reference

```bash
# Basic script
#!/bin/bash
set -euo pipefail

# Variables
VAR="value"
readonly CONST="constant"
local local_var="function scope"

# Control flow
if [ condition ]; then cmd; fi
for i in list; do cmd; done
while [ cond ]; do cmd; done
case $var in pat) cmd ;; esac

# Functions
function name() {
    local arg=$1
    echo "result"
    return 0
}

# Arguments
$0  # Script name
$1  # First argument
$#  # Argument count
$@  # All arguments

# Error handling
set -e              # Exit on error
command || die "msg"  # Die if failed
trap cleanup EXIT   # Run on exit
```

---

**End of Lecture 04**

Continue to **Lecture 05: Package Management** to learn how to manage system packages and dependencies for AI infrastructure.
