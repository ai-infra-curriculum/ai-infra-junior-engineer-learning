# Exercise 02: File Permissions and Access Control for ML Teams

## Overview

This exercise teaches you how to manage file permissions and access control in a multi-user ML infrastructure environment. You'll learn to configure permissions for shared datasets, model directories, and collaborative development environments where multiple team members need controlled access to resources.

## Learning Objectives

By completing this exercise, you will:
- Understand Linux permission model (user, group, other) and permission bits
- Configure file and directory permissions using chmod (numeric and symbolic)
- Manage file ownership with chown and chgrp
- Set up Access Control Lists (ACLs) for fine-grained permissions
- Apply default permissions with umask
- Implement security best practices for ML infrastructure
- Create secure shared directories for ML team collaboration

## Prerequisites

- Completed Exercises 01
- Completed Lecture 03: Permissions and Security
- Access to a Linux system with sudo privileges (for some tasks)
- Understanding of Linux user and group concepts
- At least 2GB free disk space

## Time Required

- Estimated: 75-90 minutes
- Difficulty: Intermediate

## Part 1: Understanding the Permission Model

### Step 1: Analyze Current Permissions

```bash
# Create a workspace for this exercise
mkdir -p ~/ml-permissions-lab
cd ~/ml-permissions-lab

# Create various files to examine
touch dataset.csv model.h5 training_script.py config.yaml
mkdir shared_models team_data

# Examine permissions
ls -l

# Detailed analysis
echo "Analyzing permissions..."
ls -l dataset.csv

# Break down permission string: -rw-r--r--
# - = file type (- = file, d = directory, l = link)
# rw- = user/owner permissions (read, write, no execute)
# r-- = group permissions (read only)
# r-- = other permissions (read only)
```

**Expected Output**:
```
-rw-r--r-- 1 username username    0 Oct 18 10:00 dataset.csv
-rw-r--r-- 1 username username    0 Oct 18 10:00 model.h5
-rw-r--r-- 1 username username    0 Oct 18 10:00 training_script.py
-rw-r--r-- 1 username username    0 Oct 18 10:00 config.yaml
drwxr-xr-x 2 username username 4096 Oct 18 10:00 shared_models
drwxr-xr-x 2 username username 4096 Oct 18 10:00 team_data
```

**Analysis Tasks**:

1. Identify the owner and group:
   ```bash
   ls -l dataset.csv | awk '{print "Owner: "$3" Group: "$4}'
   ```

2. Check your current user and groups:
   ```bash
   whoami
   groups
   id
   ```

3. Examine directory permissions:
   ```bash
   ls -ld shared_models
   # Note: directories need execute (x) to access contents
   ```

**Validation**:
- [ ] Can list file permissions
- [ ] Understand permission string format
- [ ] Know your username and groups
- [ ] Recognize difference between file and directory permissions

### Step 2: Permission Calculation (Numeric Mode)

Understand numeric permission notation:

```bash
# Create reference file
cat > permission_reference.txt << 'EOF'
PERMISSION BITS REFERENCE
=========================

Symbolic    Numeric    Binary    Meaning
---------   -------    ------    -------
---         0          000       No permissions
--x         1          001       Execute only
-w-         2          010       Write only
-wx         3          011       Write and execute
r--         4          100       Read only
r-x         5          101       Read and execute
rw-         6          110       Read and write
rwx         7          111       Read, write, and execute

COMPLETE PERMISSIONS (User Group Other)
---------------------------------------
644 = rw-r--r--  (Standard file)
755 = rwxr-xr-x  (Executable/Directory)
600 = rw-------  (Private file)
700 = rwx------  (Private directory)
775 = rwxrwxr-x  (Group shared)
664 = rw-rw-r--  (Group editable)

CALCULATION EXAMPLE
-------------------
rw-r-xr--
6  5  4  = 654

r=4, w=2, x=1
User:  rw- = 4+2+0 = 6
Group: r-x = 4+0+1 = 5
Other: r-- = 4+0+0 = 4
EOF

cat permission_reference.txt
```

**Practice Calculations**:

Calculate numeric permissions for these symbolic permissions:

1. `rwxrwxrwx` = ?
2. `rw-rw-rw-` = ?
3. `r-xr-xr-x` = ?
4. `rwx------` = ?
5. `rw-r-----` = ?

**Answers**:
```
1. 777
2. 666
3. 555
4. 700
5. 640
```

## Part 2: Modifying Permissions with chmod

### Step 3: Numeric Mode Permissions

