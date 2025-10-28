# Exercise 01: Linux Navigation and File System Mastery

## Overview

This exercise builds practical skills in Linux file system navigation, file operations, and directory management. You'll create a complete ML project structure, navigate efficiently, and manage files like a professional AI infrastructure engineer.

## Learning Objectives

By completing this exercise, you will:
- Navigate the Linux file system confidently using cd, ls, pwd
- Create directory structures for ML projects
- Perform file operations (copy, move, delete) safely
- Use find and locate to search for files
- Create and manage symbolic links
- Apply best practices for ML project organization

## Prerequisites

- Completed Lecture 01: Introduction to Linux and Command Line
- Completed Lecture 02: File System and Navigation
- Access to a Linux system (VM, WSL, or cloud instance)
- Terminal emulator
- At least 1GB free disk space

## Time Required

- Estimated: 60-90 minutes
- Difficulty: Beginner

## Part 1: Setup and Environment Exploration

### Step 1: Verify Your Environment

```bash
# Check your current location
pwd

# List your home directory contents
ls -la ~

# Check available disk space
df -h ~

# Verify you have necessary permissions
touch /tmp/test_file && rm /tmp/test_file && echo "Permissions OK" || echo "Permission issue"
```

**Expected Output**:
- Current working directory path
- List of files in home directory
- Available disk space
- "Permissions OK" message

**Validation**:
- [ ] pwd shows your current directory
- [ ] ls shows files and hidden files (starting with .)
- [ ] df shows at least 1GB free space
- [ ] Permission test succeeds

### Step 2: Explore the File System

```bash
# View the root directory structure
ls -l /

# Explore common directories
ls -l /etc       # Configuration files
ls -l /var/log   # Log files
ls -l /usr/bin   # User binaries
ls -l /opt       # Optional software

# Find your home directory in the hierarchy
cd ~
pwd
echo $HOME
```

**Questions to Answer**:
1. What is the full path to your home directory?
2. How many directories are in the root (/) directory?
3. What user owns the files in /etc?
4. What is the total size of /var/log?

**Answers** (record in notebook):
```
1. Home directory: _______________
2. Number of root directories: ___
3. Owner of /etc files: __________
4. Size of /var/log: ______________
```

## Part 2: Creating ML Project Structure

### Step 3: Build Standard ML Project Layout

Create a professional ML project structure:

```bash
# Navigate to home directory
cd ~

# Create project root
mkdir -p projects/ml-image-classifier

# Navigate into project
cd projects/ml-image-classifier

# Create complete directory structure
mkdir -p data/{raw,processed,external}
mkdir -p models/{checkpoints,final,experiments}
mkdir -p notebooks
mkdir -p src/{data,models,training,evaluation,utils}
mkdir -p tests
mkdir -p logs
mkdir -p configs
mkdir -p scripts
mkdir -p docs

# Verify structure
tree -L 2
# or if tree not installed:
find . -type d | sort
```

**Expected Structure**:
```
ml-image-classifier/
├── configs/
├── data/
│   ├── external/
│   ├── processed/
│   └── raw/
├── docs/
├── logs/
├── models/
│   ├── checkpoints/
│   ├── experiments/
│   └── final/
├── notebooks/
├── scripts/
├── src/
│   ├── data/
│   ├── evaluation/
│   ├── models/
│   ├── training/
│   └── utils/
└── tests/
```

**Validation**:
```bash
# Count directories created
find . -type d | wc -l
# Should be 19 (including root directory)

# Verify specific directories exist
test -d data/raw && echo "✓ data/raw exists" || echo "✗ Missing data/raw"
test -d src/training && echo "✓ src/training exists" || echo "✗ Missing src/training"
test -d models/checkpoints && echo "✓ models/checkpoints exists" || echo "✗ Missing"
```

**Checkpoint**: You should have 18 subdirectories plus the root directory.

### Step 4: Create Project Files

