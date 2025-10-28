# Lecture 06: Advanced Shell Scripting

## Table of Contents
1. [Introduction](#introduction)
2. [Advanced Control Structures](#advanced-control-structures)
3. [Arrays and Associative Arrays](#arrays-and-associative-arrays)
4. [Advanced String Manipulation](#advanced-string-manipulation)
5. [Advanced Argument Processing](#advanced-argument-processing)
6. [Regular Expressions in Bash](#regular-expressions-in-bash)
7. [Advanced Error Handling and Debugging](#advanced-error-handling-and-debugging)
8. [Script Templates and Best Practices](#script-templates-and-best-practices)
9. [Practical AI Infrastructure Automation](#practical-ai-infrastructure-automation)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Building on the fundamentals from Lecture 05, this lecture dives into advanced shell scripting techniques. You'll learn to write sophisticated, production-ready scripts that handle complex AI infrastructure automation tasks with robustness and elegance.

### Learning Objectives

By the end of this lecture, you will:
- Master case statements and advanced conditionals
- Work with arrays and associative arrays
- Perform complex string manipulation
- Process command-line arguments professionally
- Use regular expressions for pattern matching
- Implement comprehensive error handling
- Debug scripts effectively
- Write production-ready automation scripts
- Apply advanced techniques to AI infrastructure

### Prerequisites
- Lecture 05 (Introduction to Shell Scripting)
- Comfortable with basic bash scripting
- Understanding of variables, functions, and basic control flow

### Why Advanced Scripting?

**Production Readiness**: Basic scripts work for personal use; advanced scripts handle production workloads

**Robustness**: Handle edge cases, errors, and unexpected inputs gracefully

**Maintainability**: Well-structured code is easier to debug and extend

**Scalability**: Scripts that work with one model must work with hundreds

**Professionalism**: Production infrastructure demands professional code quality

**Duration**: 120 minutes
**Difficulty**: Intermediate to Advanced

---

## Advanced Control Structures

### Case Statements

Case statements provide cleaner syntax than multiple if-elif-else chains.

**Basic case statement**:
```bash
#!/bin/bash

ACTION=$1

case "$ACTION" in
    start)
        echo "Starting service..."
        systemctl start ml-api
        ;;
    stop)
        echo "Stopping service..."
        systemctl stop ml-api
        ;;
    restart)
        echo "Restarting service..."
        systemctl restart ml-api
        ;;
    status)
        systemctl status ml-api
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
```

**Pattern matching in case**:
```bash
#!/bin/bash
# Process different model formats

FILE=$1

case "$FILE" in
    *.h5)
        echo "Keras model detected"
        python convert.py --format keras "$FILE"
        ;;
    *.pt|*.pth)
        echo "PyTorch model detected"
        python convert.py --format pytorch "$FILE"
        ;;
    *.onnx)
        echo "ONNX model detected"
        python convert.py --format onnx "$FILE"
        ;;
    *.pb)
        echo "TensorFlow SavedModel detected"
        python convert.py --format tensorflow "$FILE"
        ;;
    *)
        echo "ERROR: Unknown model format: $FILE"
        exit 1
        ;;
esac
```

**Multiple patterns per case**:
```bash
#!/bin/bash

ENVIRONMENT=$1

case "$ENVIRONMENT" in
    dev|development)
        CONFIG="config.dev.yaml"
        REPLICAS=1
        RESOURCES="minimal"
        ;;
    staging|stg)
        CONFIG="config.staging.yaml"
        REPLICAS=2
        RESOURCES="medium"
        ;;
    prod|production)
        CONFIG="config.prod.yaml"
        REPLICAS=4
        RESOURCES="maximum"
        ;;
    test|testing)
        CONFIG="config.test.yaml"
        REPLICAS=1
        RESOURCES="minimal"
        ;;
    *)
        echo "ERROR: Unknown environment: $ENVIRONMENT"
        echo "Valid: dev, staging, prod, test"
        exit 1
        ;;
esac

echo "Deploying to $ENVIRONMENT"
echo "Config: $CONFIG"
echo "Replicas: $REPLICAS"
echo "Resources: $RESOURCES"
```

**Case with regex patterns** (using [[ ]] and =~):
```bash
#!/bin/bash

INPUT=$1

# Validate version format
if [[ "$INPUT" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Valid semantic version: $INPUT"
elif [[ "$INPUT" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "Minor version format: $INPUT"
elif [[ "$INPUT" =~ ^[0-9]+$ ]]; then
    echo "Major version only: $INPUT"
else
    echo "Invalid version format: $INPUT"
    exit 1
fi
```

### Advanced Conditionals

**Double bracket [[ ]] vs single bracket [ ]**:

```bash
# [[ ]] supports additional features
# - Pattern matching with ==
# - Regex matching with =~
# - Logical operators (&&, ||) without quotes
# - String comparison without quotes

# Pattern matching
if [[ "$FILENAME" == *.txt ]]; then
    echo "Text file"
fi

# Regex matching
if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Valid version"
fi

# Multiple conditions without escaping
if [[ -f "model.h5" && -f "config.yaml" ]]; then
    echo "Both files exist"
fi

# String comparison without quotes
if [[ $STATUS == "success" ]]; then
    echo "Operation succeeded"
fi
```

**Ternary-style operations**:
```bash
# Using && and ||
[ -f "model.h5" ] && echo "File exists" || echo "File not found"

# Assign default values
RESULT=$(command) || RESULT="default"

# Complex ternary-style
GPU_AVAILABLE=$(command -v nvidia-smi &> /dev/null && echo "yes" || echo "no")
```

---

## Arrays and Associative Arrays

### Indexed Arrays

**Creating and populating arrays**:
```bash
# Method 1: Direct assignment
MODELS=("resnet50" "vgg16" "inception" "mobilenet")

# Method 2: Individual elements
GPUS[0]=0
GPUS[1]=1
GPUS[2]=2
GPUS[3]=3

# Method 3: From command output
FILES=($(ls *.h5))
USERS=($(cut -d: -f1 /etc/passwd))
```

**Accessing array elements**:
```bash
MODELS=("resnet50" "vgg16" "inception")

echo ${MODELS[0]}           # First element: resnet50
echo ${MODELS[1]}           # Second element: vgg16
echo ${MODELS[-1]}          # Last element: inception
echo ${MODELS[@]}           # All elements (as separate words)
echo ${MODELS[*]}           # All elements (as single word)
echo ${#MODELS[@]}          # Array length: 3
```

**Iterating over arrays**:
```bash
MODELS=("resnet50" "vgg16" "inception" "mobilenet")

# Method 1: Iterate values
for model in "${MODELS[@]}"; do
    echo "Training $model"
    python train.py --model "$model"
done

# Method 2: Iterate indices
for i in "${!MODELS[@]}"; do
    echo "Model $i: ${MODELS[$i]}"
done

# Method 3: C-style
for ((i=0; i<${#MODELS[@]}; i++)); do
    echo "Model $i: ${MODELS[$i]}"
done
```

**Array operations**:
```bash
# Add element
MODELS+=("squeezenet")

# Remove element
unset MODELS[2]

# Slice array
MODELS=("resnet50" "vgg16" "inception" "mobilenet" "squeezenet")
echo ${MODELS[@]:1:3}       # vgg16 inception mobilenet (start:length)

# Copy array
NEW_MODELS=("${MODELS[@]}")

# Concatenate arrays
ARRAY1=(1 2 3)
ARRAY2=(4 5 6)
COMBINED=("${ARRAY1[@]}" "${ARRAY2[@]}")
```

**Practical example - Multi-GPU training**:
```bash
#!/bin/bash
set -euo pipefail

# Models to train
MODELS=("resnet50" "vgg16" "inception" "mobilenet")

# Available GPUs
GPUS=(0 1 2 3)

# Assign models to GPUs round-robin
GPU_INDEX=0

for model in "${MODELS[@]}"; do
    gpu=${GPUS[$GPU_INDEX]}

    echo "Training $model on GPU $gpu"
    CUDA_VISIBLE_DEVICES=$gpu python train.py --model "$model" \
        --output "results/${model}" &

    # Next GPU (with wraparound)
    GPU_INDEX=$(( (GPU_INDEX + 1) % ${#GPUS[@]} ))
done

# Wait for all training jobs to complete
wait

echo "All models trained successfully"
```

### Associative Arrays

Associative arrays use strings as keys (requires Bash 4+).

**Creating associative arrays**:
```bash
# Declare associative array
declare -A MODEL_PATHS

# Add key-value pairs
MODEL_PATHS["resnet50"]="/models/resnet50.h5"
MODEL_PATHS["vgg16"]="/models/vgg16.h5"
MODEL_PATHS["inception"]="/models/inception.h5"

# Alternative: declare and populate
declare -A CONFIG=(
    ["dev"]="config.dev.yaml"
    ["staging"]="config.staging.yaml"
    ["prod"]="config.prod.yaml"
)
```

**Accessing associative arrays**:
```bash
declare -A MODEL_PATHS=(
    ["resnet50"]="/models/resnet50.h5"
    ["vgg16"]="/models/vgg16.h5"
)

# Access by key
echo ${MODEL_PATHS["resnet50"]}      # /models/resnet50.h5

# All keys
echo ${!MODEL_PATHS[@]}              # resnet50 vgg16

# All values
echo ${MODEL_PATHS[@]}               # /models/resnet50.h5 /models/vgg16.h5

# Number of elements
echo ${#MODEL_PATHS[@]}              # 2

# Check if key exists
if [[ -v MODEL_PATHS["resnet50"] ]]; then
    echo "Key exists"
fi
```

**Iterating over associative arrays**:
```bash
declare -A MODEL_PATHS=(
    ["resnet50"]="/models/resnet50.h5"
    ["vgg16"]="/models/vgg16.h5"
    ["inception"]="/models/inception.h5"
)

# Iterate over keys
for model in "${!MODEL_PATHS[@]}"; do
    echo "$model -> ${MODEL_PATHS[$model]}"
done

# More complex iteration
for model in "${!MODEL_PATHS[@]}"; do
    path="${MODEL_PATHS[$model]}"

    if [ -f "$path" ]; then
        echo "✓ $model: $path"
    else
        echo "✗ $model: $path (NOT FOUND)"
    fi
done
```

**Practical example - Configuration management**:
```bash
#!/bin/bash
set -euo pipefail

# Environment configurations
declare -A CONFIGS=(
    ["dev_api_url"]="http://localhost:8000"
    ["dev_replicas"]="1"
    ["dev_resources"]="minimal"

    ["prod_api_url"]="https://api.production.com"
    ["prod_replicas"]="10"
    ["prod_resources"]="maximum"
)

ENV=$1  # dev or prod

# Get config values for environment
API_URL=${CONFIGS["${ENV}_api_url"]}
REPLICAS=${CONFIGS["${ENV}_replicas"]}
RESOURCES=${CONFIGS["${ENV}_resources"]}

echo "Deploying to $ENV"
echo "API URL: $API_URL"
echo "Replicas: $REPLICAS"
echo "Resources: $RESOURCES"

# Deploy with configuration
kubectl apply -f deployment.yaml \
    --set apiUrl="$API_URL" \
    --set replicas="$REPLICAS" \
    --set resources="$RESOURCES"
```

---

## Advanced String Manipulation

### String Length and Substrings

```bash
TEXT="Hello, World!"

# Length
echo ${#TEXT}                    # 13

# Substring (offset:length)
echo ${TEXT:0:5}                 # Hello
echo ${TEXT:7}                   # World!
echo ${TEXT:7:5}                 # World
echo ${TEXT: -6}                 # World! (note space before -)
```

### String Replacement

```bash
FILENAME="model_v1_final_v1.h5"

# Replace first occurrence
echo ${FILENAME/v1/v2}           # model_v2_final_v1.h5

# Replace all occurrences
echo ${FILENAME//v1/v2}          # model_v2_final_v2.h5

# Replace prefix
PATH_STR="/models/resnet50"
echo ${PATH_STR/#\/models/\/data}  # /data/resnet50

# Replace suffix
echo ${FILENAME/%.h5/.pt}        # model_v1_final_v1.pt
```

### Remove Patterns

```bash
FILEPATH="/data/models/resnet50.h5"

# Remove shortest prefix match
echo ${FILEPATH#*/}              # data/models/resnet50.h5

# Remove longest prefix match
echo ${FILEPATH##*/}             # resnet50.h5 (basename)

# Remove shortest suffix match
echo ${FILEPATH%.*}              # /data/models/resnet50

# Remove longest suffix match
echo ${FILEPATH%%.*}             # /data/models/resnet50
```

**Practical example - Path manipulation**:
```bash
#!/bin/bash

# Extract components from path
FULL_PATH="/data/models/production/resnet50_v2.h5"

# Get directory
DIR=${FULL_PATH%/*}              # /data/models/production

# Get filename
FILENAME=${FULL_PATH##*/}        # resnet50_v2.h5

# Get basename (no extension)
BASENAME=${FILENAME%.*}          # resnet50_v2

# Get extension
EXTENSION=${FILENAME##*.}        # h5

echo "Full path: $FULL_PATH"
echo "Directory: $DIR"
echo "Filename: $FILENAME"
echo "Basename: $BASENAME"
echo "Extension: $EXTENSION"

# Convert to different format
NEW_PATH="${DIR}/${BASENAME}.onnx"
echo "New path: $NEW_PATH"
```

### Case Conversion

```bash
TEXT="Hello World"

# Bash 4+
echo ${TEXT^}                    # Hello World (first char uppercase)
echo ${TEXT^^}                   # HELLO WORLD (all uppercase)
echo ${TEXT,}                    # hello World (first char lowercase)
echo ${TEXT,,}                   # hello world (all lowercase)

# Alternative for older Bash
echo "$TEXT" | tr '[:lower:]' '[:upper:]'   # HELLO WORLD
echo "$TEXT" | tr '[:upper:]' '[:lower:]'   # hello world
```

### Default Values

```bash
# Use default if unset
echo ${VAR:-default}             # Use 'default' if VAR is unset

# Set default if unset
VAR=${VAR:=default}              # Set VAR to 'default' if unset

# Use alternative if set
echo ${VAR:+alternative}         # Use 'alternative' if VAR is set

# Error if unset
echo ${VAR:?error message}       # Error with message if VAR is unset
```

**Practical example - Configuration with defaults**:
```bash
#!/bin/bash

# ML training configuration with defaults
MODEL_NAME=${MODEL_NAME:-resnet50}
BATCH_SIZE=${BATCH_SIZE:-32}
LEARNING_RATE=${LEARNING_RATE:-0.001}
EPOCHS=${EPOCHS:-100}
GPU_ID=${GPU_ID:-0}

echo "Training Configuration:"
echo "  Model: $MODEL_NAME"
echo "  Batch size: $BATCH_SIZE"
echo "  Learning rate: $LEARNING_RATE"
echo "  Epochs: $EPOCHS"
echo "  GPU: $GPU_ID"

# Run training
CUDA_VISIBLE_DEVICES=$GPU_ID python train.py \
    --model "$MODEL_NAME" \
    --batch-size "$BATCH_SIZE" \
    --lr "$LEARNING_RATE" \
    --epochs "$EPOCHS"

# Usage examples:
# ./train.sh                          # All defaults
# MODEL_NAME=vgg16 ./train.sh         # Custom model
# BATCH_SIZE=64 EPOCHS=200 ./train.sh # Custom params
```

---

## Advanced Argument Processing

### Long Options Parsing

```bash
#!/bin/bash
set -euo pipefail

# train.sh - Training script with long options

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Train ML model with specified configuration.

OPTIONS:
    --model=MODEL       Model architecture (default: resnet50)
    --epochs=N          Number of epochs (default: 100)
    --batch-size=N      Batch size (default: 32)
    --gpu=N             GPU ID (default: 0)
    --output=DIR        Output directory (required)
    --config=FILE       Config file (optional)
    --verbose           Enable verbose logging
    --help              Show this help message

EXAMPLES:
    $0 --model=vgg16 --epochs=50 --output=results/
    $0 --config=config.yaml --gpu=2 --output=results/
EOF
    exit 1
}

# Defaults
MODEL="resnet50"
EPOCHS=100
BATCH_SIZE=32
GPU=0
OUTPUT=""
CONFIG=""
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model=*)
            MODEL="${1#*=}"
            shift
            ;;
        --epochs=*)
            EPOCHS="${1#*=}"
            shift
            ;;
        --batch-size=*)
            BATCH_SIZE="${1#*=}"
            shift
            ;;
        --gpu=*)
            GPU="${1#*=}"
            shift
            ;;
        --output=*)
            OUTPUT="${1#*=}"
            shift
            ;;
        --config=*)
            CONFIG="${1#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "ERROR: Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [ -z "$OUTPUT" ]; then
    echo "ERROR: --output is required"
    usage
fi

# Display configuration
echo "Training Configuration:"
echo "  Model: $MODEL"
echo "  Epochs: $EPOCHS"
echo "  Batch size: $BATCH_SIZE"
echo "  GPU: $GPU"
echo "  Output: $OUTPUT"
[ -n "$CONFIG" ] && echo "  Config: $CONFIG"
[ "$VERBOSE" = true ] && echo "  Verbose: enabled"

# Build command
CMD="python train.py --model $MODEL --epochs $EPOCHS --batch-size $BATCH_SIZE --gpu $GPU --output $OUTPUT"
[ -n "$CONFIG" ] && CMD="$CMD --config $CONFIG"
[ "$VERBOSE" = true ] && CMD="$CMD --verbose"

# Execute
echo "Running: $CMD"
eval "$CMD"
```

### Mixing Short and Long Options

```bash
#!/bin/bash

# Parse both short (-m) and long (--model=) options

while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        --model=*)
            MODEL="${1#*=}"
            shift
            ;;
        -e|--epochs)
            EPOCHS="$2"
            shift 2
            ;;
        --epochs=*)
            EPOCHS="${1#*=}"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Now supports:
# ./script.sh -m resnet50
# ./script.sh --model resnet50
# ./script.sh --model=resnet50
```

### Positional Arguments After Options

```bash
#!/bin/bash

# deploy.sh [OPTIONS] environment target

OPTIONS=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --*)
            OPTIONS="$OPTIONS $1"
            shift
            ;;
        -*)
            OPTIONS="$OPTIONS $1 $2"
            shift 2
            ;;
        *)
            break  # Stop at first positional argument
            ;;
    esac
done

# Remaining arguments are positional
ENVIRONMENT=$1
TARGET=$2

echo "Options: $OPTIONS"
echo "Environment: $ENVIRONMENT"
echo "Target: $TARGET"
```

---

## Regular Expressions in Bash

### Pattern Matching with =~

```bash
# Regex matching requires [[ ]]

if [[ "$STRING" =~ pattern ]]; then
    echo "Match found"
fi
```

**Validate version numbers**:
```bash
VERSION="1.2.3"

if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Valid semantic version"
else
    echo "Invalid version format"
fi
```

**Extract information with capture groups**:
```bash
INPUT="model_resnet50_epoch_100.h5"

if [[ "$INPUT" =~ model_([a-z0-9]+)_epoch_([0-9]+) ]]; then
    MODEL_NAME="${BASH_REMATCH[1]}"
    EPOCH="${BASH_REMATCH[2]}"

    echo "Model: $MODEL_NAME"
    echo "Epoch: $EPOCH"
fi
```

**Validate email addresses**:
```bash
EMAIL="user@example.com"

if [[ "$EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "Valid email"
else
    echo "Invalid email"
fi
```

**Validate IP addresses**:
```bash
IP="192.168.1.100"

# Simple validation
if [[ "$IP" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo "Valid IP format"
fi

# More thorough validation
function validate_ip() {
    local ip=$1
    local valid=true

    if [[ $ip =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
        IFS='.' read -ra OCTETS <<< "$ip"
        for octet in "${OCTETS[@]}"; do
            if [ "$octet" -gt 255 ]; then
                valid=false
                break
            fi
        done
    else
        valid=false
    fi

    $valid
}

if validate_ip "192.168.1.100"; then
    echo "Valid IP address"
fi
```

**Practical example - Parse training logs**:
```bash
#!/bin/bash

# Extract metrics from training logs

LOG_FILE="training.log"

while IFS= read -r line; do
    # Match pattern: Epoch 50/100 - loss: 0.1234 - acc: 0.9876
    if [[ "$line" =~ Epoch[[:space:]]+([0-9]+)/([0-9]+).*loss:[[:space:]]+([0-9.]+).*acc:[[:space:]]+([0-9.]+) ]]; then
        EPOCH="${BASH_REMATCH[1]}"
        TOTAL="${BASH_REMATCH[2]}"
        LOSS="${BASH_REMATCH[3]}"
        ACCURACY="${BASH_REMATCH[4]}"

        echo "Epoch $EPOCH/$TOTAL: Loss=$LOSS, Accuracy=$ACCURACY"
    fi
done < "$LOG_FILE"
```

---

## Advanced Error Handling and Debugging

### Comprehensive Error Handling

```bash
#!/bin/bash

# Strict error handling
set -euo pipefail
IFS=$'\n\t'

# Error handler function
function error_handler() {
    local line=$1
    local exit_code=$2

    echo "ERROR at line $line: Command exited with status $exit_code" >&2

    # Cleanup on error
    cleanup

    exit $exit_code
}

# Trap errors
trap 'error_handler ${LINENO} $?' ERR

# Cleanup function
function cleanup() {
    echo "Performing cleanup..."
    # Remove temporary files, stop processes, etc.
}

# Trap exit
trap cleanup EXIT

# Trap interrupts
trap 'echo "Interrupted"; exit 130' INT TERM
```

### Validation Functions

```bash
#!/bin/bash

# Validate file exists
function require_file() {
    local file=$1
    local description=${2:-"File"}

    if [ ! -f "$file" ]; then
        echo "ERROR: $description not found: $file" >&2
        return 1
    fi
}

# Validate directory exists
function require_directory() {
    local dir=$1

    if [ ! -d "$dir" ]; then
        echo "ERROR: Directory not found: $dir" >&2
        return 1
    fi
}

# Validate command exists
function require_command() {
    local cmd=$1

    if ! command -v "$cmd" &> /dev/null; then
        echo "ERROR: Required command not found: $cmd" >&2
        return 1
    fi
}

# Validate numeric value
function require_number() {
    local value=$1
    local name=$2

    if ! [[ "$value" =~ ^[0-9]+$ ]]; then
        echo "ERROR: $name must be a number: $value" >&2
        return 1
    fi
}

# Validate GPU is available
function require_gpu() {
    local gpu_id=$1

    if ! command -v nvidia-smi &> /dev/null; then
        echo "ERROR: nvidia-smi not found" >&2
        return 1
    fi

    local gpu_count=$(nvidia-smi --list-gpus | wc -l)
    if [ "$gpu_id" -ge "$gpu_count" ]; then
        echo "ERROR: GPU $gpu_id not found (available: 0-$((gpu_count-1)))" >&2
        return 1
    fi
}

# Use in script
require_file "config.yaml" "Configuration file"
require_directory "/data/models"
require_command "python3"
require_number "$EPOCHS" "EPOCHS"
require_gpu 0
```

### Retry Logic

```bash
#!/bin/bash

# Retry function with exponential backoff
function retry() {
    local max_attempts=$1
    shift
    local delay=1
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt/$max_attempts: $@"

        if "$@"; then
            echo "Success on attempt $attempt"
            return 0
        fi

        if [ $attempt -lt $max_attempts ]; then
            echo "Failed. Retrying in ${delay}s..."
            sleep $delay
            delay=$((delay * 2))  # Exponential backoff
        fi

        attempt=$((attempt + 1))
    done

    echo "Failed after $max_attempts attempts"
    return 1
}

# Usage
retry 3 curl -f https://api.example.com/health
retry 5 python train.py --resume
```

### Debugging Techniques

**Debug mode**:
```bash
#!/bin/bash

# Enable debug mode with environment variable
DEBUG=${DEBUG:-0}

function debug() {
    if [ "$DEBUG" = "1" ]; then
        echo "[DEBUG] $@" >&2
    fi
}

debug "Starting script"
debug "Model: $MODEL_NAME"
debug "GPU: $GPU_ID"

# Usage:
# DEBUG=1 ./script.sh
```

**Trace execution**:
```bash
#!/bin/bash

# Enable trace for specific section
set -x  # Start tracing
command1
command2
set +x  # Stop tracing

# Or trace entire script
bash -x script.sh
```

**Verbose mode**:
```bash
#!/bin/bash

VERBOSE=false

function log() {
    if [ "$VERBOSE" = true ]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@"
    fi
}

# Parse --verbose flag
while [[ $# -gt 0 ]]; do
    case "$1" in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

log "Starting training"
log "Loading model"
```

---

## Script Templates and Best Practices

### Production Script Template

```bash
#!/bin/bash

################################################################################
# Script Name: production-template.sh
# Description: Production-ready script template with all best practices
# Author: Your Name
# Date: $(date +%Y-%m-%d)
# Version: 1.0.0
#
# Usage: ./production-template.sh [OPTIONS] <required_arg>
#
# Requirements:
#   - Bash 4.0+
#   - Required commands: python3, nvidia-smi
#
# Exit codes:
#   0 - Success
#   1 - General error
#   2 - Invalid arguments
#   3 - Missing dependencies
################################################################################

# Strict mode
set -euo pipefail
IFS=$'\n\t'

################################################################################
# GLOBAL VARIABLES
################################################################################

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_VERSION="1.0.0"
readonly LOG_FILE="${LOG_FILE:-/var/log/${SCRIPT_NAME%.sh}.log}"

# Default values
MODEL_NAME="${MODEL_NAME:-resnet50}"
EPOCHS="${EPOCHS:-100}"
VERBOSE=false
DRY_RUN=false

################################################################################
# UTILITY FUNCTIONS
################################################################################

# Print colored output
function print_red()    { echo -e "\033[0;31m$@\033[0m"; }
function print_green()  { echo -e "\033[0;32m$@\033[0m"; }
function print_yellow() { echo -e "\033[0;33m$@\033[0m"; }
function print_blue()   { echo -e "\033[0;34m$@\033[0m"; }

# Logging functions
function log_info()  { echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO]  $@" | tee -a "$LOG_FILE"; }
function log_warn()  { echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARN]  $@" | tee -a "$LOG_FILE"; }
function log_error() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $@" | tee -a "$LOG_FILE" >&2; }
function log_debug() { [ "$VERBOSE" = true ] && echo "[$(date +'%Y-%m-%d %H:%M:%S')] [DEBUG] $@" | tee -a "$LOG_FILE" >&2 || true; }

# Error handling
function die() {
    log_error "$@"
    exit 1
}

################################################################################
# ERROR HANDLING
################################################################################

function error_handler() {
    local line=$1
    log_error "Script failed at line $line"
}

trap 'error_handler ${LINENO}' ERR

function cleanup() {
    log_info "Performing cleanup..."
    # Add cleanup code here
}

trap cleanup EXIT
trap 'log_warn "Interrupted"; exit 130' INT TERM

################################################################################
# VALIDATION FUNCTIONS
################################################################################

function check_dependencies() {
    log_debug "Checking dependencies..."

    local deps=("python3" "nvidia-smi")
    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            die "Required command not found: $cmd"
        fi
    done
}

function validate_arguments() {
    log_debug "Validating arguments..."

    # Validate model name
    if [ -z "$MODEL_NAME" ]; then
        die "MODEL_NAME cannot be empty"
    fi

    # Validate epochs
    if ! [[ "$EPOCHS" =~ ^[0-9]+$ ]] || [ "$EPOCHS" -lt 1 ]; then
        die "EPOCHS must be a positive integer"
    fi
}

################################################################################
# USAGE AND HELP
################################################################################

function usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS] <required_arg>

Description of what this script does.

OPTIONS:
    -m, --model=NAME      Model architecture (default: $MODEL_NAME)
    -e, --epochs=N        Number of epochs (default: $EPOCHS)
    -v, --verbose         Enable verbose output
    -n, --dry-run         Show what would be done without doing it
    -h, --help            Show this help message
    --version             Show version information

EXAMPLES:
    $SCRIPT_NAME --model=vgg16 --epochs=50
    $SCRIPT_NAME -m resnet50 -e 100 --verbose

EXIT CODES:
    0 - Success
    1 - General error
    2 - Invalid arguments
    3 - Missing dependencies

EOF
    exit 0
}

function version() {
    echo "$SCRIPT_NAME version $SCRIPT_VERSION"
    exit 0
}

################################################################################
# ARGUMENT PARSING
################################################################################

function parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -m|--model)
                MODEL_NAME="$2"
                shift 2
                ;;
            --model=*)
                MODEL_NAME="${1#*=}"
                shift
                ;;
            -e|--epochs)
                EPOCHS="$2"
                shift 2
                ;;
            --epochs=*)
                EPOCHS="${1#*=}"
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            --version)
                version
                ;;
            *)
                die "Unknown option: $1"
                ;;
        esac
    done
}

################################################################################
# MAIN FUNCTIONS
################################################################################

function do_something() {
    log_info "Doing something with $MODEL_NAME for $EPOCHS epochs"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would execute: python train.py --model $MODEL_NAME --epochs $EPOCHS"
        return
    fi

    # Actual work here
    python train.py --model "$MODEL_NAME" --epochs "$EPOCHS"
}

function main() {
    log_info "Starting $SCRIPT_NAME v$SCRIPT_VERSION"

    check_dependencies
    validate_arguments

    do_something

    log_info "Script completed successfully"
}

################################################################################
# SCRIPT EXECUTION
################################################################################

# Parse arguments
parse_arguments "$@"

# Run main function
main
```

### Best Practices Checklist

✅ **Shebang**: Start with `#!/bin/bash`
✅ **Strict mode**: Use `set -euo pipefail`
✅ **Header comment**: Script name, description, author, date
✅ **Constants**: Use `readonly` for constants
✅ **Functions**: Break code into reusable functions
✅ **Quotes**: Always quote variables: `"$VAR"`
✅ **Local variables**: Use `local` in functions
✅ **Error handling**: Use `trap` and error handlers
✅ **Logging**: Log important events with timestamps
✅ **Validation**: Validate inputs before using
✅ **Usage function**: Provide clear usage information
✅ **Exit codes**: Use meaningful exit codes
✅ **Comments**: Explain why, not what
✅ **Dry-run mode**: Support --dry-run for testing
✅ **Version info**: Include --version flag

---

## Practical AI Infrastructure Automation

### Complete Model Deployment Pipeline

```bash
#!/bin/bash
set -euo pipefail

################################################################################
# deploy-ml-model.sh - Complete ML model deployment pipeline
################################################################################

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/model-deployment.log"

# Configuration
MODEL_REGISTRY="/models/registry"
STAGING_DIR="/models/staging"
PRODUCTION_DIR="/models/production"
BACKUP_DIR="/backups/models"
SERVICE_NAME="ml-inference-api"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Logging
function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $@" | tee -a "$LOG_FILE"
}

function log_error() {
    echo -e "${RED}[ERROR]${NC} $@" | tee -a "$LOG_FILE" >&2
}

function log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@" | tee -a "$LOG_FILE"
}

function log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@" | tee -a "$LOG_FILE"
}

# Validation
function validate_model() {
    local model_path=$1

    log "Validating model: $model_path"

    # Check file exists
    if [ ! -f "$model_path" ]; then
        log_error "Model file not found: $model_path"
        return 1
    fi

    # Check file size
    local size=$(stat -f%z "$model_path" 2>/dev/null || stat -c%s "$model_path")
    if [ "$size" -lt 1000 ]; then
        log_error "Model file too small: $size bytes"
        return 1
    fi

    # Validate model format
    if ! python -c "import tensorflow as tf; tf.keras.models.load_model('$model_path')" &> /dev/null; then
        log_error "Invalid model format"
        return 1
    fi

    log_success "Model validation passed"
    return 0
}

# Backup current model
function backup_current_model() {
    log "Backing up current production model..."

    local current_model="$PRODUCTION_DIR/current.h5"

    if [ ! -f "$current_model" ]; then
        log_warning "No current model to backup"
        return 0
    fi

    local backup_name="model_$(date +%Y%m%d_%H%M%S).h5"
    local backup_path="$BACKUP_DIR/$backup_name"

    mkdir -p "$BACKUP_DIR"
    cp "$current_model" "$backup_path"

    log_success "Backup saved: $backup_path"

    # Keep only last 10 backups
    log "Cleaning old backups..."
    ls -t "$BACKUP_DIR"/model_*.h5 | tail -n +11 | xargs -r rm
}

# Deploy to staging
function deploy_to_staging() {
    local source_model=$1

    log "Deploying to staging..."

    mkdir -p "$STAGING_DIR"
    cp "$source_model" "$STAGING_DIR/candidate.h5"

    log_success "Deployed to staging"
}

# Run validation tests
function run_validation_tests() {
    log "Running validation tests..."

    local test_script="$SCRIPT_DIR/validate_model.py"

    if [ ! -f "$test_script" ]; then
        log_error "Test script not found: $test_script"
        return 1
    fi

    if python "$test_script" --model "$STAGING_DIR/candidate.h5"; then
        log_success "All validation tests passed"
        return 0
    else
        log_error "Validation tests failed"
        return 1
    fi
}

# Promote to production
function promote_to_production() {
    log "Promoting to production..."

    backup_current_model

    mkdir -p "$PRODUCTION_DIR"
    cp "$STAGING_DIR/candidate.h5" "$PRODUCTION_DIR/current.h5"

    log_success "Model promoted to production"
}

# Restart service
function restart_service() {
    log "Restarting $SERVICE_NAME..."

    if systemctl restart "$SERVICE_NAME"; then
        log_success "Service restarted successfully"

        # Wait for service to be ready
        sleep 5

        # Health check
        if systemctl is-active "$SERVICE_NAME" &> /dev/null; then
            log_success "Service is running"
        else
            log_error "Service failed to start"
            return 1
        fi
    else
        log_error "Failed to restart service"
        return 1
    fi
}

# Rollback
function rollback() {
    log_warning "Rolling back deployment..."

    local latest_backup=$(ls -t "$BACKUP_DIR"/model_*.h5 | head -1)

    if [ -z "$latest_backup" ]; then
        log_error "No backup available for rollback"
        return 1
    fi

    cp "$latest_backup" "$PRODUCTION_DIR/current.h5"
    restart_service

    log_success "Rollback completed"
}

# Main deployment pipeline
function main() {
    local model_path=$1

    if [ -z "$model_path" ]; then
        log_error "Usage: $0 <model_path>"
        exit 1
    fi

    log "=== Starting Model Deployment Pipeline ==="
    log "Model: $model_path"

    # Validation
    if ! validate_model "$model_path"; then
        log_error "Model validation failed"
        exit 1
    fi

    # Deploy to staging
    if ! deploy_to_staging "$model_path"; then
        log_error "Staging deployment failed"
        exit 1
    fi

    # Run tests
    if ! run_validation_tests; then
        log_error "Validation tests failed"
        exit 1
    fi

    # Promote to production
    if ! promote_to_production; then
        log_error "Production promotion failed"
        rollback
        exit 1
    fi

    # Restart service
    if ! restart_service; then
        log_error "Service restart failed"
        rollback
        exit 1
    fi

    log_success "=== Deployment completed successfully ==="
}

# Execute
main "$@"
```

---

## Summary and Key Takeaways

### Advanced Techniques Mastered

**Control Structures**:
- Case statements for cleaner conditionals
- Advanced pattern matching
- Complex conditional expressions with [[ ]]

**Data Structures**:
- Indexed arrays for lists
- Associative arrays for key-value pairs
- Array operations and iterations

**String Processing**:
- Advanced substitution and replacement
- Pattern removal (prefix/suffix)
- Case conversion

**Arguments**:
- Long option parsing (--option=value)
- Mixed short and long options
- Positional arguments with options

**Regular Expressions**:
- Pattern matching with =~
- Capture groups with BASH_REMATCH
- Input validation

**Error Handling**:
- Comprehensive error trapping
- Validation functions
- Retry logic
- Debugging techniques

### Production Best Practices

✅ **Use strict mode**: `set -euo pipefail`
✅ **Validate all inputs**: Never trust user input
✅ **Log everything**: Timestamps and severity levels
✅ **Handle errors gracefully**: Trap, cleanup, rollback
✅ **Support dry-run mode**: Test without executing
✅ **Provide clear usage**: --help with examples
✅ **Version your scripts**: Track changes over time
✅ **Document thoroughly**: Comments, headers, README
✅ **Make idempotent**: Safe to run multiple times
✅ **Test extensively**: Unit tests for functions

### AI Infrastructure Applications

**Model Deployment**: Automated pipelines with validation and rollback
**Training Automation**: Multi-model, multi-GPU orchestration
**Resource Management**: Health checks, alerting, auto-scaling
**Data Processing**: ETL pipelines for datasets
**Monitoring**: Metrics collection and analysis
**Backup/Recovery**: Automated backups with retention policies

### Next Steps

In **Lecture 07: Text Processing Tools**, you'll learn:
- grep for pattern matching
- sed for stream editing
- awk for text processing and reports
- Combining tools in pipelines
- Analyzing ML logs and metrics

### Quick Reference

```bash
# Case statement
case "$VAR" in
    pattern1) commands ;;
    pattern2) commands ;;
    *) default ;;
esac

# Arrays
ARRAY=(item1 item2 item3)
echo ${ARRAY[0]}
for item in "${ARRAY[@]}"; do echo $item; done

# Associative arrays
declare -A MAP
MAP["key"]="value"
echo ${MAP["key"]}

# String manipulation
${VAR#pattern}      # Remove prefix
${VAR%pattern}      # Remove suffix
${VAR/old/new}      # Replace first
${VAR//old/new}     # Replace all

# Regex matching
if [[ "$VAR" =~ pattern ]]; then
    echo ${BASH_REMATCH[0]}
fi

# Error handling
set -euo pipefail
trap cleanup EXIT
trap 'error_handler ${LINENO}' ERR
```

---

**End of Lecture 06: Advanced Shell Scripting**

You now have advanced shell scripting skills for production AI infrastructure automation. These techniques enable you to write robust, maintainable scripts that handle real-world complexity.

**Next**: Lecture 07 - Text Processing Tools (grep, sed, awk)