```bash
cd ~/ml-permissions-lab

# Create test files
touch private_model.h5 shared_dataset.csv team_script.py public_readme.md

# Set private file (owner only, read/write)
chmod 600 private_model.h5
ls -l private_model.h5
# Expected: -rw-------

# Set shared dataset (owner rw, group rw, other read)
chmod 664 shared_dataset.csv
ls -l shared_dataset.csv
# Expected: -rw-rw-r--

# Set executable script (owner rwx, group rx, other rx)
chmod 755 team_script.py
ls -l team_script.py
# Expected: -rwxr-xr-x

# Set public readable file
chmod 644 public_readme.md
ls -l public_readme.md
# Expected: -rw-r--r--

# Create directory with proper permissions
mkdir -p secure_models
chmod 700 secure_models
ls -ld secure_models
# Expected: drwx------

# Create shared directory
mkdir -p shared_experiments
chmod 775 shared_experiments
ls -ld shared_experiments
# Expected: drwxrwxr-x
```

**Validation**:
```bash
# Verify all permissions
echo "=== Permission Verification ==="
ls -l | grep -E "(private|shared|team|public)"

# Test permissions work correctly
# Private file should not be readable by others (simulated)
test -r private_model.h5 && echo "✓ Owner can read private file"

# Team script should be executable
test -x team_script.py && echo "✓ Script is executable"

# Directory should be accessible
test -d secure_models && echo "✓ Secure directory exists"
```

### Step 4: Symbolic Mode Permissions

```bash
# Create files for symbolic mode practice
cd ~/ml-permissions-lab
mkdir symbolic_practice
cd symbolic_practice

touch model_v1.h5 data_prep.py results.csv

# Add execute permission for owner
chmod u+x data_prep.py
ls -l data_prep.py
# Before: -rw-r--r--
# After:  -rwxr--r--

# Add write permission for group
chmod g+w results.csv
ls -l results.csv
# Before: -rw-r--r--
# After:  -rw-rw-r--

# Remove read permission for others
chmod o-r model_v1.h5
ls -l model_v1.h5
# Before: -rw-r--r--
# After:  -rw-r-----

# Set exact permissions (overwrites existing)
chmod u=rwx,g=rx,o=r data_prep.py
ls -l data_prep.py
# Result: -rwxr-xr--

# Multiple changes at once
touch experiment_data.json
chmod u+x,g+w,o-r experiment_data.json
ls -l experiment_data.json

# Add execute to all
touch analyze.sh
chmod a+x analyze.sh
ls -l analyze.sh
# a = all (user, group, other)

# Recursive permission change
mkdir -p test_project/{data,models,scripts}
touch test_project/data/train.csv
touch test_project/models/model.h5
touch test_project/scripts/run.sh

# Make all scripts executable recursively
find test_project/scripts -type f -name "*.sh" -exec chmod +x {} \;

# Set directory permissions recursively
chmod -R 755 test_project
ls -lR test_project
```

**Symbolic Mode Reference**:
```bash
cat > symbolic_reference.txt << 'EOF'
SYMBOLIC MODE REFERENCE
=======================

Who (ugoa)
----------
u = user/owner
g = group
o = others
a = all (ugo)

Operation (+-=)
---------------
+ = add permission
- = remove permission
= = set exact permission

Permission (rwx)
----------------
r = read
w = write
x = execute

Examples:
---------
chmod u+x file      Add execute for owner
chmod g-w file      Remove write for group
chmod o-r file      Remove read for others
chmod a+r file      Add read for all
chmod u=rwx file    Set owner to rwx
chmod go=rx file    Set group and other to r-x
chmod u+x,g+x file  Add execute for owner and group
EOF

cat symbolic_reference.txt
```

### Step 5: Real-World ML Scenarios