```bash
# Create README files
echo "# ML Image Classifier Project" > README.md
echo "Raw dataset storage - immutable" > data/raw/README.md
echo "Processed datasets ready for training" > data/processed/README.md
echo "Training checkpoints - autosaved during training" > models/checkpoints/README.md

# Create Python package markers
touch src/__init__.py
touch src/data/__init__.py
touch src/models/__init__.py
touch src/training/__init__.py
touch src/evaluation/__init__.py
touch src/utils/__init__.py

# Create configuration files
cat > configs/default.yaml << 'EOF'
# Default configuration
model:
  architecture: resnet50
  input_shape: [224, 224, 3]
  num_classes: 10

training:
  batch_size: 32
  epochs: 100
  learning_rate: 0.001

data:
  train_path: data/processed/train
  val_path: data/processed/val
  test_path: data/processed/test
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Virtual environments
venv/
env/
ENV/

# Jupyter
.ipynb_checkpoints/

# Data and models
data/raw/*
data/processed/*
!data/raw/README.md
!data/processed/README.md
models/checkpoints/*
models/experiments/*
!models/checkpoints/.gitkeep
logs/*.log

# IDE
.vscode/
.idea/
*.swp
EOF

# Create placeholder files
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch models/checkpoints/.gitkeep
touch logs/.gitkeep

# Create requirements.txt
cat > requirements.txt << 'EOF'
numpy==1.24.3
pandas==2.0.3
tensorflow==2.13.0
scikit-learn==1.3.0
matplotlib==3.7.2
pyyaml==6.0.1
tqdm==4.66.1
EOF
```

**Validation**:
```bash
# Verify files created
ls -1
# README.md, configs/, data/, docs/, etc.

# Count all files (not directories)
find . -type f | wc -l
# Should be at least 15 files

# Verify specific files
test -f README.md && echo "✓ README.md exists"
test -f configs/default.yaml && echo "✓ Config exists"
test -f requirements.txt && echo "✓ Requirements exists"
test -f .gitignore && echo "✓ .gitignore exists"
```

## Part 3: Navigation Practice

### Step 5: Efficient Navigation

Practice moving around your project structure efficiently.

```bash
# Return to project root
cd ~/projects/ml-image-classifier

# Navigate to specific directories using absolute paths
cd /home/$USER/projects/ml-image-classifier/src/training
pwd

# Navigate using relative paths
cd ../../data/raw
pwd

# Use shortcuts
cd ~                    # Home directory
cd -                    # Previous directory (toggle)
cd ../processed         # Parent, then sibling
cd ../../..             # Up 3 levels

# Practice navigation challenge:
cd ~/projects/ml-image-classifier
cd notebooks
cd ../src/models
cd ../../configs
cd ../logs
pwd                     # Should be in logs/
```

**Navigation Quiz**:

Starting from `~/projects/ml-image-classifier/src/training/`:

1. Navigate to `data/raw` using relative path:
   ```bash
   cd _______________
   ```

2. Navigate to `models/final` using relative path:
   ```bash
   cd _______________
   ```

3. Return to project root using absolute path:
   ```bash
   cd _______________
   ```

**Answers**:
```bash
1. cd ../../data/raw
2. cd ../../models/final  (from data/raw)
3. cd ~/projects/ml-image-classifier
```

### Step 6: Advanced Listing

Master the `ls` command with various options:

```bash
# Return to project root
cd ~/projects/ml-image-classifier

# List all files including hidden
ls -la

# List with human-readable sizes
ls -lh

# List sorted by modification time (newest first)
ls -lt

# List sorted by size (largest first)
ls -lhS

# Recursive list of all files
ls -R

# List only directories
ls -d */

# List with file type indicators
ls -F
# / = directory, * = executable, @ = link

# Combine options
ls -lhSr               # Long, human-readable, by size, reversed

# Practice: Find the largest file in your project
find . -type f -exec ls -lh {} \; | sort -k5 -hr | head -5
```

**Validation Tasks**:
1. List all `.yaml` files:
   ```bash
   ls **/*.yaml
   # or
   find . -name "*.yaml"
   ```

2. List all Python files with details:
   ```bash
   ls -lh **/*.py
   ```

3. Count total files in project:
   ```bash
   find . -type f | wc -l
   ```

## Part 4: File Operations

### Step 7: Copying and Moving Files

```bash
# Return to project root
cd ~/projects/ml-image-classifier

# Create sample training script
cat > src/training/train.py << 'EOF'
#!/usr/bin/env python3
"""Training script for ML model"""

import yaml
import numpy as np

def main():
    print("Training started...")
    # Training code here
    print("Training completed!")

if __name__ == "__main__":
    main()
EOF

# Make it executable
chmod +x src/training/train.py

# Copy configuration for experiments
cp configs/default.yaml configs/experiment_001.yaml

# Modify experiment config
sed -i 's/resnet50/vgg16/' configs/experiment_001.yaml
sed -i 's/epochs: 100/epochs: 50/' configs/experiment_001.yaml

# Create more experiment configs
cp configs/experiment_001.yaml configs/experiment_002.yaml
sed -i 's/vgg16/inception_v3/' configs/experiment_002.yaml

# Copy training script for different experiment
cp src/training/train.py src/training/train_distributed.py

# Move to scripts directory for deployment
cp src/training/train.py scripts/deploy_training.py

# Backup configuration
mkdir -p configs/backups
cp configs/*.yaml configs/backups/

# Create versioned backup
cp configs/default.yaml configs/backups/default_$(date +%Y%m%d).yaml
```

