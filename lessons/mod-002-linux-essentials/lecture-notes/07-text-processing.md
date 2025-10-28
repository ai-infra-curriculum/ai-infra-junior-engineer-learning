# Lecture 07: Text Processing Tools

## Table of Contents
1. [Introduction](#introduction)
2. [grep: Pattern Matching](#grep-pattern-matching)
3. [sed: Stream Editing](#sed-stream-editing)
4. [awk: Text Processing and Reports](#awk-text-processing-and-reports)
5. [Combining Tools with Pipes](#combining-tools-with-pipes)
6. [AI Infrastructure Applications](#ai-infrastructure-applications)
7. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Text processing is essential for AI infrastructure engineers. You'll analyze training logs, parse metrics, process datasets, extract information from configuration files, and troubleshoot issues by searching through massive log files. The three core text processing tools—grep, sed, and awk—are the power tools of the command line.

This lecture teaches you to master these tools for real-world AI infrastructure tasks.

### Learning Objectives

By the end of this lecture, you will:
- Search files and logs efficiently with grep
- Transform text streams with sed
- Process structured data with awk
- Combine tools in powerful pipelines
- Apply text processing to ML log analysis
- Extract insights from training metrics
- Debug infrastructure issues through log analysis

### Prerequisites
- Lectures 01-06 (Linux fundamentals through advanced scripting)
- Comfort with command-line basics
- Understanding of regular expressions (helpful but not required)

### Why Text Processing for AI Infrastructure?

**Log Analysis**: Extract errors, warnings, and metrics from training logs
**Metrics Processing**: Parse and analyze model performance data
**Configuration Management**: Modify config files programmatically
**Data Preprocessing**: Clean and transform datasets
**Troubleshooting**: Debug issues by searching through logs
**Automation**: Process text in scripts and pipelines
**Reporting**: Generate summaries from raw data

**Duration**: 90 minutes
**Difficulty**: Intermediate

---

## grep: Pattern Matching

**grep** (Global Regular Expression Print) searches for patterns in text.

### Basic grep Syntax

```bash
grep [OPTIONS] PATTERN [FILE...]
```

### Simple Pattern Search

```bash
# Search for "error" in file
grep error training.log

# Search multiple files
grep error *.log

# Search all files recursively
grep -r error /var/log/

# Search from stdin (pipe)
cat training.log | grep error
```

### Essential grep Options

**-i**: Case-insensitive search
```bash
# Find "error", "Error", "ERROR", etc.
grep -i error training.log
```

**-v**: Invert match (show lines that DON'T match)
```bash
# Show lines without "DEBUG"
grep -v DEBUG application.log
```

**-n**: Show line numbers
```bash
# Show line numbers with matches
grep -n error training.log
# Output: 42:ERROR: Model failed to load
```

**-c**: Count matching lines
```bash
# Count error lines
grep -c error training.log
# Output: 15
```

**-l**: List files with matches (don't show the matches)
```bash
# Which log files contain errors?
grep -l error *.log
# Output: training.log api.log
```

**-r**: Recursive search
```bash
# Search all files in directory tree
grep -r "cuda error" /var/log/
```

**-A, -B, -C**: Context lines
```bash
# Show 3 lines AFTER match
grep -A 3 "ERROR" training.log

# Show 3 lines BEFORE match
grep -B 3 "ERROR" training.log

# Show 3 lines AROUND match (before AND after)
grep -C 3 "ERROR" training.log
```

**-w**: Match whole words only
```bash
# Match "train" but not "training" or "trainer"
grep -w train commands.log
```

**-o**: Show only the matched part
```bash
# Extract just the matched text
grep -o "[0-9]\+\.[0-9]\+" metrics.log
# Output: 0.95
#         0.87
#         0.92
```

### Regular Expressions with grep

**Basic regex patterns**:
```bash
# . - Any single character
grep "model.h5" files.log

# * - Zero or more of previous character
grep "erro*r" log.txt     # er, error, errrror

# ^ - Start of line
grep "^ERROR" log.txt     # Lines starting with ERROR

# $ - End of line
grep "success$" log.txt   # Lines ending with success

# [...] - Character class
grep "[Ee]rror" log.txt   # Error or error

# [^...] - Negated character class
grep "[^0-9]" log.txt     # Lines without numbers
```

**Extended regex** (use -E or egrep):
```bash
# + - One or more
grep -E "erro+r" log.txt

# ? - Zero or one
grep -E "colou?r" log.txt  # color or colour

# | - OR
grep -E "error|warning" log.txt

# () - Grouping
grep -E "(failed|error)" log.txt

# {n} - Exactly n times
grep -E "[0-9]{3}" log.txt  # 3 digits

# {n,m} - Between n and m times
grep -E "[0-9]{2,4}" log.txt  # 2-4 digits
```

### AI/ML Log Analysis Examples

**Find training errors**:
```bash
# All error lines
grep -i error training.log

# CUDA errors specifically
grep -i "cuda error" training.log

# Out of memory errors
grep -i "out of memory" training.log
grep -i "oom" training.log
```

**Extract metrics**:
```bash
# Find lines with accuracy
grep "accuracy" training.log

# Lines with epoch information
grep "Epoch [0-9]\+/" training.log

# Loss values
grep -o "loss: [0-9]\+\.[0-9]\+" training.log
```

**Filter by severity**:
```bash
# Only errors and critical
grep -E "ERROR|CRITICAL" application.log

# Exclude debug messages
grep -v DEBUG application.log

# Info, warning, and error (exclude debug)
grep -E "INFO|WARN|ERROR" application.log
```

**Search by timestamp**:
```bash
# Errors in specific hour
grep "2024-10-28 14:" training.log | grep ERROR

# Errors today
grep "$(date +%Y-%m-%d)" training.log | grep ERROR
```

**Find specific GPU issues**:
```bash
# GPU out of memory
grep -i "gpu.*memory" training.log

# GPU not found
grep -i "gpu.*not found" training.log

# CUDA version mismatch
grep -i "cuda.*version" training.log
```

### Practical Example: Analyze Training Log

```bash
#!/bin/bash
# analyze-training-log.sh

LOG_FILE="training.log"

echo "=== Training Log Analysis ==="
echo ""

# Total errors
ERROR_COUNT=$(grep -c ERROR "$LOG_FILE" || echo 0)
echo "Total errors: $ERROR_COUNT"

# Warnings
WARN_COUNT=$(grep -c WARNING "$LOG_FILE" || echo 0)
echo "Total warnings: $WARN_COUNT"

# Epochs completed
EPOCHS=$(grep -c "Epoch [0-9]\+/" "$LOG_FILE")
echo "Epochs completed: $EPOCHS"

# CUDA errors
CUDA_ERRORS=$(grep -c "cuda error" "$LOG_FILE" || echo 0)
if [ $CUDA_ERRORS -gt 0 ]; then
    echo ""
    echo "CUDA errors found: $CUDA_ERRORS"
    grep "cuda error" "$LOG_FILE"
fi

# OOM errors
OOM_ERRORS=$(grep -c -i "out of memory" "$LOG_FILE" || echo 0)
if [ $OOM_ERRORS -gt 0 ]; then
    echo ""
    echo "Out of memory errors: $OOM_ERRORS"
    grep -i "out of memory" "$LOG_FILE"
fi

# Last 5 errors
echo ""
echo "Last 5 errors:"
grep ERROR "$LOG_FILE" | tail -5
```

---

## sed: Stream Editing

**sed** (Stream EDitor) performs text transformations on streams.

### Basic sed Syntax

```bash
sed [OPTIONS] 'COMMAND' [FILE...]
```

### Substitution (Most Common Use)

**Basic substitution**:
```bash
# Replace first occurrence on each line
sed 's/old/new/' file.txt

# Replace all occurrences (g = global)
sed 's/old/new/g' file.txt

# Replace only on lines matching pattern
sed '/pattern/s/old/new/g' file.txt
```

**Substitution flags**:
```bash
# g - Global (all occurrences on line)
sed 's/error/ERROR/g' file.txt

# i - Case-insensitive
sed 's/error/ERROR/gi' file.txt

# 2 - Only 2nd occurrence
sed 's/old/new/2' file.txt

# p - Print lines where substitution occurred
sed -n 's/error/ERROR/p' file.txt
```

### In-Place Editing

**Edit files directly** (-i flag):
```bash
# Edit file in place
sed -i 's/old/new/g' file.txt

# Create backup with .bak extension
sed -i.bak 's/old/new/g' file.txt

# macOS requires empty string for no backup
sed -i '' 's/old/new/g' file.txt  # macOS
```

### Line Operations

**Delete lines**:
```bash
# Delete lines containing pattern
sed '/pattern/d' file.txt

# Delete lines 5-10
sed '5,10d' file.txt

# Delete first line
sed '1d' file.txt

# Delete last line
sed '$d' file.txt

# Delete empty lines
sed '/^$/d' file.txt

# Delete lines starting with #
sed '/^#/d' file.txt
```

**Print lines**:
```bash
# Print specific lines (use -n to suppress default)
sed -n '5,10p' file.txt      # Lines 5-10
sed -n '1p' file.txt          # First line
sed -n '$p' file.txt          # Last line

# Print lines matching pattern
sed -n '/pattern/p' file.txt

# Print every 2nd line
sed -n '1~2p' file.txt
```

**Insert and append**:
```bash
# Insert before line 5
sed '5i\New line here' file.txt

# Append after line 5
sed '5a\New line here' file.txt

# Insert before matching line
sed '/pattern/i\New line' file.txt

# Append after matching line
sed '/pattern/a\New line' file.txt
```

### Advanced Substitution

**Using different delimiters** (helpful with paths):
```bash
# Instead of s/\/old\/path/\/new\/path/g
# Use | or # as delimiter
sed 's|/old/path|/new/path|g' file.txt
sed 's#/old/path#/new/path#g' file.txt
```

**Capture groups and backreferences**:
```bash
# Swap two words
echo "first second" | sed 's/\(.*\) \(.*\)/\2 \1/'
# Output: second first

# Extract and reformat
echo "2024-10-28" | sed 's/\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\)/\3\/\2\/\1/'
# Output: 28/10/2024
```

**Multiple commands**:
```bash
# Use -e for multiple commands
sed -e 's/old1/new1/g' -e 's/old2/new2/g' file.txt

# Or use semicolons
sed 's/old1/new1/g; s/old2/new2/g' file.txt

# Or newlines
sed '
s/old1/new1/g
s/old2/new2/g
' file.txt
```

### AI/ML Configuration Examples

**Update model paths**:
```bash
# Update model path in config
sed -i 's|/models/old|/models/new|g' config.yaml

# Update multiple paths
sed -i '
s|/data/train|/datasets/training|g
s|/data/val|/datasets/validation|g
s|/data/test|/datasets/testing|g
' config.yaml
```

**Modify hyperparameters**:
```bash
# Change learning rate
sed -i 's/learning_rate: 0.001/learning_rate: 0.0001/' config.yaml

# Update batch size
sed -i 's/batch_size: 32/batch_size: 64/' config.yaml

# Enable GPU
sed -i 's/use_gpu: false/use_gpu: true/' config.yaml
```

**Clean log files**:
```bash
# Remove ANSI color codes
sed 's/\x1b\[[0-9;]*m//g' colored.log > clean.log

# Remove timestamps
sed 's/^[0-9-]\+ [0-9:]\+ //' log.txt

# Remove debug lines
sed '/DEBUG/d' log.txt > filtered.log

# Extract only errors
sed -n '/ERROR/p' log.txt > errors.log
```

**Format metrics**:
```bash
# Convert scientific notation
echo "loss: 1.234e-03" | sed 's/\([0-9]\+\.[0-9]\+\)e-\([0-9]\+\)/0.00\1/'

# Add commas to numbers
echo "1000000" | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta'
# Output: 1,000,000

# Round percentages
sed 's/\([0-9]\+\)\.[0-9]\+%/\1%/g' metrics.txt
```

### Practical Example: Config File Update Script

```bash
#!/bin/bash
# update-training-config.sh

CONFIG_FILE="training_config.yaml"
BACKUP_FILE="${CONFIG_FILE}.backup"

# Create backup
cp "$CONFIG_FILE" "$BACKUP_FILE"

echo "Updating training configuration..."

# Update learning rate
sed -i 's/learning_rate: 0.001/learning_rate: 0.0001/' "$CONFIG_FILE"
echo "✓ Learning rate updated to 0.0001"

# Update batch size
sed -i 's/batch_size: 32/batch_size: 64/' "$CONFIG_FILE"
echo "✓ Batch size updated to 64"

# Update model path
sed -i 's|model_path: /models/v1|model_path: /models/v2|' "$CONFIG_FILE"
echo "✓ Model path updated to /models/v2"

# Enable mixed precision
sed -i 's/mixed_precision: false/mixed_precision: true/' "$CONFIG_FILE"
echo "✓ Mixed precision enabled"

echo ""
echo "Configuration updated successfully"
echo "Backup saved to: $BACKUP_FILE"
```

---

## awk: Text Processing and Reports

**awk** is a powerful pattern scanning and processing language.

### Basic awk Syntax

```bash
awk 'PATTERN {ACTION}' file.txt
```

### Field Processing

**Default field separator is whitespace**:
```bash
# Print first field
echo "one two three" | awk '{print $1}'
# Output: one

# Print multiple fields
echo "one two three" | awk '{print $1, $3}'
# Output: one three

# Print all fields
echo "one two three" | awk '{print $0}'
# Output: one two three

# Print last field
echo "one two three" | awk '{print $NF}'
# Output: three

# Print second-to-last field
echo "one two three" | awk '{print $(NF-1)}'
# Output: two
```

**Custom field separator** (-F flag):
```bash
# CSV file (comma-separated)
echo "name,age,city" | awk -F',' '{print $1, $2}'
# Output: name age

# Colon-separated (/etc/passwd)
awk -F':' '{print $1, $3}' /etc/passwd

# Multiple separators
awk -F'[:,]' '{print $1}' file.txt
```

### Built-in Variables

**Common awk variables**:
```bash
# NR - Number of Records (current line number)
awk '{print NR, $0}' file.txt

# NF - Number of Fields (fields in current line)
awk '{print NF}' file.txt

# FS - Field Separator (input)
awk -v FS=',' '{print $1}' file.txt

# OFS - Output Field Separator
awk 'BEGIN {OFS=","} {print $1, $2}' file.txt

# FILENAME - Current filename
awk '{print FILENAME, $0}' file1.txt file2.txt
```

### Pattern Matching

```bash
# Print lines matching pattern
awk '/pattern/' file.txt

# Print if field matches
awk '$1 == "value"' file.txt

# Numeric comparison
awk '$3 > 100' file.txt

# Multiple conditions
awk '$1 == "ERROR" && $3 > 100' file.txt

# Regex match
awk '$2 ~ /pattern/' file.txt

# Negated regex match
awk '$2 !~ /pattern/' file.txt
```

### Calculations and Reports

**Arithmetic operations**:
```bash
# Add values in column 3
awk '{sum += $3} END {print sum}' numbers.txt

# Average
awk '{sum += $1; count++} END {print sum/count}' numbers.txt

# Find maximum
awk 'BEGIN {max=0} {if($1>max) max=$1} END {print max}' numbers.txt

# Find minimum
awk 'BEGIN {min=999999} {if($1<min) min=$1} END {print min}' numbers.txt
```

**Counting and grouping**:
```bash
# Count occurrences
awk '{count[$1]++} END {for(word in count) print word, count[word]}' file.txt

# Sum by category
awk '{sum[$1] += $2} END {for(cat in sum) print cat, sum[cat]}' file.txt
```

### AI/ML Log Analysis with awk

**Extract training metrics**:
```bash
# Extract epoch and loss
awk '/Epoch/ {print $2, $NF}' training.log

# Extract accuracy from specific format
# Example: "Epoch 10/100 - loss: 0.1234 - acc: 0.9876"
awk -F': ' '/acc:/ {print $NF}' training.log

# Calculate average loss
awk '/loss:/ {sum += $NF; count++} END {print "Avg loss:", sum/count}' training.log
```

**Parse GPU metrics**:
```bash
# nvidia-smi output processing
nvidia-smi --query-gpu=index,utilization.gpu,memory.used \
  --format=csv,noheader | \
  awk -F, '{print "GPU " $1 ": " $2 " util, " $3 " memory"}'

# Average GPU utilization
nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | \
  awk '{sum += $1; count++} END {print "Avg GPU util:", sum/count "%"}'
```

**Analyze API logs**:
```bash
# Count requests by endpoint
awk '{print $7}' access.log | sort | uniq -c | sort -rn

# Average response time
awk '{sum += $10; count++} END {print "Avg response:", sum/count "ms"}' api.log

# Requests per minute
awk -F: '{print $1":"$2}' access.log | uniq -c
```

**Process CSV data**:
```bash
# Calculate statistics from metrics.csv
awk -F',' '
NR>1 {
    sum_loss += $2
    sum_acc += $3
    count++
}
END {
    print "Average Loss:", sum_loss/count
    print "Average Accuracy:", sum_acc/count
}
' metrics.csv
```

### Advanced awk Features

**BEGIN and END blocks**:
```bash
awk '
BEGIN {
    print "Starting processing..."
    sum = 0
}
{
    sum += $1
}
END {
    print "Total:", sum
    print "Average:", sum/NR
}
' numbers.txt
```

**Conditional actions**:
```bash
awk '
{
    if ($3 > 90)
        print $1, "excellent"
    else if ($3 > 70)
        print $1, "good"
    else
        print $1, "needs improvement"
}
' scores.txt
```

**Arrays in awk**:
```bash
# Count word frequency
awk '
{
    for(i=1; i<=NF; i++)
        words[$i]++
}
END {
    for(word in words)
        print word, words[word]
}
' file.txt
```

### Practical Example: Training Metrics Report

```bash
#!/bin/bash
# generate-training-report.sh

LOG_FILE="training.log"

echo "=== Training Metrics Report ==="
echo ""

# Extract metrics and generate report
awk '
BEGIN {
    epoch_count = 0
    total_loss = 0
    total_acc = 0
    min_loss = 999999
    max_acc = 0
}

# Match epoch lines: "Epoch 10/100 - loss: 0.1234 - acc: 0.9876"
/Epoch [0-9]+\// {
    # Extract values using field positions or regex
    for(i=1; i<=NF; i++) {
        if($i ~ /loss:/) {
            loss = $(i+1)
            total_loss += loss
            if(loss < min_loss) min_loss = loss
        }
        if($i ~ /acc:/) {
            acc = $(i+1)
            total_acc += acc
            if(acc > max_acc) max_acc = acc
        }
    }
    epoch_count++
}

END {
    if(epoch_count > 0) {
        print "Total Epochs:", epoch_count
        print "Average Loss:", total_loss/epoch_count
        print "Average Accuracy:", total_acc/epoch_count
        print "Best Loss:", min_loss
        print "Best Accuracy:", max_acc
        print ""
        print "Training Trend:"
        if(min_loss < 0.1)
            print "  Loss: Excellent convergence"
        else if(min_loss < 0.5)
            print "  Loss: Good convergence"
        else
            print "  Loss: May need more training"

        if(max_acc > 0.95)
            print "  Accuracy: Excellent performance"
        else if(max_acc > 0.80)
            print "  Accuracy: Good performance"
        else
            print "  Accuracy: Needs improvement"
    } else {
        print "No epoch data found in log file"
    }
}
' "$LOG_FILE"
```

---

## Combining Tools with Pipes

The real power comes from combining grep, sed, and awk in pipelines.

### Simple Pipelines

**Filter then extract**:
```bash
# Find errors, extract timestamps
grep ERROR log.txt | awk '{print $1, $2}'

# Find GPU lines, extract GPU ID
grep GPU log.txt | sed 's/.*GPU \([0-9]\+\).*/\1/'

# Count error types
grep ERROR log.txt | awk '{print $3}' | sort | uniq -c
```

**Transform then analyze**:
```bash
# Clean data, then calculate
sed 's/[^0-9.]//g' metrics.txt | awk '{sum+=$1} END {print sum}'

# Extract values, sort, show top 10
grep "accuracy:" log.txt | awk '{print $NF}' | sort -rn | head -10
```

### Complex Analysis Pipelines

**Analyze training performance**:
```bash
#!/bin/bash
# Analyze last 24 hours of training

# Extract recent epochs, calculate statistics
grep "$(date +%Y-%m-%d)" training.log | \
grep "Epoch" | \
awk -F': ' '{print $2, $4}' | \
awk '{loss+=$1; acc+=$2; count++} END {
    print "Last 24 hours:"
    print "  Epochs:", count
    print "  Avg Loss:", loss/count
    print "  Avg Accuracy:", acc/count
}'
```

**Find bottlenecks**:
```bash
#!/bin/bash
# Find slowest training steps

grep "step_time" training.log | \
awk '{print $5}' | \
sort -rn | \
head -10 | \
awk '{
    sum+=$1
    print "  Slow step:", $1 "s"
}
END {
    print "  Total time in slow steps:", sum "s"
}'
```

**API performance analysis**:
```bash
#!/bin/bash
# Analyze API response times

cat api_access.log | \
awk '{print $7, $11}' | \          # endpoint, response_time
grep -v "^$" | \                   # remove empty lines
awk '{
    sum[$1] += $2
    count[$1]++
}
END {
    print "Average Response Times:"
    for(endpoint in sum)
        printf "  %s: %.2fms\n", endpoint, sum[endpoint]/count[endpoint]
}' | \
sort -k2 -rn                        # sort by time
```

### Advanced Pipeline: Log Analysis Tool

```bash
#!/bin/bash
# comprehensive-log-analysis.sh

LOG_FILE="$1"

if [ -z "$LOG_FILE" ]; then
    echo "Usage: $0 <log_file>"
    exit 1
fi

echo "=== Comprehensive Log Analysis ==="
echo "File: $LOG_FILE"
echo ""

# Timeline Analysis
echo "## Timeline"
grep -E "ERROR|WARN" "$LOG_FILE" | \
awk '{print $1, $2}' | \
awk -F: '{print $1":"$2}' | \
sort | uniq -c | \
awk '{printf "  %s: %d events\n", $2, $1}'
echo ""

# Error Analysis
echo "## Error Distribution"
grep ERROR "$LOG_FILE" | \
awk '{
    for(i=3; i<=NF; i++)
        if($i ~ /^[A-Z]/)
            errors[$i]++
}
END {
    for(e in errors)
        printf "  %s: %d occurrences\n", e, errors[e]
}' | \
sort -t: -k2 -rn | \
head -10
echo ""

# Performance Metrics
echo "## Performance Metrics"
grep -E "time:|duration:" "$LOG_FILE" | \
sed 's/.*time: \([0-9.]\+\).*/\1/' | \
awk '{
    sum+=$1
    if(NR==1) min=max=$1
    if($1<min) min=$1
    if($1>max) max=$1
    count++
}
END {
    if(count>0) {
        print "  Count:", count
        printf "  Average: %.2fs\n", sum/count
        printf "  Min: %.2fs\n", min
        printf "  Max: %.2fs\n", max
    }
}'
echo ""

# Resource Usage
echo "## Resource Usage Patterns"
grep -E "memory|cpu|gpu" "$LOG_FILE" | \
awk '{
    if($0 ~ /memory/)
        mem++
    if($0 ~ /cpu/)
        cpu++
    if($0 ~ /gpu/)
        gpu++
}
END {
    print "  Memory events:", mem
    print "  CPU events:", cpu
    print "  GPU events:", gpu
}'
```

---

## AI Infrastructure Applications

### Use Case 1: Parse TensorFlow Training Logs

```bash
#!/bin/bash
# parse-tf-logs.sh

LOG_FILE="$1"

echo "=== TensorFlow Training Analysis ==="

# Extract epoch metrics
awk '
/Epoch [0-9]+\// {
    epoch = $2
    sub(/\/.*/, "", epoch)

    for(i=1; i<=NF; i++) {
        if($i == "loss:") loss = $(i+1)
        if($i == "accuracy:") acc = $(i+1)
        if($i == "val_loss:") val_loss = $(i+1)
        if($i == "val_accuracy:") val_acc = $(i+1)
    }

    printf "Epoch %d: loss=%.4f acc=%.4f val_loss=%.4f val_acc=%.4f\n",
           epoch, loss, acc, val_loss, val_acc

    sum_loss += loss
    sum_acc += acc
    count++
}

END {
    print ""
    print "Summary:"
    printf "  Average Loss: %.4f\n", sum_loss/count
    printf "  Average Accuracy: %.4f\n", sum_acc/count
}
' "$LOG_FILE"
```

### Use Case 2: Monitor Distributed Training

```bash
#!/bin/bash
# monitor-distributed-training.sh

# Collect logs from all workers
WORKERS=(worker1 worker2 worker3 worker4)

echo "=== Distributed Training Status ==="
echo ""

for worker in "${WORKERS[@]}"; do
    echo "## $worker"

    # Get latest status
    ssh "$worker" "tail -100 /var/log/training.log" | \
    grep -E "Epoch|ERROR|WARN" | \
    tail -5

    # Get resource usage
    ssh "$worker" "nvidia-smi --query-gpu=utilization.gpu,memory.used \
        --format=csv,noheader" | \
    awk -F, -v worker="$worker" '{
        printf "  GPU: %s util, %s memory\n", $1, $2
    }'

    echo ""
done

# Aggregate metrics
echo "## Aggregate Statistics"
for worker in "${WORKERS[@]}"; do
    ssh "$worker" "tail -1000 /var/log/training.log"
done | \
grep "step_time" | \
awk '{sum+=$NF; count++} END {
    printf "  Average step time: %.2fs\n", sum/count
    printf "  Total steps: %d\n", count
}'
```

### Use Case 3: Generate Training Report

```bash
#!/bin/bash
# generate-training-report.sh

EXPERIMENT_DIR="$1"
OUTPUT_FILE="$EXPERIMENT_DIR/report.txt"

{
    echo "# Training Report"
    echo "Generated: $(date)"
    echo "Experiment: $EXPERIMENT_DIR"
    echo ""

    # Configuration
    echo "## Configuration"
    grep -E "model|learning_rate|batch_size|epochs" \
        "$EXPERIMENT_DIR/config.yaml" | \
    sed 's/^/  /'
    echo ""

    # Training Progress
    echo "## Training Progress"
    awk '
    /Epoch [0-9]+\// {
        epoch=$2
        sub(/\/.*/, "", epoch)
        for(i=1; i<=NF; i++) {
            if($i=="loss:") loss=$(i+1)
            if($i=="acc:") acc=$(i+1)
        }
        if(epoch % 10 == 0 || epoch==1)
            printf "  Epoch %3d: loss=%.4f acc=%.4f\n", epoch, loss, acc
    }
    ' "$EXPERIMENT_DIR/training.log"
    echo ""

    # Final Metrics
    echo "## Final Metrics"
    tail -1 "$EXPERIMENT_DIR/training.log" | \
    awk '{
        for(i=1; i<=NF; i++) {
            if($i=="loss:") printf "  Training Loss: %s\n", $(i+1)
            if($i=="val_loss:") printf "  Validation Loss: %s\n", $(i+1)
            if($i=="acc:") printf "  Training Accuracy: %s\n", $(i+1)
            if($i=="val_acc:") printf "  Validation Accuracy: %s\n", $(i+1)
        }
    }'
    echo ""

    # Errors and Warnings
    echo "## Issues"
    ERROR_COUNT=$(grep -c ERROR "$EXPERIMENT_DIR/training.log" || echo 0)
    WARN_COUNT=$(grep -c WARN "$EXPERIMENT_DIR/training.log" || echo 0)
    echo "  Errors: $ERROR_COUNT"
    echo "  Warnings: $WARN_COUNT"

    if [ $ERROR_COUNT -gt 0 ]; then
        echo ""
        echo "  Recent Errors:"
        grep ERROR "$EXPERIMENT_DIR/training.log" | tail -5 | sed 's/^/    /'
    fi

} > "$OUTPUT_FILE"

echo "Report generated: $OUTPUT_FILE"
cat "$OUTPUT_FILE"
```

---

## Summary and Key Takeaways

### Tools Mastered

**grep - Pattern Matching**:
- Search files for patterns
- Regular expressions
- Context lines (-A, -B, -C)
- Recursive search (-r)
- Count matches (-c)
- Case-insensitive (-i)

**sed - Stream Editing**:
- Substitution (s/old/new/g)
- In-place editing (-i)
- Delete lines (d)
- Insert/append (i, a)
- Multiple commands
- Regular expressions

**awk - Text Processing**:
- Field processing ($1, $2, $NF)
- Pattern-action paradigm
- Built-in variables (NR, NF, FS)
- Arithmetic operations
- Arrays and loops
- Reports and summaries

### Key Concepts

1. **Pipelines**: Chain tools for powerful text processing
2. **Patterns**: Match and extract specific information
3. **Fields**: Process structured data column by column
4. **Transformations**: Modify text programmatically
5. **Aggregation**: Calculate statistics and summaries

### AI Infrastructure Applications

**Log Analysis**:
- Extract errors and warnings
- Parse training metrics
- Identify performance bottlenecks
- Monitor resource usage

**Data Processing**:
- Clean datasets
- Transform formats
- Extract features
- Generate reports

**Automation**:
- Process logs in scripts
- Generate alerts
- Create dashboards
- Automate reporting

### Best Practices

✅ **Start simple**: Basic grep before complex awk
✅ **Test incrementally**: Build pipelines step by step
✅ **Use appropriate tool**: grep for search, sed for replace, awk for reports
✅ **Quote patterns**: Prevent shell interpretation
✅ **Save intermediate results**: Debug complex pipelines
✅ **Comment regex**: Document complex patterns
✅ **Use -n with sed**: Explicit printing for clarity
✅ **Name awk variables**: Readable code over brevity

### Common Patterns

```bash
# Search and count
grep pattern file.txt | wc -l

# Extract and analyze
grep pattern file.txt | awk '{print $3}' | sort | uniq -c

# Filter and transform
grep ERROR log.txt | sed 's/ERROR://' | awk '{print $1, $2}'

# Calculate metrics
awk '/metric/ {sum+=$2; count++} END {print sum/count}' log.txt

# Generate report
{
    echo "Report:"
    grep metric log.txt | awk '{print "  " $0}'
} > report.txt
```

### Next Steps

In **Lecture 08: Networking Fundamentals**, you'll learn:
- TCP/IP networking basics
- Network configuration
- SSH and remote access
- Network troubleshooting
- AI infrastructure networking

### Quick Reference

```bash
# grep
grep pattern file.txt           # Search
grep -i pattern file.txt        # Case-insensitive
grep -r pattern dir/            # Recursive
grep -n pattern file.txt        # Line numbers
grep -A 3 pattern file.txt      # 3 lines after
grep -E 'pat1|pat2' file.txt    # Extended regex

# sed
sed 's/old/new/g' file.txt      # Replace all
sed -i 's/old/new/g' file.txt   # In-place
sed '/pattern/d' file.txt       # Delete lines
sed -n '10,20p' file.txt        # Print lines 10-20

# awk
awk '{print $1}' file.txt       # First field
awk -F: '{print $1}' file.txt   # Custom separator
awk '$3 > 100' file.txt         # Filter
awk '{sum+=$1} END {print sum}' # Sum column

# Pipelines
grep ERROR log.txt | awk '{print $1}' | sort | uniq -c
```

---

**End of Lecture 07: Text Processing Tools**

You now have powerful text processing skills for analyzing logs, processing data, and automating AI infrastructure tasks. These tools are essential for day-to-day operations.

**Next**: Lecture 08 - Networking Fundamentals