```bash
cd ~/ml-permissions-lab
mkdir ml_project_team
cd ml_project_team

# Scenario 1: Shared Dataset Directory
# Multiple data scientists need read access, only owner can modify
mkdir -p datasets/{raw,processed}

# Raw data: immutable (owner rw, group and others read)
chmod 755 datasets/raw
touch datasets/raw/train_images.tar
chmod 644 datasets/raw/train_images.tar

# Processed data: team can write
chmod 775 datasets/processed
touch datasets/processed/augmented_images.npz
chmod 664 datasets/processed/augmented_images.npz

# Scenario 2: Model Repository
# Team can read models, only ML engineers can write
mkdir -p models/{checkpoints,production}

chmod 775 models/checkpoints  # Team collaborative
chmod 755 models/production   # Production: restricted

touch models/checkpoints/epoch_050.h5
chmod 664 models/checkpoints/epoch_050.h5

touch models/production/v1.2.3.h5
chmod 644 models/production/v1.2.3.h5  # Read-only

# Scenario 3: Training Scripts
# Everyone can read and execute, only developers can modify
mkdir -p scripts
touch scripts/train_model.py scripts/evaluate.py scripts/deploy.sh

chmod 755 scripts/*.py
chmod 755 scripts/*.sh

# Scenario 4: Sensitive Configuration
# Only owner should access
mkdir -p configs/secrets
chmod 700 configs/secrets

touch configs/secrets/api_keys.yaml configs/secrets/db_credentials.json
chmod 600 configs/secrets/*

# Scenario 5: Log Files
# System writes, team reads
mkdir -p logs
chmod 755 logs

touch logs/training_2024-10-18.log
chmod 644 logs/training_2024-10-18.log

# Scenario 6: Collaborative Notebooks
# Team can edit together
mkdir -p notebooks
chmod 775 notebooks

touch notebooks/exploration.ipynb notebooks/training_analysis.ipynb
chmod 664 notebooks/*.ipynb

# Verify the complete structure
echo "=== ML Project Permission Structure ==="
find . -ls | awk '{print $3, $11}'
```

**Validation Checklist**:
```bash
# Test each scenario
echo "=== Validation ==="

# 1. Datasets
test -r datasets/raw/train_images.tar && echo "✓ Raw data is readable"
test -w datasets/processed/augmented_images.npz && echo "✓ Processed data is writable"

# 2. Models
test -r models/production/v1.2.3.h5 && echo "✓ Production model is readable"
test -w models/checkpoints/epoch_050.h5 && echo "✓ Checkpoint is writable"

# 3. Scripts
test -x scripts/train_model.py && echo "✓ Training script is executable"

# 4. Secrets
test "$(stat -c '%a' configs/secrets)" = "700" && echo "✓ Secrets directory is private"

# 5. Logs
test -r logs/training_2024-10-18.log && echo "✓ Log file is readable"

# 6. Notebooks
test -w notebooks/exploration.ipynb && echo "✓ Notebook is editable"
```

## Part 3: Ownership Management

### Step 6: Understanding chown and chgrp

```bash
cd ~/ml-permissions-lab
mkdir ownership_lab
cd ownership_lab

# Create test files
touch dataset.csv model.h5 script.py

# Check current ownership
ls -l
# Format: -rw-r--r-- 1 username username size date file

# Note: Changing ownership typically requires sudo
# We'll demonstrate the commands (may need sudo in real scenarios)

# Show current user and groups
echo "Current user: $(whoami)"
echo "Groups: $(groups)"
echo "Primary group: $(id -gn)"

# Create a scenario with a dedicated ML group (requires sudo)
cat > ownership_commands.sh << 'EOF'
#!/bin/bash
# These commands demonstrate ownership changes
# Run with sudo if needed

# Create ML team group (requires sudo)
# sudo groupadd mlteam

# Add users to ML team (requires sudo)
# sudo usermod -a -G mlteam alice
# sudo usermod -a -G mlteam bob
# sudo usermod -a -G mlteam charlie

# Change group ownership of shared directory
# sudo chgrp mlteam shared_models/

# Change owner and group
# sudo chown alice:mlteam models/production/

# Recursive ownership change
# sudo chown -R alice:mlteam datasets/

# Change only group (keep owner)
# sudo chgrp -R mlteam experiments/

# Verify changes
# ls -l shared_models/
# ls -ld datasets/
EOF

chmod +x ownership_commands.sh
cat ownership_commands.sh
```

### Step 7: Practical Group Permissions Setup