**Validation**:
```bash
# Verify copies
ls -l configs/
ls -l configs/backups/
ls -l src/training/
ls -l scripts/

# Count config files
ls configs/*.yaml | wc -l
# Should be 3 (default, experiment_001, experiment_002)

# Verify experiment configs are different
diff configs/default.yaml configs/experiment_001.yaml
```

### Step 8: Safe Deletion

```bash
# Create temporary files for practice
mkdir -p /tmp/ml-practice
cd /tmp/ml-practice

# Create test files
touch file1.txt file2.txt file3.log
mkdir test_dir
touch test_dir/nested.txt

# Safe deletion with confirmation
rm -i file1.txt
# Prompts: remove regular empty file 'file1.txt'? y

# Delete files by pattern
rm *.log

# Delete directory and contents
rm -r test_dir

# PRACTICE SAFE DELETION IN YOUR PROJECT
cd ~/projects/ml-image-classifier

# Create temporary experiment
mkdir -p models/experiments/failed_experiment_001
touch models/experiments/failed_experiment_001/model.h5

# Verify before deleting
ls -R models/experiments/

# Delete failed experiment
rm -rf models/experiments/failed_experiment_001

# Verify deletion
ls models/experiments/
```

**Safety Exercise**:
```bash
# Create a "recycle bin" instead of direct deletion
mkdir -p ~/.trash

# Create alias for safer deletion
alias trash='mv --target-directory=$HOME/.trash'

# Use trash instead of rm
cd ~/projects/ml-image-classifier
touch temp_file.txt
trash temp_file.txt

# Verify it's in trash
ls ~/.trash/

# Restore if needed
mv ~/.trash/temp_file.txt .

# Periodically clean trash
find ~/.trash -mtime +30 -delete
```

## Part 5: Finding Files

### Step 9: Using find

```bash
cd ~/projects/ml-image-classifier

# Find all Python files
find . -name "*.py"

# Find all YAML files
find . -name "*.yaml"

# Find all README files
find . -name "README.md"

# Find empty directories
find . -type d -empty

# Find files modified in last day
find . -type f -mtime -1

# Find large files (>1MB)
find . -type f -size +1M

# Find and execute command
find . -name "*.py" -exec wc -l {} \;

# Find Python files and count lines
find . -name "*.py" -exec cat {} \; | wc -l

# Find and delete __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Find files with specific permissions
find . -type f -perm 644
```

**Practice Tasks**:

1. Find all `.md` files and list with sizes:
   ```bash
   find . -name "*.md" -exec ls -lh {} \;
   ```

2. Find all files in `src/` directory:
   ```bash
   find src/ -type f
   ```

3. Count total Python files:
   ```bash
   find . -name "*.py" -type f | wc -l
   ```

### Step 10: Working with Links

```bash
cd ~/projects/ml-image-classifier

# Create symlink to current best model (initially empty)
ln -s models/final/resnet50_best.h5 current_model.h5

# Create symlink to data directory for quick access
ln -s data/processed ~/ml-data

# Create symlink to configs
ln -s ~/projects/ml-image-classifier/configs ~/ml-configs

# Verify links
ls -l current_model.h5
ls -l ~/ml-data
ls -l ~/ml-configs

# Test link functionality
ls ~/ml-data/
# Should show contents of data/processed/

# Update link to point to new model
rm current_model.h5
ln -s models/final/vgg16_best.h5 current_model.h5

# Create link to latest experiment config
ln -s configs/experiment_002.yaml latest_config.yaml

# List all symbolic links in project
find . -type l -ls
```

**Validation**:
```bash
# Verify links work
test -L current_model.h5 && echo "✓ current_model.h5 is a link"
test -L ~/ml-data && echo "✓ ~/ml-data is a link"

# Show link targets
readlink current_model.h5
readlink ~/ml-data
```

## Part 6: Advanced Challenges

### Challenge 1: Project Statistics

Write a script to gather project statistics:

