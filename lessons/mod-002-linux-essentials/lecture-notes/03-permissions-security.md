# Lecture 03: Permissions and Security

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Linux Permissions](#understanding-linux-permissions)
3. [Users and Groups](#users-and-groups)
4. [Managing Permissions with chmod](#managing-permissions-with-chmod)
5. [Changing Ownership with chown](#changing-ownership-with-chown)
6. [Special Permissions](#special-permissions)
7. [Default Permissions and umask](#default-permissions-and-umask)
8. [Access Control Lists (ACLs)](#access-control-lists-acls)
9. [Security Best Practices for AI Infrastructure](#security-best-practices-for-ai-infrastructure)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Security is paramount in AI infrastructure. You'll be managing sensitive datasets, proprietary models, API keys, and production systems. Understanding Linux permissions ensures you can protect these assets while enabling collaboration across teams.

This lecture covers the Linux permission model, user management, and security practices essential for AI infrastructure engineers.

### Learning Objectives

By the end of this lecture, you will:
- Understand the Linux permission model (read, write, execute)
- Interpret and modify file permissions using symbolic and numeric notation
- Manage users and groups effectively
- Use `chmod`, `chown`, and `chgrp` confidently
- Implement special permissions (setuid, setgid, sticky bit)
- Configure default permissions with umask
- Apply Access Control Lists (ACLs) for complex scenarios
- Secure AI infrastructure following best practices

### Prerequisites
- Lecture 01: Linux Fundamentals
- Understanding of multi-user systems
- Basic security awareness

### Why Permissions Matter in AI Infrastructure

**Data Privacy**: Protect sensitive training data and PII (personally identifiable information)

**Model Security**: Prevent unauthorized access to proprietary models worth millions in R&D

**Access Control**: Manage who can run experiments, access GPUs, and modify production systems

**Compliance**: Meet regulatory requirements (GDPR, HIPAA, SOC 2)

**Collaboration**: Enable team access while maintaining security boundaries

## Understanding Linux Permissions

Every file and directory in Linux has three permission levels for three categories of users.

### Permission Categories (Who)

1. **User (u)**: The file owner
2. **Group (g)**: Members of the file's group
3. **Others (o)**: Everyone else on the system

### Permission Types (What)

1. **Read (r)**: View file contents or list directory contents
2. **Write (w)**: Modify file or create/delete files in directory
3. **Execute (x)**: Run file as program or access directory

### Viewing Permissions

```bash
ls -l train.py
# -rwxr-xr-- 1 alice mlteam 2048 Oct 15 14:30 train.py
# │└┬┘└┬┘└┬┘   │     │      │    │           │
# │ │  │  │    │     │      │    │           └─ Filename
# │ │  │  │    │     │      │    └─ Modification date
# │ │  │  │    │     │      └─ File size
# │ │  │  │    │     └─ Group owner
# │ │  │  │    └─ File owner
# │ │  │  └─ Others permissions (r--)
# │ │  └─ Group permissions (r-x)
# │ └─ User/owner permissions (rwx)
# └─ File type (- = file, d = directory, l = link)
```

### File Type Indicators

```bash
-    Regular file
d    Directory
l    Symbolic link
b    Block device (disk drives)
c    Character device (terminals)
p    Named pipe (FIFO)
s    Socket
```

### Permission Meanings by Context

**For Regular Files**:
- `r` (read): Can view file contents (`cat`, `less`, `vim`)
- `w` (write): Can modify file contents
- `x` (execute): Can run file as a program/script

**For Directories**:
- `r` (read): Can list directory contents (`ls`)
- `w` (write): Can create, delete, rename files in directory
- `x` (execute): Can access directory (`cd`), access files within

### Permission Examples

```bash
# File examples
-rw-r--r--  config.yaml       # Owner: read/write, Group: read, Others: read
-rwxr-xr-x  train.py          # Owner: read/write/execute, Group: read/execute, Others: read/execute
-rw-------  api_key.txt       # Owner: read/write, Group: none, Others: none (private)
-rwxrwxrwx  dangerous.sh      # Everyone: full access (security risk!)

# Directory examples
drwxr-xr-x  models/           # Owner: full, Group: read/list, Others: read/list
drwx------  .ssh/             # Owner: full, Group: none, Others: none (secure)
drwxrwxr-x  shared/           # Owner+Group: full, Others: read/list
drwxrwxrwt  /tmp/             # Special: sticky bit set
```

## Users and Groups

### Understanding /etc/passwd

User account information is stored in `/etc/passwd`:

```bash
cat /etc/passwd | grep alice
# alice:x:1001:1001:Alice Johnson:/home/alice:/bin/bash
#   │   │  │    │         │            │           └─ Default shell
#   │   │  │    │         │            └─ Home directory
#   │   │  │    │         └─ Full name/comment
#   │   │  │    └─ Primary group ID (GID)
#   │   │  └─ User ID (UID)
#   │   └─ Password (x = stored in /etc/shadow)
#   └─ Username
```

### Understanding /etc/group

Group information is stored in `/etc/group`:

```bash
cat /etc/group | grep mlteam
# mlteam:x:2001:alice,bob,charlie
#   │    │  │      └─ Group members
#   │    │  └─ Group ID (GID)
#   │    └─ Password (rarely used)
#   └─ Group name
```

### Viewing User and Group Information

```bash
# Current user
whoami                          # alice
id                              # uid=1001(alice) gid=1001(alice) groups=1001(alice),2001(mlteam)
groups                          # alice mlteam docker

# Specific user
id bob                          # Show bob's UID, GID, groups
groups bob                      # Show bob's groups

# All logged-in users
who                             # Show currently logged-in users
w                               # Show who is logged in and what they're doing
```

### Creating Users (Requires sudo/root)

```bash
# Create user with home directory
sudo useradd -m -s /bin/bash charlie
# -m: create home directory
# -s: set default shell

# Set password
sudo passwd charlie

# Create user with specific UID and groups
sudo useradd -m -u 1005 -g mlteam -G docker,admin dave
# -u: specific UID
# -g: primary group
# -G: additional groups

# Modern alternative (more user-friendly)
sudo adduser charlie            # Interactive user creation
```

### Creating Groups

```bash
# Create group
sudo groupadd mlteam
sudo groupadd -g 2001 mlteam    # With specific GID

# Add user to group
sudo usermod -aG mlteam alice   # -aG: append to group (don't remove from others)
sudo usermod -aG docker alice   # Add to docker group

# Remove user from group
sudo gpasswd -d alice mlteam

# Verify
groups alice
```

### Modifying Users

```bash
# Change user's primary group
sudo usermod -g newgroup alice

# Change user's home directory
sudo usermod -d /new/home/path alice

# Change user's shell
sudo usermod -s /bin/zsh alice

# Change username
sudo usermod -l newname oldname

# Lock/unlock user account
sudo usermod -L alice           # Lock
sudo usermod -U alice           # Unlock
```

### Deleting Users and Groups

```bash
# Delete user (keep home directory)
sudo userdel alice

# Delete user and home directory
sudo userdel -r alice

# Delete group
sudo groupdel mlteam
```

### Sudo and Privilege Escalation

The `sudo` command allows authorized users to run commands as root.

**Configuration**: `/etc/sudoers` (edit with `visudo` only!)

```bash
# Grant user sudo access
sudo usermod -aG sudo alice     # On Ubuntu/Debian
sudo usermod -aG wheel alice    # On RHEL/CentOS

# Run command as root
sudo apt update
sudo systemctl restart nginx

# Run command as different user
sudo -u bob python train.py

# Run shell as root (be careful!)
sudo -i                         # Login shell
sudo -s                         # Keep environment

# Check sudo access
sudo -l                         # List allowed commands

# Run previous command with sudo
sudo !!
```

**Best Practices**:
- Use `sudo` for individual commands, not `sudo su` for root shell
- Review sudo access regularly
- Log sudo usage for auditing
- Use specific command permissions when possible

## Managing Permissions with chmod

`chmod` (change mode) modifies file and directory permissions.

### Symbolic Notation

**Syntax**: `chmod [who][operation][permissions] file`

**Who**: `u` (user), `g` (group), `o` (others), `a` (all)
**Operation**: `+` (add), `-` (remove), `=` (set exactly)
**Permissions**: `r` (read), `w` (write), `x` (execute)

**Examples**:
```bash
# Add execute permission for owner
chmod u+x train.py

# Remove write permission for group and others
chmod go-w config.yaml

# Set exact permissions: owner read/write, group read, others none
chmod u=rw,g=r,o= sensitive_data.csv

# Add execute for everyone
chmod a+x script.sh
chmod +x script.sh              # Shorthand for a+x

# Remove all permissions for others
chmod o-rwx private_model.h5

# Make file read-only for everyone
chmod a-w readonly_config.yaml

# Multiple operations
chmod u+x,go-w train.py         # Owner: add execute, Group/Others: remove write
```

### Numeric (Octal) Notation

Each permission has a numeric value:
- `r` (read) = 4
- `w` (write) = 2
- `x` (execute) = 1

Combine values for each category:
- `7` = rwx (4+2+1)
- `6` = rw- (4+2)
- `5` = r-x (4+1)
- `4` = r-- (4)
- `0` = --- (none)

**Syntax**: `chmod [user][group][others] file`

**Common Patterns**:
```bash
chmod 644 file.txt              # rw-r--r-- (standard file)
chmod 755 script.sh             # rwxr-xr-x (executable script)
chmod 700 private.key           # rwx------ (private file)
chmod 600 api_key.txt           # rw------- (secrets)
chmod 777 dangerous.sh          # rwxrwxrwx (AVOID - security risk!)
chmod 444 readonly.txt          # r--r--r-- (read-only)

# Directories
chmod 755 public_dir/           # rwxr-xr-x (standard directory)
chmod 750 team_dir/             # rwxr-x--- (team-accessible)
chmod 700 private_dir/          # rwx------ (private directory)
chmod 775 shared_dir/           # rwxrwxr-x (team-writable)
```

### Recursive Permission Changes

```bash
# Change permissions recursively
chmod -R 755 project/           # All files and directories

# Directories only
find project/ -type d -exec chmod 755 {} \;

# Files only
find project/ -type f -exec chmod 644 {} \;

# Set directories to 755 and files to 644
chmod -R u+rwX,g+rX,o+rX project/
# Capital X: adds execute only to directories and already-executable files
```

### AI Infrastructure Permission Patterns

```bash
# Model files (read-only for group)
chmod 640 models/*.h5
# rw-r----- : Owner can update, team can read, others blocked

# Training scripts (executable)
chmod 750 scripts/train.py
# rwxr-x--- : Owner can modify/run, team can run, others blocked

# Configuration files
chmod 640 config/*.yaml
# rw-r----- : Owner can edit, team can read

# API keys and secrets
chmod 600 .env secrets.yaml
# rw------- : Owner only, completely private

# Shared dataset directory
chmod 775 /data/shared/
# rwxrwxr-x : Team can add/modify, others can read

# Log files
chmod 664 logs/*.log
# rw-rw-r-- : Owner and group can write, others can read

# Temporary processing directory
chmod 1777 /data/temp/
# rwxrwxrwt : Everyone can use, sticky bit prevents deletion by others
```

### Permission Troubleshooting

```bash
# "Permission denied" when reading file
ls -l file.txt                  # Check if you have read permission
# Fix: chmod u+r file.txt (if you're owner) or contact owner

# "Permission denied" when running script
ls -l script.sh                 # Check execute permission
# Fix: chmod u+x script.sh

# Cannot cd into directory
ls -ld directory/               # Check execute permission on directory
# Fix: chmod u+x directory/

# Cannot create files in directory
ls -ld directory/               # Check write permission
# Fix: chmod u+w directory/

# Check effective permissions
namei -l /path/to/file          # Shows permissions for entire path
```

## Changing Ownership with chown

`chown` (change owner) modifies file ownership.

### Basic Syntax

```bash
# Change owner
sudo chown alice file.txt

# Change owner and group
sudo chown alice:mlteam file.txt

# Change group only (using chown)
sudo chown :mlteam file.txt

# Recursive
sudo chown -R alice:mlteam project/

# Preserve symbolic links
sudo chown -h alice link_name
```

### Using chgrp

`chgrp` changes only the group owner.

```bash
# Change group
sudo chgrp mlteam file.txt

# Recursive
sudo chgrp -R mlteam project/

# Verbose output
sudo chgrp -v mlteam file.txt
```

### Practical Examples

```bash
# Transfer project ownership when employee leaves
sudo chown -R newowner:mlteam /projects/alice_project/

# Set up shared dataset directory
sudo mkdir /data/shared/imagenet
sudo chown root:mlteam /data/shared/imagenet
sudo chmod 775 /data/shared/imagenet
# Now mlteam members can add/modify files

# Fix ownership after extracting archive
tar -xzf archive.tar.gz
sudo chown -R alice:mlteam extracted_directory/

# Set ownership for web server
sudo chown -R www-data:www-data /var/www/ml-api/

# Docker volume ownership
sudo chown -R 1000:1000 /docker/volumes/ml-data/
```

### Combining chown and chmod

```bash
# Set up new project directory
sudo mkdir /projects/new_model
sudo chown alice:mlteam /projects/new_model
sudo chmod 770 /projects/new_model
# Result: Alice owns, mlteam can fully access, others blocked

# Secure secret file
sudo chown alice:alice .api_key
sudo chmod 600 .api_key
# Result: Only alice can read/write

# Shared model repository
sudo mkdir /models/production
sudo chown root:mlteam /models/production
sudo chmod 2775 /models/production  # Note: 2 sets setgid (covered next)
# Result: Team can add models, all new files inherit mlteam group
```

## Special Permissions

Beyond standard rwx, Linux has three special permissions.

### Setuid (Set User ID) - 4

When set on an executable, it runs with owner's permissions, not executor's.

```bash
# Syntax: chmod u+s file or chmod 4755 file
chmod u+s program
chmod 4755 program
# -rwsr-xr-x : Notice 's' instead of 'x' for owner

# Real example: passwd command
ls -l /usr/bin/passwd
# -rwsr-xr-x root root /usr/bin/passwd
# Any user can run passwd, but it executes as root (needs root to modify /etc/shadow)
```

**AI Infrastructure Use Case**:
```bash
# GPU monitoring tool that needs elevated access
sudo chown root:mlteam /usr/local/bin/gpu-monitor
sudo chmod 4750 /usr/local/bin/gpu-monitor
# mlteam members can run it, executes with root privileges to access GPU stats
```

**Security Warning**: Setuid is dangerous if misused. Carefully review any setuid programs.

### Setgid (Set Group ID) - 2

**On Executables**: Runs with group permissions of the file, not executor's group.

**On Directories**: New files inherit the directory's group, not creator's primary group.

```bash
# Syntax: chmod g+s file/dir or chmod 2755 file/dir
chmod g+s directory/
chmod 2775 directory/
# drwxrwsr-x : Notice 's' instead of 'x' for group

# Practical use: Shared project directory
sudo mkdir /projects/shared
sudo chown root:mlteam /projects/shared
sudo chmod 2775 /projects/shared
# Now when anyone creates a file here, it automatically gets group 'mlteam'
```

**Example**:
```bash
# Without setgid
cd /normal/directory
touch file.txt
ls -l file.txt
# -rw-r--r-- alice alice file.txt  (creator's primary group)

# With setgid
cd /projects/shared  # Has setgid set, group is mlteam
touch file.txt
ls -l file.txt
# -rw-r--r-- alice mlteam file.txt  (directory's group inherited!)
```

### Sticky Bit - 1

Prevents users from deleting files they don't own in a directory, even if they have write permission.

```bash
# Syntax: chmod +t directory or chmod 1777 directory
chmod +t /shared/temp/
chmod 1777 /shared/temp/
# drwxrwxrwt : Notice 't' instead of 'x' for others

# Classic example: /tmp
ls -ld /tmp
# drwxrwxrwt root root /tmp
# Anyone can create files, but can only delete their own
```

**AI Infrastructure Use Case**:
```bash
# Shared temporary processing directory
sudo mkdir /data/temp
sudo chmod 1777 /data/temp
# Everyone can create temp files, but can't delete others' files
```

### Viewing Special Permissions

```bash
# Find setuid files (potential security risks)
find / -perm -4000 -type f 2>/dev/null

# Find setgid files
find / -perm -2000 -type f 2>/dev/null

# Find sticky bit directories
find / -perm -1000 -type d 2>/dev/null

# Find files with any special permissions
find /path -perm /7000 -ls
```

### Numeric Notation with Special Permissions

```
[special][user][group][others]
   4       7     5      5

4000 = setuid
2000 = setgid
1000 = sticky bit
```

**Examples**:
```bash
chmod 4755 file     # setuid, rwxr-xr-x
chmod 2755 dir      # setgid, rwxr-sr-x
chmod 1777 dir      # sticky, rwxrwxrwt
chmod 6755 file     # setuid+setgid, rwsr-sr-x
chmod 7755 dir      # all special permissions
```

## Default Permissions and umask

`umask` sets default permissions for newly created files and directories.

### Understanding umask

**umask** is a mask that *subtracts* permissions from the default:
- Default for files: `666` (rw-rw-rw-)
- Default for directories: `777` (rwxrwxrwx)
- umask is subtracted from these defaults

**Common umask Values**:
```
umask 022:
  Files: 666 - 022 = 644 (rw-r--r--)
  Dirs:  777 - 022 = 755 (rwxr-xr-x)

umask 002:
  Files: 666 - 002 = 664 (rw-rw-r--)
  Dirs:  777 - 002 = 775 (rwxrwxr-x)

umask 077:
  Files: 666 - 077 = 600 (rw-------)
  Dirs:  777 - 077 = 700 (rwx------)

umask 027:
  Files: 666 - 027 = 640 (rw-r-----)
  Dirs:  777 - 027 = 750 (rwxr-x---)
```

### Viewing and Setting umask

```bash
# View current umask
umask
# 0022

# View in symbolic notation
umask -S
# u=rwx,g=rx,o=rx

# Set umask for current session
umask 027                       # More restrictive
umask 002                       # More permissive

# Test new umask
touch testfile
mkdir testdir
ls -ld testfile testdir
```

### Making umask Permanent

```bash
# For single user: ~/.bashrc or ~/.profile
echo "umask 027" >> ~/.bashrc

# For all users: /etc/profile or /etc/bash.bashrc
sudo sh -c 'echo "umask 027" >> /etc/profile'

# For specific group (in their shell config)
if groups | grep -q mlteam; then
    umask 002  # Permissive for team collaboration
else
    umask 077  # Restrictive for others
fi
```

### AI Infrastructure Recommendations

```bash
# General users: umask 022 (standard)
# Files: 644, Directories: 755

# Development teams: umask 002 (collaborative)
# Files: 664, Directories: 775
# Combine with setgid on shared directories

# Security-focused: umask 077 (restrictive)
# Files: 600, Directories: 700
# Use for systems handling sensitive data

# Recommended for ML engineers in team environment
umask 002
```

## Access Control Lists (ACLs)

ACLs provide fine-grained permissions beyond user/group/others.

### Why ACLs?

Standard permissions are limited to one user and one group. ACLs allow:
- Multiple users with different permissions
- Multiple groups with different permissions
- Default permissions for new files in directories

### Viewing ACLs

```bash
# Check if file has ACL
ls -l file.txt
# -rw-r--r--+ : The '+' indicates ACL is set

# View ACL details
getfacl file.txt
# # file: file.txt
# # owner: alice
# # group: mlteam
# user::rw-
# user:bob:r--
# user:charlie:rw-
# group::r--
# group:dataeng:rw-
# mask::rw-
# other::r--
```

### Setting ACLs

```bash
# Grant user bob read access
setfacl -m u:bob:r file.txt

# Grant user charlie read+write access
setfacl -m u:charlie:rw file.txt

# Grant group dataeng read+write access
setfacl -m g:dataeng:rw file.txt

# Remove specific ACL entry
setfacl -x u:bob file.txt

# Remove all ACLs
setfacl -b file.txt

# Recursive ACL
setfacl -R -m u:bob:r directory/
```

### Default ACLs for Directories

```bash
# Set default ACL for new files in directory
setfacl -d -m u:bob:rw /projects/shared/
# Now all new files created in /projects/shared/ will give bob rw access

# Combine with normal ACL
setfacl -m u:bob:rwx /projects/shared/          # For existing content
setfacl -d -m u:bob:rw /projects/shared/        # For new content

# View default ACL
getfacl /projects/shared/
```

### Practical ACL Examples

```bash
# Scenario: Multiple teams need different access to dataset
sudo setfacl -m g:mlteam:rwx /data/shared-dataset/
sudo setfacl -m g:dataeng:r-x /data/shared-dataset/
sudo setfacl -m g:analysts:r-- /data/shared-dataset/
# mlteam: full access, dataeng: read+list, analysts: read only

# Grant specific user access to model repository
setfacl -m u:alice:rwx /models/production/
setfacl -m u:bob:r-x /models/production/
# alice can modify, bob can read

# Set up shared project with defaults
sudo setfacl -m g:mlteam:rwx /projects/experiment/
sudo setfacl -d -m g:mlteam:rwx /projects/experiment/
sudo setfacl -d -m u::rwx /projects/experiment/
sudo setfacl -d -m o::--- /projects/experiment/
# Team has full access, new files inherit team access, others blocked
```

### Copying and Backing Up ACLs

```bash
# Backup ACLs
getfacl -R /projects/shared > acl_backup.txt

# Restore ACLs
setfacl --restore=acl_backup.txt

# Copy ACLs from one directory to another
getfacl /source/dir | setfacl --set-file=- /dest/dir
```

## Security Best Practices for AI Infrastructure

### 1. Principle of Least Privilege

Grant minimum necessary permissions.

```bash
# Bad: Everyone has full access
chmod 777 sensitive_data/

# Good: Specific access only
chmod 750 sensitive_data/
chown alice:mlteam sensitive_data/
# Alice: full control, mlteam: read+execute, others: none
```

### 2. Protect Sensitive Data

```bash
# API keys and secrets
chmod 600 .env api_keys.yaml
chown alice:alice .env

# SSH keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 644 ~/.ssh/authorized_keys

# Model weights (proprietary)
chmod 640 models/proprietary_*.h5
chown alice:mlteam models/proprietary_*.h5

# Database credentials
chmod 600 database.conf
```

### 3. Secure Shared Resources

```bash
# Shared dataset - read-only for most
sudo mkdir /data/shared/imagenet
sudo chown root:mlteam /data/shared/imagenet
sudo chmod 755 /data/shared/imagenet
# Only root can modify, everyone can read

# Team workspace - collaborative
sudo mkdir /projects/team-workspace
sudo chown root:mlteam /projects/team-workspace
sudo chmod 2775 /projects/team-workspace
# Team can collaborate, new files inherit mlteam group

# Temporary processing - with sticky bit
sudo mkdir /data/temp-processing
sudo chmod 1777 /data/temp-processing
# Everyone can create files, can't delete others' files
```

### 4. Audit Permissions Regularly

```bash
# Find world-writable files (security risk)
find /home -type f -perm -002 2>/dev/null

# Find setuid/setgid files (potential privilege escalation)
find / -perm -4000 -o -perm -2000 -type f 2>/dev/null | tee setuid_files.txt

# Find files with no owner (orphaned files)
find / -nouser -o -nogroup 2>/dev/null

# Find recently modified files
find /etc -mtime -7 -type f

# Check who can access sensitive directories
ls -la /data/sensitive/
getfacl /data/sensitive/
```

### 5. Implement Role-Based Access

```bash
# Create groups for roles
sudo groupadd ml-developers
sudo groupadd ml-researchers
sudo groupadd ml-operations
sudo groupadd data-engineers

# Assign users to appropriate groups
sudo usermod -aG ml-developers alice
sudo usermod -aG ml-researchers bob
sudo usermod -aG ml-operations charlie

# Set up directories with role-based permissions
sudo mkdir /projects/{development,research,production}
sudo chown root:ml-developers /projects/development
sudo chown root:ml-researchers /projects/research
sudo chown root:ml-operations /projects/production
sudo chmod 2770 /projects/*
```

### 6. Secure GPU Access

```bash
# Restrict GPU access to specific group
sudo groupadd gpu-users
sudo usermod -aG gpu-users alice

# Set GPU device permissions (in /etc/udev/rules.d/)
sudo sh -c 'echo "KERNEL==\"nvidia*\", GROUP=\"gpu-users\", MODE=\"0660\"" > /etc/udev/rules.d/70-gpu-access.rules'
sudo udevadm control --reload-rules
```

### 7. Log File Security

```bash
# Logs should be readable but not writable by applications
chmod 644 /var/log/ml-training/*.log
chown root:adm /var/log/ml-training/

# Sensitive logs
chmod 640 /var/log/auth.log
chmod 640 /var/log/ml-api/access.log
```

### 8. Script Security

```bash
# Make scripts read-only after testing
chmod 555 production_train.py

# Scripts with secrets should be restricted
chmod 700 deploy_with_credentials.sh

# Use setgid for team scripts
sudo chown root:mlteam /scripts/shared_train.sh
sudo chmod 2755 /scripts/shared_train.sh
```

### 9. Automated Permission Checks

```bash
# Create audit script
cat > /usr/local/bin/permission-audit.sh << 'EOF'
#!/bin/bash
echo "=== Permission Audit $(date) ===" | tee -a /var/log/permission-audit.log
echo "World-writable files:"
find /home -type f -perm -002 2>/dev/null | tee -a /var/log/permission-audit.log
echo "Setuid/Setgid files:"
find / -perm -4000 -o -perm -2000 -type f 2>/dev/null | tee -a /var/log/permission-audit.log
echo "Orphaned files:"
find /home -nouser -o -nogroup 2>/dev/null | tee -a /var/log/permission-audit.log
EOF

sudo chmod 755 /usr/local/bin/permission-audit.sh

# Schedule weekly audit (add to crontab)
sudo crontab -e
# 0 2 * * 0 /usr/local/bin/permission-audit.sh
```

### 10. Docker and Container Security

```bash
# Docker volumes should have appropriate ownership
sudo chown -R 1000:1000 /docker/volumes/ml-data
sudo chmod 755 /docker/volumes/ml-data

# Docker daemon group (allows Docker access without sudo)
sudo groupadd docker
sudo usermod -aG docker alice
# Note: This is convenient but reduces security - use carefully
```

## Summary and Key Takeaways

### Commands Mastered

**Permission Commands**:
- `chmod` - Change file permissions (symbolic or numeric)
- `chown` - Change file owner and group
- `chgrp` - Change file group
- `umask` - Set default permissions for new files

**User/Group Management**:
- `useradd`/`adduser` - Create users
- `usermod` - Modify users
- `userdel` - Delete users
- `groupadd` - Create groups
- `gpasswd` - Manage group membership

**ACL Commands**:
- `getfacl` - View ACLs
- `setfacl` - Set ACLs

**Information Commands**:
- `whoami` - Current user
- `id` - User/group IDs
- `groups` - User groups
- `who`/`w` - Logged-in users

### Permission Patterns Quick Reference

```bash
# Files
600 (rw-------)  Secret files (API keys, private keys)
640 (rw-r-----)  Shared configs, readable by group
644 (rw-r--r--)  Standard files, readable by all
664 (rw-rw-r--)  Team-editable files
755 (rwxr-xr-x)  Executable scripts, public

# Directories
700 (rwx------)  Private directories
750 (rwxr-x---)  Team-readable directories
755 (rwxr-xr-x)  Public directories
770 (rwxrwx---)  Team-collaborative directories
775 (rwxrwxr-x)  Team-writable, public-readable
1777 (rwxrwxrwt) Shared temp (sticky bit)
2775 (rwxrwsr-x) Team-collaborative with setgid
```

### Key Concepts

1. **Three Permission Levels**: user, group, others (ugo)
2. **Three Permission Types**: read, write, execute (rwx)
3. **Two Notations**: symbolic (u+x) and numeric (755)
4. **Special Permissions**: setuid (4), setgid (2), sticky bit (1)
5. **Default Permissions**: Controlled by umask
6. **ACLs**: Fine-grained permissions beyond standard ugo

### Security Principles

✅ **Principle of Least Privilege**: Minimum necessary access
✅ **Defense in Depth**: Multiple security layers
✅ **Regular Audits**: Check permissions periodically
✅ **Document Access**: Know who has access to what
✅ **Secure Defaults**: Restrictive umask
✅ **Group-Based Access**: Use groups for team access
✅ **Protect Secrets**: 600 permissions for sensitive files

### AI Infrastructure Best Practices

1. **Dataset Security**: Read-only for most users (755 directories, 644 files)
2. **Model Protection**: Restrict write access (640 for proprietary models)
3. **Team Collaboration**: Use setgid directories with group access (2775)
4. **API Keys**: Strict permissions (600), owner-only access
5. **Shared Resources**: Sticky bit for temp directories (1777)
6. **GPU Access**: Group-based access control
7. **Log Files**: Readable but not writable by applications (644)
8. **Scripts**: Read-only in production (555 or 755)

### Common Mistakes to Avoid

❌ `chmod 777` - Never use unless absolutely necessary and temporary
❌ Running services as root - Use dedicated service accounts
❌ Storing secrets in world-readable files
❌ Ignoring file ownership when extracting archives
❌ Forgetting to set umask for team environments
❌ Not using setgid on shared team directories
❌ Overlooking ACLs for complex permission scenarios
❌ Not auditing permissions regularly

### Troubleshooting Guide

**Problem**: "Permission denied" when reading file
- **Check**: `ls -l file` - Do you have read permission?
- **Fix**: `chmod u+r file` (if owner) or contact owner

**Problem**: Cannot write to directory
- **Check**: `ls -ld directory` - Do you have write+execute?
- **Fix**: `chmod u+wx directory`

**Problem**: Script won't execute
- **Check**: `ls -l script.sh` - Execute permission set?
- **Fix**: `chmod u+x script.sh`

**Problem**: Created files have wrong group
- **Check**: `ls -ld directory` - Is setgid set?
- **Fix**: `chmod g+s directory`

**Problem**: Other users deleting my files in shared directory
- **Check**: Directory permissions
- **Fix**: `chmod +t directory` (sticky bit)

### Practice Exercises

1. Create a multi-user ML project structure with appropriate permissions
2. Set up a secure shared dataset directory with ACLs
3. Configure umask for team collaboration
4. Audit system for world-writable files
5. Implement role-based access for ML teams
6. Secure API keys and credentials
7. Set up setgid directories for automatic group inheritance

### Next Steps

In **Lecture 03: Process Management**, you'll learn:
- Understanding processes and system resources
- Monitoring with ps, top, htop
- Managing services with systemd
- Job control and background processes
- Resource limits and priorities

### Additional Resources

- **Man Pages**: `man chmod`, `man chown`, `man setfacl`, `man umask`
- **Linux Security**: "Understanding Linux File Permissions" (LinuxAcademy)
- **ACL Guide**: Red Hat documentation on ACLs
- **Security Hardening**: CIS Benchmarks for Linux

### Quick Reference Card

```bash
# View permissions
ls -l file                    # Standard view
ls -ld directory             # Directory itself
getfacl file                 # ACL view
id                           # Current user info
groups                       # Current user groups

# Change permissions
chmod 644 file               # Numeric
chmod u+x file               # Symbolic
chmod -R 755 dir/            # Recursive

# Change ownership
chown user:group file        # Owner and group
chown -R user:group dir/     # Recursive
chgrp group file             # Group only

# Special permissions
chmod u+s file               # Setuid
chmod g+s dir                # Setgid
chmod +t dir                 # Sticky bit
chmod 4755 file              # Setuid numeric

# ACLs
setfacl -m u:bob:rw file     # Grant user access
setfacl -m g:team:r file     # Grant group access
setfacl -x u:bob file        # Remove ACL entry
setfacl -b file              # Remove all ACLs

# Default permissions
umask                        # View umask
umask 027                    # Set umask
```

---

**End of Lecture 02**

Continue to **Lecture 03: Process Management** to learn how to monitor and manage running processes and system services.