```bash
cd ~/ml-permissions-lab
mkdir team_collaboration
cd team_collaboration

# Simulate team environment
# Create group-shared structure

# Project directories
mkdir -p {datasets,models,experiments,notebooks,scripts}

# Set group permissions for collaboration
chmod 775 datasets models experiments notebooks scripts

# Create files with proper group permissions
touch datasets/train_data.csv
chmod 664 datasets/train_data.csv

touch models/baseline_model.h5
chmod 664 models/baseline_model.h5

touch experiments/exp_001_config.yaml
chmod 664 experiments/exp_001_config.yaml

touch scripts/preprocess.py
chmod 775 scripts/preprocess.py

# Create README explaining permissions
cat > PERMISSIONS.md << 'EOF'
# ML Team Collaboration Permissions

## Directory Structure

### datasets/ (775)
- Group writable for all team members
- Files should be 664 (group editable)
- Raw data should be 644 (read-only after initial creation)

### models/ (775)
- Checkpoints: 664 (team editable)
- Production models: 644 (read-only)

### experiments/ (775)
- Config files: 664 (team editable)
- Results: 644 (read-only after completion)

### notebooks/ (775)
- All notebooks: 664 (team editable for collaboration)

### scripts/ (775)
- Python scripts: 664 (view and edit)
- Shell scripts: 775 (executable)

## Best Practices

1. Always set group permissions when creating files
2. Use umask to set default permissions
3. Review permissions before sharing sensitive data
4. Use ACLs for fine-grained access control
EOF

chmod 644 PERMISSIONS.md
cat PERMISSIONS.md
```

## Part 4: Advanced Access Control Lists (ACLs)

### Step 8: Working with ACLs

Access Control Lists provide fine-grained permissions beyond traditional Unix permissions.

```bash
cd ~/ml-permissions-lab
mkdir acl_practice
cd acl_practice

# Check if ACL is supported
df -T .
getfacl --version

# Create a shared model directory
mkdir shared_model_registry
touch shared_model_registry/model_v1.h5

# View default ACLs
getfacl shared_model_registry/model_v1.h5

# Set ACL to give specific user read access
# (Replace 'alice' with actual username in real scenario)
# setfacl -m u:alice:r shared_model_registry/model_v1.h5

# Set ACL for group
# setfacl -m g:mlteam:rw shared_model_registry/model_v1.h5

# Set default ACL for directory (applies to new files)
# setfacl -d -m g:mlteam:rw shared_model_registry/

# View ACL
# getfacl shared_model_registry/model_v1.h5

# Create example ACL configuration script
cat > setup_acls.sh << 'EOF'
#!/bin/bash
# ACL Setup Script for ML Infrastructure

# Note: Replace usernames and groups with actual values

# Set ACLs for sensitive model directory
# Only specific users can access
# setfacl -m u:ml_engineer:rwx models/production/
# setfacl -m u:data_scientist:r-x models/production/
# setfacl -m g:mlops:rwx models/production/

# Set default ACLs for datasets
# New files inherit group permissions
# setfacl -d -m g:datateam:rw datasets/raw/
# setfacl -d -m g:datateam:rw datasets/processed/

# Set ACLs for experiment results
# Researcher has full access, team can read
# setfacl -m u:researcher1:rwx experiments/exp_001/
# setfacl -m g:mlteam:r-x experiments/exp_001/

# Remove ACL
# setfacl -x u:username file
# setfacl -b file  # Remove all ACLs

# Copy ACL from one file to another
# getfacl file1 | setfacl --set-file=- file2

echo "ACL setup complete"
echo "Use 'getfacl' to view ACLs"
EOF

chmod +x setup_acls.sh
cat setup_acls.sh

# Create ACL reference guide
cat > acl_reference.txt << 'EOF'
ACL COMMANDS REFERENCE
======================

View ACLs:
----------
getfacl file              View ACLs for file
getfacl -R directory      View ACLs recursively

Set ACLs:
---------
setfacl -m u:user:rwx file       Set user permissions
setfacl -m g:group:rw file       Set group permissions
setfacl -m o::r file             Set others permissions
setfacl -m m::rwx file           Set mask (max permissions)

Default ACLs (for directories):
--------------------------------
setfacl -d -m g:group:rw dir     New files inherit group permissions
setfacl -d -m u:user:rx dir      New files inherit user permissions

Remove ACLs:
------------
setfacl -x u:user file           Remove user ACL
setfacl -x g:group file          Remove group ACL
setfacl -b file                  Remove all ACLs

Copy ACLs:
----------
getfacl file1 | setfacl --set-file=- file2

Backup/Restore ACLs:
--------------------
getfacl -R directory > acls.txt
setfacl --restore=acls.txt

Examples:
---------
# Give alice read/write access
setfacl -m u:alice:rw dataset.csv

# Give mlteam group full access
setfacl -m g:mlteam:rwx models/

# Set default ACL for new files
setfacl -d -m g:mlteam:rw shared/

# Remove all ACLs
setfacl -b file

ACL Notation:
-------------
# = effective permission (considering mask)
u:username:rwx = user permission
g:groupname:rw = group permission
o::r = others permission
m::rwx = mask (maximum effective permissions)
EOF

cat acl_reference.txt
```

