# Lecture 05: Introduction to Shell Scripting

## Table of Contents
1. [Introduction](#introduction)
2. [Bash Script Basics](#bash-script-basics)
3. [Variables and Data Types](#variables-and-data-types)
4. [Basic Control Structures](#basic-control-structures)
5. [Simple Functions](#simple-functions)
6. [Command-Line Arguments](#command-line-arguments)
7. [Basic Error Handling](#basic-error-handling)
8. [Practical Examples](#practical-examples)
9. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Shell scripting is the AI infrastructure engineer's superpower for automation. Whether deploying models, managing datasets, or orchestrating training pipelines, shell scripts turn repetitive manual tasks into reliable, repeatable processes.

This lecture introduces you to Bash scripting fundamentals. You'll learn to write simple but powerful scripts that automate common AI infrastructure tasks.

### Learning Objectives

By the end of this lecture, you will:
- Write and execute basic Bash scripts
- Use variables and command substitution
- Implement simple control structures (if/else, for/while loops)
- Create reusable functions
- Process command-line arguments
- Handle basic errors
- Apply scripting to AI infrastructure automation

### Prerequisites
- Lectures 01-04 (Linux fundamentals through system administration)
- Comfort with command-line basics
- Text editor familiarity (nano, vim, or VS Code)

### Why Shell Scripting for AI Infrastructure?

**Automation**: Deploy models, provision environments, orchestrate training
**Consistency**: Same process every time, no manual errors
**Efficiency**: Automate repetitive tasks, save hours daily
**Integration**: Glue together different tools and services
**Documentation**: Scripts serve as executable documentation

**Duration**: 90 minutes
**Difficulty**: Beginner to Intermediate

---

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

### The Shebang (#!)

The first line tells the system which interpreter to use:

```bash
#!/bin/bash              # Use bash
#!/bin/sh                # Use sh (POSIX compatible)
#!/usr/bin/env bash      # Use bash (portable - finds bash in PATH)
#!/usr/bin/env python3   # Use python3
```

**Best Practice**: Use `#!/bin/bash` for bash-specific features, `#!/bin/sh` for maximum portability.

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
# Output: Hello, World!

# Or run with bash explicitly (doesn't need execute permission)
bash hello.sh
```

**Important**: Scripts must be executable (`chmod +x`) to run with `./script.sh` syntax.

### Script Structure

A well-organized script follows this structure:

```bash
#!/bin/bash

#############################################
# Script Name: setup-ml-env.sh
# Description: Set up ML development environment
# Author: Your Name
# Date: 2024-10-28
# Version: 1.0
#############################################

# Global variables
MODEL_PATH="/models/production"
LOG_FILE="/var/log/setup.log"

# Functions
function log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

function setup_environment() {
    log_message "Setting up environment..."
    # Setup logic here
}

# Main execution
main() {
    log_message "Starting setup"
    setup_environment
    log_message "Setup complete"
}

# Run main function
main "$@"
```

### Comments

```bash
# Single line comment
# This is ignored by the shell

echo "Output"  # Inline comment

: '
Multi-line comment
Everything between these quotes is ignored
Useful for documenting larger blocks
'

# TODO: Add error handling
# FIXME: This needs optimization
# NOTE: Important information
```

---

## Variables and Data Types

### Variable Assignment

**Basic assignment** (no spaces around =):

```bash
# Correct
NAME="Alice"
AGE=25
MODEL_PATH="/models/resnet50.h5"

# Wrong (will cause errors)
NAME = "Alice"      # Spaces around = not allowed
AGE =25             # Space before = not allowed
```

**Using variables**:

```bash
# Reference with $
echo $NAME
echo "My name is $NAME"

# Better: Use braces (recommended)
echo "Model: ${MODEL_PATH}"
echo "Age next year: $((AGE + 1))"
```

### Command Substitution

Capture command output in variables:

```bash
# Modern syntax (preferred)
CURRENT_DATE=$(date +%Y-%m-%d)
NUM_FILES=$(ls | wc -l)
GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)

# Old syntax (backticks - avoid)
HOSTNAME=`hostname`

# Use in strings
echo "Today is ${CURRENT_DATE}"
echo "Found ${NUM_FILES} files"
```

### Arithmetic Operations

```bash
# Arithmetic expansion
COUNT=5
COUNT=$((COUNT + 1))        # COUNT is now 6
TOTAL=$((5 * 10))           # TOTAL is 50
RESULT=$((100 / 3))         # RESULT is 33 (integer division)

# Common operations
X=$((10 + 5))               # Addition
X=$((10 - 5))               # Subtraction
X=$((10 * 5))               # Multiplication
X=$((10 / 5))               # Division
X=$((10 % 3))               # Modulo (remainder)

# Increment/decrement
COUNT=$((COUNT + 1))        # Increment
COUNT=$((COUNT - 1))        # Decrement

# Use in practice
BATCH_SIZE=32
NUM_BATCHES=$((1000 / BATCH_SIZE))
echo "Will process ${NUM_BATCHES} batches"
```

### String Operations

```bash
# String length
NAME="Alice"
echo ${#NAME}               # 5

# Substring extraction
TEXT="Hello, World!"
echo ${TEXT:0:5}            # Hello (start at 0, length 5)
echo ${TEXT:7}              # World! (start at 7, to end)

# String replacement
FILENAME="model_v1.h5"
echo ${FILENAME/v1/v2}      # model_v2.h5 (replace first)
echo ${FILENAME//v1/v2}     # Replace all occurrences

# Change extension
echo ${FILENAME/.h5/.pt}    # model_v1.pt

# Default values
echo ${VAR:-default}        # Use 'default' if VAR is unset
VAR=${VAR:-default}         # Set VAR to 'default' if unset

# Example: Configuration with defaults
MODEL_NAME=${MODEL_NAME:-resnet50}
BATCH_SIZE=${BATCH_SIZE:-32}
echo "Training ${MODEL_NAME} with batch size ${BATCH_SIZE}"
```

### Quoting Rules

**Single quotes** - Literal strings (no variable expansion):
```bash
NAME="Alice"
echo 'Hello $NAME'          # Output: Hello $NAME
```

**Double quotes** - Allow variable expansion:
```bash
NAME="Alice"
echo "Hello $NAME"          # Output: Hello Alice
```

**No quotes** - Word splitting and globbing:
```bash
FILES=$(ls *.txt)
echo $FILES                 # Words split by spaces
echo "$FILES"               # Preserved with newlines
```

**Best Practice**: Always quote variables unless you specifically need word splitting.

```bash
# Good
echo "Processing file: $FILENAME"

# Bad (can break with spaces in filename)
echo Processing file: $FILENAME

# Good (preserve spaces and special characters)
cp "$SOURCE" "$DEST"

# Bad (breaks with spaces)
cp $SOURCE $DEST
```

### Variable Scope

```bash
# Global variable
GLOBAL_VAR="I am global"

# Function with local variable
function test_scope() {
    local LOCAL_VAR="I am local"
    echo "Inside function: $GLOBAL_VAR"
    echo "Inside function: $LOCAL_VAR"
}

test_scope
echo "Outside function: $GLOBAL_VAR"
echo "Outside function: $LOCAL_VAR"  # Empty - LOCAL_VAR not accessible
```

---

## Basic Control Structures

### If Statements

**Basic if**:
```bash
if [ -f "model.h5" ]; then
    echo "Model file exists"
fi
```

**If-else**:
```bash
if [ -d "/data/imagenet" ]; then
    echo "Dataset found"
else
    echo "Dataset not found"
    exit 1
fi
```

**If-elif-else**:
```bash
GPU_COUNT=2

if [ $GPU_COUNT -eq 0 ]; then
    echo "No GPUs available"
elif [ $GPU_COUNT -eq 1 ]; then
    echo "One GPU available"
else
    echo "$GPU_COUNT GPUs available"
fi
```

### Test Operators

**File tests**:
```bash
[ -e file ]         # Exists
[ -f file ]         # Is regular file
[ -d dir ]          # Is directory
[ -L link ]         # Is symbolic link
[ -r file ]         # Is readable
[ -w file ]         # Is writable
[ -x file ]         # Is executable
[ -s file ]         # File size > 0

# Examples
if [ -f "config.yaml" ]; then
    echo "Config file found"
fi

if [ ! -d "logs" ]; then
    mkdir logs
fi
```

**String tests**:
```bash
[ -z "$str" ]       # String is empty
[ -n "$str" ]       # String is not empty
[ "$s1" = "$s2" ]   # Strings are equal
[ "$s1" != "$s2" ]  # Strings are not equal

# Examples
if [ -z "$MODEL_NAME" ]; then
    echo "Error: MODEL_NAME is not set"
    exit 1
fi

if [ "$ENV" = "production" ]; then
    echo "Running in production mode"
fi
```

**Numeric tests**:
```bash
[ $a -eq $b ]       # Equal
[ $a -ne $b ]       # Not equal
[ $a -lt $b ]       # Less than
[ $a -le $b ]       # Less than or equal
[ $a -gt $b ]       # Greater than
[ $a -ge $b ]       # Greater than or equal

# Examples
EPOCHS=100
if [ $EPOCHS -gt 50 ]; then
    echo "Long training job"
fi

if [ $GPU_COUNT -ge 2 ]; then
    echo "Can run distributed training"
fi
```

**Combining conditions**:
```bash
# AND
if [ -f "model.h5" ] && [ -f "config.yaml" ]; then
    echo "Both files found"
fi

# OR
if [ ! -f "model.h5" ] || [ ! -f "config.yaml" ]; then
    echo "Missing required files"
fi

# Complex conditions with [[ ]]
if [[ -f "model.h5" && -f "config.yaml" ]]; then
    echo "Both files found"
fi
```

### For Loops

**Iterate over list**:
```bash
# Simple list
for model in resnet50 vgg16 inception; do
    echo "Processing $model"
done

# Iterate array
MODELS=("resnet50" "vgg16" "inception")
for model in "${MODELS[@]}"; do
    echo "Training $model"
    python train.py --model "$model"
done
```

**Iterate over files**:
```bash
# Process all .h5 files
for file in *.h5; do
    echo "Found model: $file"
done

# Process files in directory
for file in /data/images/*.jpg; do
    echo "Processing image: $file"
done
```

**Numeric ranges**:
```bash
# Range with brace expansion
for i in {1..5}; do
    echo "Iteration $i"
done

# Range with step
for i in {0..10..2}; do
    echo "Even number: $i"
done

# C-style for loop
for ((i=0; i<10; i++)); do
    echo "Count: $i"
done
```

**Practical examples**:
```bash
# Train models on different GPUs
MODELS=("resnet50" "vgg16" "mobilenet")
GPU=0

for model in "${MODELS[@]}"; do
    echo "Training $model on GPU $GPU"
    CUDA_VISIBLE_DEVICES=$GPU python train.py --model "$model" &
    GPU=$((GPU + 1))
done
wait  # Wait for all background jobs

# Process dataset batches
for batch in {1..100}; do
    echo "Processing batch $batch"
    python process.py --batch $batch
done
```

### While Loops

**Basic while**:
```bash
COUNT=0
while [ $COUNT -lt 5 ]; do
    echo "Count: $COUNT"
    COUNT=$((COUNT + 1))
done
```

**Read file line by line**:
```bash
while IFS= read -r line; do
    echo "Line: $line"
done < file.txt

# Process CSV file
while IFS=, read -r name age city; do
    echo "Name: $name, Age: $age, City: $city"
done < data.csv
```

**Infinite loop with break**:
```bash
while true; do
    echo "Checking system health..."

    # Check if service is running
    if ! systemctl is-active ml-api; then
        echo "Service is down! Restarting..."
        systemctl restart ml-api
    fi

    sleep 60  # Wait 60 seconds
done
```

**Until loop** (runs until condition is true):
```bash
COUNT=0
until [ $COUNT -ge 5 ]; do
    echo "Count: $COUNT"
    COUNT=$((COUNT + 1))
done
```

### Break and Continue

```bash
# Break - exit loop
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        break  # Stop loop at 5
    fi
    echo $i
done
# Output: 1 2 3 4

# Continue - skip to next iteration
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue  # Skip 5
    fi
    echo $i
done
# Output: 1 2 3 4 6 7 8 9 10
```

---

## Simple Functions

### Defining Functions

**Method 1** (with function keyword):
```bash
function greet() {
    echo "Hello, $1!"
}

greet "Alice"
# Output: Hello, Alice!
```

**Method 2** (POSIX style):
```bash
greet() {
    echo "Hello, $1!"
}

greet "Bob"
# Output: Hello, Bob!
```

### Function Arguments

Functions access arguments through special variables:
- `$1`, `$2`, `$3`, ... - Individual arguments
- `$@` - All arguments as separate words
- `$#` - Number of arguments

```bash
function train_model() {
    local model_name=$1
    local epochs=$2
    local gpu_id=${3:-0}  # Default to 0 if not provided

    echo "Training $model_name"
    echo "Epochs: $epochs"
    echo "GPU: $gpu_id"

    python train.py --model "$model_name" --epochs "$epochs" --gpu "$gpu_id"
}

# Call function
train_model "resnet50" 100 2
```

### Return Values

**Exit codes** (0-255):
```bash
function check_file() {
    local file=$1

    if [ -f "$file" ]; then
        return 0  # Success
    else
        return 1  # Failure
    fi
}

# Use return value
if check_file "model.h5"; then
    echo "File exists"
else
    echo "File not found"
fi
```

**Return strings via echo**:
```bash
function get_model_name() {
    local path=$1
    basename "$path" .h5
}

MODEL_NAME=$(get_model_name "/models/resnet50.h5")
echo $MODEL_NAME  # resnet50
```

### Local Variables

Use `local` to keep variables function-scoped:

```bash
GLOBAL_VAR="I am global"

function test_local() {
    local LOCAL_VAR="I am local"
    GLOBAL_VAR="Modified global"

    echo "Inside function:"
    echo "  GLOBAL_VAR: $GLOBAL_VAR"
    echo "  LOCAL_VAR: $LOCAL_VAR"
}

test_local

echo "Outside function:"
echo "  GLOBAL_VAR: $GLOBAL_VAR"    # Modified global
echo "  LOCAL_VAR: $LOCAL_VAR"      # Empty - not accessible
```

### Practical Function Examples

**Logging function**:
```bash
function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@"
}

log "Starting training"
log "Epoch 1 complete"
log "Training finished"
```

**Error handling function**:
```bash
function die() {
    echo "ERROR: $@" >&2
    exit 1
}

# Usage
if [ ! -f "config.yaml" ]; then
    die "Config file not found"
fi
```

**Check if command exists**:
```bash
function command_exists() {
    command -v "$1" &> /dev/null
}

if ! command_exists nvidia-smi; then
    echo "nvidia-smi not found. Please install NVIDIA drivers."
    exit 1
fi
```

---

## Command-Line Arguments

### Positional Parameters

Scripts access arguments through special variables:

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
# Output:
# Script name: ./script.sh
# First argument: model.h5
# Second argument: config.yaml
# All arguments: model.h5 config.yaml
# Number of arguments: 2
```

### Processing Arguments

**Basic argument handling**:
```bash
#!/bin/bash
# train.sh

if [ $# -lt 2 ]; then
    echo "Usage: $0 <model_name> <epochs>"
    exit 1
fi

MODEL_NAME=$1
EPOCHS=$2
GPU=${3:-0}  # Optional third argument, default to 0

echo "Training $MODEL_NAME for $EPOCHS epochs on GPU $GPU"
python train.py --model "$MODEL_NAME" --epochs "$EPOCHS" --gpu "$GPU"
```

### Simple Options with getopts

`getopts` is a built-in for parsing options:

```bash
#!/bin/bash
# train.sh - Training script with options

usage() {
    echo "Usage: $0 [-m MODEL] [-e EPOCHS] [-g GPU] [-h]"
    echo "  -m MODEL    Model architecture (default: resnet50)"
    echo "  -e EPOCHS   Number of epochs (default: 100)"
    echo "  -g GPU      GPU ID (default: 0)"
    echo "  -h          Show this help"
    exit 1
}

# Defaults
MODEL="resnet50"
EPOCHS=100
GPU=0

# Parse options
while getopts "m:e:g:h" opt; do
    case $opt in
        m) MODEL="$OPTARG" ;;
        e) EPOCHS="$OPTARG" ;;
        g) GPU="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Shift past processed options
shift $((OPTIND - 1))

echo "Model: $MODEL"
echo "Epochs: $EPOCHS"
echo "GPU: $GPU"
echo "Remaining args: $@"

# Run training
python train.py --model "$MODEL" --epochs "$EPOCHS" --gpu "$GPU"

# Example usage:
# ./train.sh -m vgg16 -e 50 -g 2
# ./train.sh -h
```

---

## Basic Error Handling

### Exit Codes

Every command returns an exit code:
- `0` = Success
- Non-zero = Error

```bash
# Check last command exit code
ls /tmp
echo $?   # 0 (success)

ls /nonexistent
echo $?   # Non-zero (error)

# Use in conditionals
if ls /data; then
    echo "Directory exists"
else
    echo "Directory not found"
fi
```

### Exit on Error

Use `set -e` to exit script on any error:

```bash
#!/bin/bash
set -e  # Exit on error

echo "Step 1"
command1

echo "Step 2"
command2  # If this fails, script exits immediately

echo "Step 3"
command3  # This won't run if command2 failed
```

### Exit on Undefined Variable

Use `set -u` to exit on undefined variables:

```bash
#!/bin/bash
set -u  # Exit on undefined variable

echo $UNDEFINED_VAR  # Script exits with error
```

### Combining Options

```bash
#!/bin/bash
# Strict mode
set -euo pipefail

# -e: Exit on error
# -u: Exit on undefined variable
# -o pipefail: Exit if any command in a pipeline fails

# This is safer:
command1 | command2 | command3
# If command2 fails, script exits (due to pipefail)
```

### Temporarily Disable Error Exit

```bash
#!/bin/bash
set -e

# This command might fail, and that's OK
set +e
optional_command_that_might_fail
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
    echo "Optional command failed, but continuing"
fi

# Continue with script
```

### Error Messages

**Print to stderr**:
```bash
# Redirect to stderr with >&2
echo "ERROR: File not found" >&2

# Better: Create error function
function error() {
    echo "ERROR: $@" >&2
}

error "Configuration file missing"
```

---

## Practical Examples

### Example 1: Environment Setup Script

```bash
#!/bin/bash
set -euo pipefail

# setup-ml-env.sh - Set up ML development environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

function log() {
    echo -e "${GREEN}[INFO]${NC} $@"
}

function error() {
    echo -e "${RED}[ERROR]${NC} $@" >&2
}

function check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 not found"
        return 1
    fi
    return 0
}

# Main setup
log "Setting up ML environment..."

# Check prerequisites
log "Checking prerequisites..."
check_command python3 || exit 1
check_command pip || exit 1

# Create virtual environment
log "Creating virtual environment..."
python3 -m venv ml-env

# Activate virtual environment
source ml-env/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Install packages
log "Installing ML packages..."
pip install numpy pandas scikit-learn tensorflow torch

log "Setup complete!"
log "To activate: source ml-env/bin/activate"
```

### Example 2: Model Training Automation

```bash
#!/bin/bash
set -euo pipefail

# train-models.sh - Train multiple models

MODELS=("resnet50" "vgg16" "mobilenet")
EPOCHS=10
LOG_DIR="logs"

# Create log directory
mkdir -p "$LOG_DIR"

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@" | tee -a "$LOG_DIR/training.log"
}

log "Starting training pipeline"

# Train each model
for model in "${MODELS[@]}"; do
    log "Training $model..."

    LOG_FILE="$LOG_DIR/${model}_$(date +%Y%m%d_%H%M%S).log"

    if python train.py --model "$model" --epochs "$EPOCHS" > "$LOG_FILE" 2>&1; then
        log "$model training completed successfully"
    else
        log "ERROR: $model training failed"
        exit 1
    fi
done

log "All models trained successfully"
```

### Example 3: System Health Check

```bash
#!/bin/bash

# health-check.sh - Check system health

WARN_CPU=80
WARN_MEM=85
WARN_DISK=90

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

# Run checks
echo "=== System Health Check $(date) ==="
echo ""

STATUS=0
check_cpu || STATUS=1
check_memory || STATUS=1
check_disk || STATUS=1

echo ""
if [ $STATUS -eq 0 ]; then
    echo "Overall status: HEALTHY"
else
    echo "Overall status: WARNING"
fi

exit $STATUS
```

### Example 4: Backup Script

```bash
#!/bin/bash
set -euo pipefail

# backup-models.sh - Backup ML models

SOURCE_DIR="/models/production"
BACKUP_DIR="/backups/models"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="models_backup_${TIMESTAMP}.tar.gz"

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@"
}

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    log "ERROR: Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
log "Creating backup: $BACKUP_NAME"
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}" -C "$(dirname $SOURCE_DIR)" "$(basename $SOURCE_DIR)"

# Verify backup
if [ -f "${BACKUP_DIR}/${BACKUP_NAME}" ]; then
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}" | cut -f1)
    log "Backup created successfully: ${BACKUP_NAME} (${SIZE})"
else
    log "ERROR: Backup failed"
    exit 1
fi

# Keep only last 7 days of backups
log "Cleaning old backups..."
find "$BACKUP_DIR" -name "models_backup_*.tar.gz" -mtime +7 -delete

log "Backup complete"
```

---

## Summary and Key Takeaways

### Commands and Syntax Mastered

**Script Basics**:
- `#!/bin/bash` - Shebang line
- `chmod +x script.sh` - Make executable
- `./script.sh` - Run script

**Variables**:
- `VAR=value` - Assignment (no spaces!)
- `$VAR` or `${VAR}` - Reference variable
- `$(command)` - Command substitution
- `$((expression))` - Arithmetic

**Control Flow**:
- `if [ condition ]; then ... fi` - Conditional
- `for item in list; do ... done` - For loop
- `while [ condition ]; do ... done` - While loop

**Functions**:
- `function name() { ... }` - Define function
- `$1, $2, $3` - Function arguments
- `return` - Exit code
- `local VAR` - Local variable

**Error Handling**:
- `set -e` - Exit on error
- `set -u` - Exit on undefined variable
- `set -o pipefail` - Exit on pipe failures
- `$?` - Last exit code

### Key Concepts

1. **Scripts are programs**: Write scripts like any other program with structure and documentation
2. **Variables store data**: Use variables to make scripts flexible and maintainable
3. **Control flow guides execution**: if/for/while determine what code runs
4. **Functions promote reuse**: Write once, use many times
5. **Error handling prevents disasters**: Always handle errors gracefully

### Best Practices Learned

✅ **Always use shebang**: `#!/bin/bash`
✅ **Quote variables**: `"$VAR"` not `$VAR`
✅ **Use local in functions**: Prevents variable conflicts
✅ **Check exit codes**: Verify commands succeeded
✅ **Add comments**: Explain what and why
✅ **Use meaningful names**: `model_name` not `x`
✅ **Handle errors**: Use `set -e` or check return values
✅ **Test scripts**: Run with test data before production

### Common Patterns for AI Infrastructure

```bash
# Check if file exists before using
if [ ! -f "model.h5" ]; then
    echo "Model not found"
    exit 1
fi

# Loop over models
for model in resnet50 vgg16 inception; do
    python train.py --model "$model"
done

# Create timestamp for logs
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="training_${TIMESTAMP}.log"

# Run with GPU selection
for gpu in 0 1 2 3; do
    CUDA_VISIBLE_DEVICES=$gpu python train.py --gpu $gpu &
done
wait

# Simple error handling
if ! python train.py; then
    echo "Training failed"
    exit 1
fi
```

### Next Steps

In **Lecture 06: Advanced Shell Scripting**, you'll learn:
- Advanced control structures (case statements)
- Arrays and associative arrays
- String manipulation and regex
- Advanced argument processing
- Complex error handling and debugging
- Script templates and best practices

### Quick Reference

```bash
# Variables
VAR="value"
echo "$VAR"
RESULT=$(command)
NUM=$((5 + 3))

# Conditionals
if [ condition ]; then
    # code
fi

# Loops
for item in list; do
    # code
done

while [ condition ]; do
    # code
done

# Functions
function name() {
    local var=$1
    echo "result"
    return 0
}

# Arguments
$0  # Script name
$1  # First arg
$#  # Arg count
$@  # All args

# Error handling
set -e
if ! command; then
    echo "Error" >&2
    exit 1
fi
```

---

**End of Lecture 05: Introduction to Shell Scripting**

You now have the foundation to write simple but powerful shell scripts for AI infrastructure automation. Practice writing scripts for your daily tasks to build confidence and fluency.

**Next**: Lecture 06 - Advanced Shell Scripting