```bash
cat > scripts/project_stats.sh << 'EOF'
#!/bin/bash

echo "=== ML Project Statistics ==="
echo ""
echo "Total directories: $(find . -type d | wc -l)"
echo "Total files: $(find . -type f | wc -l)"
echo "Python files: $(find . -name "*.py" | wc -l)"
echo "Config files: $(find . -name "*.yaml" -o -name "*.yml" | wc -l)"
echo "Markdown files: $(find . -name "*.md" | wc -l)"
echo ""
echo "Lines of Python code: $(find . -name "*.py" -exec cat {} \; | wc -l)"
echo ""
echo "Disk usage: $(du -sh . | cut -f1)"
EOF

chmod +x scripts/project_stats.sh
./scripts/project_stats.sh
```

### Challenge 2: Backup Script

Create a backup script:

```bash
cat > scripts/backup_project.sh << 'EOF'
#!/bin/bash

PROJECT_ROOT="$HOME/projects/ml-image-classifier"
BACKUP_DIR="$HOME/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="ml-classifier_${DATE}.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_NAME"

tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
    --exclude='models/checkpoints/*' \
    --exclude='models/experiments/*' \
    --exclude='data/raw/*' \
    --exclude='data/processed/*' \
    --exclude='__pycache__' \
    --exclude='.ipynb_checkpoints' \
    -C "$HOME/projects" \
    ml-image-classifier

echo "Backup created: $BACKUP_DIR/$BACKUP_NAME"
ls -lh "$BACKUP_DIR/$BACKUP_NAME"
EOF

chmod +x scripts/backup_project.sh
./scripts/backup_project.sh
```

### Challenge 3: Cleanup Script

Create a cleanup script for temporary files:

```bash
cat > scripts/cleanup.sh << 'EOF'
#!/bin/bash

echo "Cleaning up project..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove Jupyter checkpoints
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null

# Remove old logs (older than 30 days)
find logs/ -name "*.log" -mtime +30 -delete 2>/dev/null

# Remove temporary files
find . -name "*.tmp" -delete
find . -name "*.bak" -delete

# Remove empty directories
find . -type d -empty -delete

echo "Cleanup complete!"
EOF

chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

## Final Validation

### Verification Checklist

Run these commands to verify your work:

```bash
cd ~/projects/ml-image-classifier

# 1. Check directory structure
echo "=== Directory Structure ==="
tree -L 2 || find . -type d | sort

# 2. Check file count
echo "=== File Statistics ==="
echo "Total files: $(find . -type f | wc -l)"
echo "Python files: $(find . -name "*.py" | wc -l)"
echo "Config files: $(find . -name "*.yaml" | wc -l)"

# 3. Check scripts are executable
echo "=== Executable Scripts ==="
ls -l scripts/*.sh

# 4. Check symlinks
echo "=== Symbolic Links ==="
find . -type l -ls

# 5. Verify backups
echo "=== Backups ==="
ls -lh ~/backups/

# 6. Test navigation
echo "=== Navigation Test ==="
cd src/training && echo "✓ Can access src/training"
cd ../../data/raw && echo "✓ Can access data/raw"
cd ~/projects/ml-image-classifier && echo "✓ Returned to root"
```

**Expected Results**:
- [ ] 18+ subdirectories created
- [ ] 15+ files created
- [ ] 3+ scripts executable
- [ ] 2+ symbolic links created
- [ ] 1+ backup created
- [ ] All navigation tests pass

## Troubleshooting

**Problem**: Permission denied when creating directories
- **Solution**: Check you're in your home directory: `cd ~`
- Verify permissions: `ls -ld ~/projects`

**Problem**: tree command not found
- **Solution**: Install tree: `sudo apt install tree` or use `find` alternative

**Problem**: Symlink broken
- **Solution**: Check target exists: `ls -l symlink_name`
- Recreate with correct path: `ln -sf /correct/path linkname`

**Problem**: Can't find created files
- **Solution**: Verify you're in correct directory: `pwd`
- List all files including hidden: `ls -la`

## Reflection Questions

1. Why is a consistent directory structure important for ML projects?
2. When would you use absolute vs relative paths?
3. What's the advantage of using symlinks for dataset paths?
4. How do you safely delete files you might need later?
5. What's the benefit of creating backup scripts?

## Next Steps

After completing this exercise:
- **Exercise 02**: File Permissions - Learn to secure your ML project
- **Exercise 03**: Process Management - Monitor training jobs
- **Exercise 04**: Shell Scripting - Automate ML workflows

## Additional Practice

1. Create a second ML project with different structure
2. Write a script to compare two directory structures
3. Create a script to find and archive old experiment results
4. Set up a watch script to monitor file changes
5. Create a template generator script for new projects

---

**Congratulations!** You've mastered Linux navigation and file management for ML projects. These skills form the foundation for all your infrastructure work.