## Part 5: Default Permissions with umask

### Step 9: Understanding and Setting umask

```bash
cd ~/ml-permissions-lab
mkdir umask_practice
cd umask_practice

# Check current umask
umask
# Common values: 0022 or 0002

# View umask in symbolic notation
umask -S

# Understand umask calculation
cat > umask_explanation.txt << 'EOF'
UMASK EXPLANATION
=================

umask subtracts from default permissions:
- Files default:    666 (rw-rw-rw-)
- Directories default: 777 (rwxrwxrwx)

umask 0022:
-----------
Files:     666 - 022 = 644 (rw-r--r--)
Dirs:      777 - 022 = 755 (rwxr-xr-x)

umask 0002:
-----------
Files:     666 - 002 = 664 (rw-rw-r--)
Dirs:      777 - 002 = 775 (rwxrwxr-x)

umask 0077:
-----------
Files:     666 - 077 = 600 (rw-------)
Dirs:      777 - 077 = 700 (rwx------)

Calculation:
------------
Each digit position (user, group, other):
umask digit subtracts from default

Example: umask 0027
User:  7 - 0 = 7 (rwx for dirs, rw for files)
Group: 7 - 2 = 5 (r-x for dirs, r-- for files)
Other: 7 - 7 = 0 (--- no permissions)

Result:
Files:  666 - 027 = 640 (rw-r-----)
Dirs:   777 - 027 = 750 (rwxr-x---)
EOF

cat umask_explanation.txt

# Test different umask values
echo "=== Testing umask values ==="

# Save current umask
OLD_UMASK=$(umask)

# Test umask 0022 (standard)
umask 0022
touch test_022_file
mkdir test_022_dir
ls -l test_022_file  # Should be 644
ls -ld test_022_dir  # Should be 755

# Test umask 0002 (group collaborative)
umask 0002
touch test_002_file
mkdir test_002_dir
ls -l test_002_file  # Should be 664
ls -ld test_002_dir  # Should be 775

# Test umask 0077 (private)
umask 0077
touch test_077_file
mkdir test_077_dir
ls -l test_077_file  # Should be 600
ls -ld test_077_dir  # Should be 700

# Restore original umask
umask $OLD_UMASK

# Show comparison
echo "=== umask Comparison ==="
ls -l test_*
```

### Step 10: Setting Permanent umask

```bash
cd ~/ml-permissions-lab

# Create a guide for setting permanent umask
cat > umask_setup_guide.md << 'EOF'
# Setting Permanent umask

## For Individual User

Add to `~/.bashrc` or `~/.bash_profile`:

```bash
# Set umask for group collaboration (ML team)
umask 0002

# Or for private files (security-sensitive work)
umask 0077

# Or standard (less restrictive)
umask 0022
```

## For ML Project Directory

Create a wrapper script:

```bash
#!/bin/bash
# ml_env.sh - Set up ML environment

# Set collaborative umask
umask 0002

# Set environment variables
export ML_PROJECT_ROOT="$HOME/ml-projects"
export ML_DATA_DIR="$ML_PROJECT_ROOT/datasets"
export ML_MODELS_DIR="$ML_PROJECT_ROOT/models"

# Create directories with proper permissions
mkdir -p "$ML_DATA_DIR" "$ML_MODELS_DIR"

echo "ML environment configured"
echo "umask: $(umask)"
```

## Testing umask

```bash
# Test script
./ml_env.sh
touch test_file.txt
mkdir test_dir
ls -l test_file.txt  # Check permissions
ls -ld test_dir      # Check permissions
```

## Best Practices

1. **Team Collaboration**: Use umask 0002
   - Files: 664 (group can edit)
   - Dirs: 775 (group can access)

2. **Security-Sensitive**: Use umask 0077
   - Files: 600 (owner only)
   - Dirs: 700 (owner only)

3. **General Use**: Use umask 0022
   - Files: 644 (others can read)
   - Dirs: 755 (others can access)

4. **Project-Specific**: Set in project scripts
5. **System-Wide**: Configure in `/etc/profile` (requires sudo)
EOF

cat umask_setup_guide.md

# Create practical ML environment setup script
cat > ml_permissions_env.sh << 'EOF'
#!/bin/bash
# ML Permissions Environment Setup

# Set collaborative umask for ML team
umask 0002

# Create ML project structure
ML_ROOT="$HOME/ml-workspace"
mkdir -p "$ML_ROOT"/{datasets,models,experiments,notebooks,scripts,logs}

# Set directory permissions
chmod 775 "$ML_ROOT"/{datasets,models,experiments,notebooks,scripts}
chmod 755 "$ML_ROOT/logs"  # Logs: owner writes, team reads

# Create sample files
touch "$ML_ROOT/datasets/sample.csv"
touch "$ML_ROOT/models/model.h5"
touch "$ML_ROOT/experiments/config.yaml"
touch "$ML_ROOT/scripts/train.py"

# Make scripts executable
chmod +x "$ML_ROOT/scripts"/*.py 2>/dev/null || true

echo "ML workspace created at: $ML_ROOT"
echo "Current umask: $(umask)"
echo ""
echo "Directory permissions:"
ls -ld "$ML_ROOT"/*

echo ""
echo "File permissions:"
find "$ML_ROOT" -type f -ls | awk '{print $3, $11}'
EOF

chmod +x ml_permissions_env.sh
./ml_permissions_env.sh
```

## Part 6: Security Best Practices

### Step 11: Implementing Security Patterns

```bash
cd ~/ml-permissions-lab
mkdir security_patterns
cd security_patterns

# Pattern 1: Least Privilege
cat > least_privilege.sh << 'EOF'
#!/bin/bash
# Implement least privilege principle

# Create security zones
mkdir -p {public,shared,restricted,private}

# Public: Everyone can read (documentation, public datasets)
chmod 755 public
touch public/readme.md public/sample_data.csv
chmod 644 public/*

# Shared: Team collaboration (experiments, notebooks)
chmod 775 shared
touch shared/experiment.ipynb shared/results.csv
chmod 664 shared/*

# Restricted: Limited access (production models, sensitive data)
chmod 750 restricted
touch restricted/prod_model.h5 restricted/customer_data.csv
chmod 640 restricted/*

# Private: Owner only (API keys, credentials)
chmod 700 private
touch private/api_keys.yaml private/db_password.txt
chmod 600 private/*

echo "Security zones created:"
ls -ld {public,shared,restricted,private}
EOF

chmod +x least_privilege.sh
./least_privilege.sh

# Pattern 2: Secure File Creation
cat > secure_file_creation.sh << 'EOF'
#!/bin/bash
# Securely create sensitive files

# Function to create secure file
create_secure_file() {
    local filename=$1
    local content=$2

    # Set restrictive umask
    old_umask=$(umask)
    umask 0077

    # Create file (will have 600 permissions)
    echo "$content" > "$filename"

    # Restore umask
    umask $old_umask

    echo "Created secure file: $filename ($(stat -c '%a' "$filename"))"
}

# Create secure credentials file
create_secure_file "credentials.yaml" "api_key: secret_key_here"

# Verify permissions
ls -l credentials.yaml
# Should be -rw-------
EOF

chmod +x secure_file_creation.sh
./secure_file_creation.sh

# Pattern 3: Permission Audit Script
cat > audit_permissions.sh << 'EOF'
#!/bin/bash
# Audit file permissions for security issues

PROJECT_ROOT="${1:-.}"

echo "=== Permission Security Audit ==="
echo "Scanning: $PROJECT_ROOT"
echo ""

# Find world-writable files (security risk)
echo "World-writable files (RISK):"
find "$PROJECT_ROOT" -type f -perm -002 -ls 2>/dev/null

# Find world-writable directories
echo ""
echo "World-writable directories (RISK):"
find "$PROJECT_ROOT" -type d -perm -002 -ls 2>/dev/null

# Find files with no permission restrictions
echo ""
echo "Files with 777 permissions (RISK):"
find "$PROJECT_ROOT" -type f -perm 777 -ls 2>/dev/null

# Find SUID/SGID files (potential risk)
echo ""
echo "SUID/SGID files:"
find "$PROJECT_ROOT" -type f \( -perm -4000 -o -perm -2000 \) -ls 2>/dev/null

# Find files readable by others that might contain secrets
echo ""
echo "Potentially sensitive files readable by others:"
find "$PROJECT_ROOT" -type f \( -name "*secret*" -o -name "*password*" -o -name "*key*" -o -name "*.pem" \) -perm -004 -ls 2>/dev/null

# Find executable files
echo ""
echo "Executable files:"
find "$PROJECT_ROOT" -type f -executable -ls 2>/dev/null

echo ""
echo "Audit complete"
EOF

chmod +x audit_permissions.sh

# Pattern 4: Fix Common Permission Issues
cat > fix_permissions.sh << 'EOF'
#!/bin/bash
# Fix common permission issues in ML projects

PROJECT_ROOT="${1:-.}"

echo "Fixing permissions in: $PROJECT_ROOT"

# Fix directory permissions (755)
find "$PROJECT_ROOT" -type d -exec chmod 755 {} \; 2>/dev/null

# Fix regular file permissions (644)
find "$PROJECT_ROOT" -type f -exec chmod 644 {} \; 2>/dev/null

# Make scripts executable (755)
find "$PROJECT_ROOT" -type f -name "*.sh" -exec chmod 755 {} \; 2>/dev/null
find "$PROJECT_ROOT" -type f -name "*.py" -path "*/scripts/*" -exec chmod 755 {} \; 2>/dev/null

# Secure credential files (600)
find "$PROJECT_ROOT" -type f \( -name "*secret*" -o -name "*password*" -o -name "*key*" -o -name "credentials.*" \) -exec chmod 600 {} \; 2>/dev/null

# Secure private directories (700)
find "$PROJECT_ROOT" -type d -name "private" -exec chmod 700 {} \; 2>/dev/null
find "$PROJECT_ROOT" -type d -name "secrets" -exec chmod 700 {} \; 2>/dev/null

echo "Permissions fixed"
echo "Run audit script to verify"
EOF

chmod +x fix_permissions.sh

# Run audit on security patterns
echo "=== Running Security Audit ==="
./audit_permissions.sh .
```

### Step 12: Real-World Security Scenarios

```bash
cd ~/ml-permissions-lab
mkdir production_security
cd production_security

# Scenario: Secure Model Deployment
cat > secure_model_deployment.sh << 'EOF'
#!/bin/bash
# Secure model deployment workflow

DEPLOY_DIR="/opt/ml/models"  # Would be real path in production
STAGING_DIR="$HOME/ml-permissions-lab/production_security/staging"
PROD_DIR="$HOME/ml-permissions-lab/production_security/production"

# Create staging and production directories
mkdir -p "$STAGING_DIR" "$PROD_DIR"

# Staging: Team can modify (775/664)
chmod 775 "$STAGING_DIR"

# Production: Readonly for most, only deploy script can write (755/644)
chmod 755 "$PROD_DIR"

# Deploy a model
deploy_model() {
    local model_name=$1

    # Create model in staging (permissive)
    touch "$STAGING_DIR/$model_name"
    chmod 664 "$STAGING_DIR/$model_name"
    echo "Model staged: $model_name"

    # After testing, promote to production (restrictive)
    cp "$STAGING_DIR/$model_name" "$PROD_DIR/$model_name"
    chmod 444 "$PROD_DIR/$model_name"  # Read-only
    echo "Model deployed: $model_name (read-only)"
}

deploy_model "model_v1.2.3.h5"

echo ""
echo "Staging area:"
ls -l "$STAGING_DIR"
echo ""
echo "Production area:"
ls -l "$PROD_DIR"
EOF

chmod +x secure_model_deployment.sh
./secure_model_deployment.sh

# Scenario: Multi-Tenant Dataset Access
cat > multi_tenant_access.sh << 'EOF'
#!/bin/bash
# Multi-tenant dataset access control

# Create tenant directories
mkdir -p datasets/{tenant_a,tenant_b,shared}

# Tenant A: Only tenant A can access (700)
chmod 700 datasets/tenant_a
touch datasets/tenant_a/customer_data.csv
chmod 600 datasets/tenant_a/customer_data.csv

# Tenant B: Only tenant B can access (700)
chmod 700 datasets/tenant_b
touch datasets/tenant_b/customer_data.csv
chmod 600 datasets/tenant_b/customer_data.csv

# Shared: Both tenants can read, controlled writes (755)
chmod 755 datasets/shared
touch datasets/shared/public_dataset.csv
chmod 644 datasets/shared/public_dataset.csv

echo "Multi-tenant structure:"
ls -lR datasets/
EOF

chmod +x multi_tenant_access.sh
./multi_tenant_access.sh
```

## Part 7: Comprehensive Challenge

### Challenge: Build a Complete ML Project with Proper Permissions

```bash
cd ~/ml-permissions-lab
mkdir final_challenge
cd final_challenge

# Your task: Create a complete ML project structure with security
cat > challenge_requirements.md << 'EOF'
# Final Challenge: Secure ML Project Setup

## Requirements

Create a complete ML project with the following security requirements:

### 1. Directory Structure
- public/: Documentation, public datasets (755/644)
- team/: Collaborative workspace (775/664)
- team/datasets/: Team data (775/664)
- team/experiments/: Experiments (775/664)
- team/notebooks/: Shared notebooks (775/664)
- production/: Production models (755/444 - read-only)
- private/: Secrets and credentials (700/600)
- scripts/: Deployment scripts (755/755)
- logs/: Application logs (755/644)

### 2. Security Requirements
- No world-writable files or directories
- Credentials and secrets accessible only by owner
- Production models are read-only
- Scripts are executable
- Team can collaborate on experiments
- Logs are readable by team, writable by system

### 3. Deliverables
- Complete directory structure
- Sample files in each directory
- Permission audit script that validates security
- Documentation of permission strategy

### 4. Validation
Your setup must pass security audit with no warnings.
EOF

cat challenge_requirements.md

# Solution template (try yourself first!)
cat > solution.sh << 'EOF'
#!/bin/bash
# Solution to ML Project Security Challenge

# TODO: Implement the complete solution
# 1. Create directory structure
# 2. Set appropriate permissions
# 3. Create sample files
# 4. Implement audit script
# 5. Document your approach

echo "Implement your solution here"
EOF

chmod +x solution.sh
```

## Validation and Testing

### Final Validation Script

```bash
cd ~/ml-permissions-lab

cat > validate_exercise.sh << 'EOF'
#!/bin/bash
# Validation script for Exercise 02

PASS=0
FAIL=0

test_permission() {
    local file=$1
    local expected=$2
    local actual=$(stat -c '%a' "$file" 2>/dev/null)

    if [ "$actual" = "$expected" ]; then
        echo "✓ $file has correct permissions ($expected)"
        ((PASS++))
    else
        echo "✗ $file has incorrect permissions (expected $expected, got $actual)"
        ((FAIL++))
    fi
}

echo "=== Permission Validation ==="
echo ""

# Test symbolic practice
if [ -d "symbolic_practice" ]; then
    cd symbolic_practice
    test_permission "data_prep.py" "754"
    cd ..
fi

# Test ML project team
if [ -d "ml_project_team" ]; then
    cd ml_project_team
    test_permission "datasets/raw" "755"
    test_permission "configs/secrets" "700"
    cd ..
fi

# Test security patterns
if [ -d "security_patterns" ]; then
    cd security_patterns
    test_permission "private" "700"
    test_permission "public" "755"
    cd ..
fi

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

**Problem**: Permission denied when creating files
- **Solution**: Check directory permissions with `ls -ld directory`
- Ensure directory has write permission: `chmod u+w directory`

**Problem**: Cannot execute script
- **Solution**: Add execute permission: `chmod +x script.sh`
- Verify: `ls -l script.sh` should show `x` in permissions

**Problem**: Group permissions not working
- **Solution**: Verify you're in the correct group: `groups`
- Check file group ownership: `ls -l file`

**Problem**: ACL commands not found
- **Solution**: Install ACL tools: `sudo apt install acl`
- Check filesystem supports ACL: `mount | grep acl`

**Problem**: umask changes don't persist
- **Solution**: Add umask command to `~/.bashrc`
- Source the file: `source ~/.bashrc`

**Problem**: Cannot change ownership
- **Solution**: chown requires sudo: `sudo chown user:group file`
- Or work within your own directories

## Reflection Questions

1. Why is the execute permission necessary for directories?
2. When would you use ACLs instead of traditional permissions?
3. How does umask affect newly created files?
4. What security risks arise from world-writable files?
5. How would you structure permissions for a 10-person ML team?
6. Why should production models be read-only?
7. What permissions should log files have and why?

## Next Steps

After completing this exercise:
- **Exercise 03**: Process Management - Monitor and control ML training processes
- **Exercise 04**: Shell Scripting - Automate permission management
- **Lecture 03**: Process Management - Understanding Linux processes

## Additional Resources

- Linux File Permissions: https://www.linux.com/training-tutorials/understanding-linux-file-permissions/
- ACL Tutorial: https://www.redhat.com/sysadmin/linux-access-control-lists
- umask Guide: https://www.cyberciti.biz/tips/understanding-linux-unix-umask-value-usage.html
- Security Best Practices: https://www.cisecurity.org/

---

**Congratulations!** You've mastered Linux file permissions and access control for ML infrastructure. These skills are critical for maintaining secure, collaborative ML environments.
