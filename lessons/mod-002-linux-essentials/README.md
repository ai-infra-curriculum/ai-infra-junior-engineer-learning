# Module 002: Linux Essentials for AI Infrastructure

## Module Overview

This module provides a comprehensive foundation in Linux systems administration, essential for any AI Infrastructure Engineer. You'll learn to navigate Linux environments, manage systems, automate tasks through scripting, and understand networking fundamentals. These skills form the backbone of infrastructure engineering, as most AI/ML workloads run on Linux-based systems.

By the end of this module, you'll be comfortable working in Linux environments, writing shell scripts to automate common tasks, managing system resources, and troubleshooting basic system issues.

## Learning Objectives

By completing this module, you will be able to:

1. **Navigate and manipulate files** using Linux command-line interface
2. **Manage users, groups, and permissions** to secure systems appropriately
3. **Monitor system resources** (CPU, memory, disk, network) and identify bottlenecks
4. **Write shell scripts** to automate repetitive infrastructure tasks
5. **Configure networking** including interfaces, DNS, and basic troubleshooting
6. **Manage processes and services** using systemd and traditional process management
7. **Perform basic system administration** tasks like package management and log analysis
8. **Troubleshoot common system issues** using appropriate diagnostic tools
9. **Work with text processing tools** (grep, sed, awk) for log analysis
10. **Understand Linux filesystem hierarchy** and storage management

## Prerequisites

- Basic computer literacy and comfort with text-based interfaces
- Completion of Module 001 (Python Fundamentals) recommended but not required
- Access to a Linux system (VM, WSL, or native installation)
- Willingness to practice commands and experiment safely

**Recommended Setup:**
- Ubuntu 22.04 LTS or similar distribution (virtual machine acceptable)
- Terminal emulator of your choice
- Text editor (vim, nano, or VS Code with remote SSH)
- At least 2GB RAM and 20GB disk space for practice environment

## Time Commitment

- **Total Estimated Time:** 40-50 hours
- **Lectures & Reading:** 15-20 hours
- **Hands-on Exercises:** 20-25 hours
- **Practice & Review:** 5-10 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-6 weeks
- Full-time (20-30 hrs/week): 2-3 weeks

This module is designed for flexibility. You can move faster through familiar topics and spend more time on challenging areas.

## Module Structure

### Week 1: Linux Fundamentals
- **Topics:** Command-line basics, file system navigation, file operations
- **Key Skills:** ls, cd, cp, mv, rm, mkdir, file permissions
- **Practice:** 10-15 exercises building muscle memory for essential commands

### Week 2: System Administration Basics
- **Topics:** User management, package management, process control
- **Key Skills:** useradd, apt/yum, ps, kill, top, systemctl
- **Practice:** Setting up users, installing software, managing services

### Week 3: Shell Scripting
- **Topics:** Bash scripting fundamentals, variables, control structures, functions
- **Key Skills:** Writing automation scripts, error handling, argument processing
- **Practice:** Creating scripts for backup, monitoring, and deployment tasks

### Week 4: Networking & Advanced Topics
- **Topics:** Networking basics, text processing, system monitoring
- **Key Skills:** ip, netstat, ssh, grep, sed, awk, monitoring tools
- **Practice:** Network troubleshooting, log analysis, performance monitoring

## Detailed Topic Breakdown

### 1. Command-Line Fundamentals (6-8 hours)

#### 1.1 Getting Started with the Shell
- Terminal emulators and shell types (bash, zsh, sh)
- Command syntax and structure
- Getting help: man pages, --help, info
- Command history and tab completion
- Environment variables and PATH

#### 1.2 File System Navigation
- Linux file system hierarchy (/, /home, /etc, /var, /usr)
- Absolute vs relative paths
- Essential navigation commands (cd, pwd, ls)
- Working with directories (mkdir, rmdir, tree)
- Finding files (find, locate, which, whereis)

#### 1.3 File Operations
- Creating and editing files (touch, nano, vim)
- Copying, moving, and deleting (cp, mv, rm)
- Viewing file contents (cat, less, more, head, tail)
- File types and extensions
- Links (hard links vs symbolic links)
- Archiving and compression (tar, gzip, zip)

#### 1.4 File Permissions and Ownership
- Understanding Linux permission model (rwx)
- Numeric and symbolic notation (chmod)
- Changing ownership (chown, chgrp)
- Special permissions (setuid, setgid, sticky bit)
- umask and default permissions
- Access Control Lists (ACLs) introduction

### 2. System Administration (8-10 hours)

#### 2.1 User and Group Management
- Understanding /etc/passwd and /etc/group
- Creating users (useradd, adduser)
- Modifying users (usermod, passwd)
- Group management (groupadd, groupmod)
- Sudo and privilege escalation
- User authentication and security best practices

#### 2.2 Package Management
- Understanding package managers (apt, yum, dnf)
- Installing, updating, and removing packages
- Managing repositories
- Handling dependencies
- System updates and upgrades
- Building from source when necessary

#### 2.3 Process Management
- Understanding processes and PIDs
- Viewing processes (ps, top, htop)
- Process states and priorities
- Killing processes (kill, killall, pkill)
- Background and foreground jobs (&, fg, bg)
- Process scheduling (nice, renice)
- Process signals (SIGTERM, SIGKILL, SIGHUP)

#### 2.4 Service Management with systemd
- Understanding systemd architecture
- Managing services (systemctl start/stop/restart/status)
- Enabling services at boot
- Viewing service logs (journalctl)
- Creating custom service units
- Timers as cron alternatives

### 3. Shell Scripting and Automation (10-12 hours)

#### 3.1 Bash Scripting Basics
- Script structure and shebang (#!/bin/bash)
- Variables and data types
- Command substitution
- Quoting rules (single, double, backticks)
- Exit codes and error handling
- Script debugging (set -x, set -e)

#### 3.2 Control Structures
- Conditional statements (if/elif/else)
- Test operators (file, string, numeric)
- Case statements
- Loops (for, while, until)
- Break and continue
- Functions and scope

#### 3.3 Advanced Scripting Techniques
- Command-line argument processing
- Reading user input
- Working with arrays
- String manipulation
- Regular expressions basics
- Error handling and logging
- Script templates for common tasks

#### 3.4 Practical Automation Scripts
- System backup scripts
- Log rotation and cleanup
- Health check scripts
- Deployment automation basics
- Monitoring and alerting scripts
- Batch processing workflows

### 4. Text Processing and Log Analysis (6-8 hours)

#### 4.1 Text Viewing and Search
- Pattern matching with grep
- Regular expressions in practice
- Recursive searching
- Finding and replacing text
- Working with multiple files
- Performance considerations

#### 4.2 Stream Editing with sed
- Basic sed syntax
- Find and replace operations
- Line-based editing
- In-place file editing
- Multi-line operations
- Practical sed use cases

#### 4.3 Text Processing with awk
- AWK basics and syntax
- Field and record processing
- Pattern matching and actions
- Built-in variables
- Arithmetic and string operations
- Generating reports from logs

#### 4.4 Log Analysis Workflows
- Understanding common log formats
- Apache/Nginx access logs
- System logs (/var/log/)
- Application logs
- Combining tools for complex analysis
- Building log analysis pipelines

### 5. Networking Fundamentals (6-8 hours)

#### 5.1 Network Basics
- TCP/IP fundamentals
- IP addressing and subnetting
- DNS concepts and resolution
- Ports and protocols
- OSI model overview
- Understanding network interfaces

#### 5.2 Network Configuration
- Viewing network configuration (ip, ifconfig)
- Configuring network interfaces
- Static vs DHCP addressing
- Network manager and netplan
- Hostname and DNS configuration
- Routing basics

#### 5.3 Network Diagnostics
- Connectivity testing (ping, traceroute)
- Port scanning basics (netstat, ss)
- Packet capture (tcpdump basics)
- Network performance testing
- Troubleshooting methodology
- Common network issues

#### 5.4 Remote Access and Transfer
- SSH fundamentals
- SSH key-based authentication
- Secure file transfer (scp, rsync)
- SSH tunneling basics
- Remote command execution
- SSH configuration and best practices

### 6. System Monitoring and Performance (6-8 hours)

#### 6.1 Resource Monitoring
- CPU monitoring (top, htop, mpstat)
- Memory analysis (free, vmstat)
- Disk usage (df, du, iostat)
- Network statistics (iftop, nethogs)
- System load and uptime
- Resource limits (ulimit)

#### 6.2 System Logs
- Understanding syslog
- Log locations and organization
- Reading log files
- Log rotation with logrotate
- Centralized logging concepts
- Parsing and analyzing logs

#### 6.3 Performance Tuning Basics
- Identifying bottlenecks
- CPU vs I/O bound processes
- Memory management and swap
- Disk I/O optimization
- Network tuning basics
- Performance monitoring tools

#### 6.4 Troubleshooting Methodology
- Systematic problem-solving approach
- Gathering system information
- Isolating issues
- Common system problems
- Documentation and logging
- When to escalate issues

## Lecture Outline

> **Note:** Full lecture materials are currently in development. Placeholder files are available in the `lecture-notes/` directory. Complete lecture notes will be added in upcoming updates.

### Lecture 1: Introduction to Linux and Command Line (90 min)
- History and philosophy of Linux
- Distribution landscape
- Terminal emulators and shells
- Basic command structure
- Getting help and documentation
- **Lab:** Setting up your Linux environment

### Lecture 2: File System and Navigation (90 min)
- Linux filesystem hierarchy standard
- Path concepts and navigation
- File operations and manipulation
- Working with directories
- Finding files
- **Lab:** File system exploration exercises

### Lecture 3: Permissions and Security (90 min)
- Linux permission model
- Users and groups
- Ownership and permissions
- Special permissions
- Sudo and privilege escalation
- **Lab:** Setting up multi-user environment

### Lecture 4: System Administration Basics (120 min)
- Package management
- Service management with systemd
- Process management
- System monitoring
- Log files
- **Lab:** Managing a Linux system

### Lecture 5: Introduction to Shell Scripting (90 min)
- Why shell scripting?
- Script structure and syntax
- Variables and data types
- Basic control structures
- Functions
- **Lab:** Writing your first scripts

### Lecture 6: Advanced Shell Scripting (120 min)
- Advanced control structures
- Error handling
- Argument processing
- Debugging techniques
- Best practices
- **Lab:** Building automation scripts

### Lecture 7: Text Processing Tools (90 min)
- grep and regular expressions
- sed for stream editing
- awk for text processing
- Combining tools with pipes
- Practical log analysis
- **Lab:** Analyzing web server logs

### Lecture 8: Networking Fundamentals (120 min)
- TCP/IP basics
- Network configuration
- SSH and remote access
- Network diagnostics
- Security considerations
- **Lab:** Network troubleshooting scenarios

## Hands-On Exercises

> **Note:** Detailed exercise instructions are being developed. Placeholder files are available in the `exercises/` directory. Complete exercises will be added in upcoming updates.

### Exercise Categories

#### Basic Skills (10 exercises)
1. Command-line navigation challenge
2. File manipulation workflow
3. Permission configuration scenarios
4. User management tasks
5. Package installation exercise
6. Process management practice
7. Service configuration
8. Basic script writing
9. Text search and manipulation
10. Network configuration basics

#### Intermediate Challenges (10 exercises)
11. Advanced file operations and scripting
12. System monitoring and analysis
13. Log analysis pipeline
14. Backup script creation
15. Service deployment automation
16. Multi-step troubleshooting scenarios
17. Network diagnostics challenge
18. Performance tuning exercise
19. Security hardening tasks
20. Complete system administration workflow

#### Integration Projects (5 exercises)
21. System health check script
22. Automated deployment pipeline (basic)
23. Log monitoring and alerting system
24. User provisioning automation
25. Complete system setup from scratch

## Assessment and Evaluation

### Knowledge Checks
- Quiz after each major section (6 quizzes total)
- Command recall exercises
- Concept explanation questions
- Troubleshooting scenario analysis

### Practical Assessments
- **Hands-on Labs:** Complete all 25 exercises with working solutions
- **Script Portfolio:** Create 5 automation scripts demonstrating key concepts
- **System Setup:** Configure a complete Linux system to specifications
- **Troubleshooting Challenge:** Diagnose and fix 10 system issues

### Competency Criteria
To complete this module successfully, you should be able to:
- Navigate and manage files confidently via command line
- Write functional shell scripts for common automation tasks
- Perform basic system administration tasks independently
- Troubleshoot common system and network issues
- Read and analyze log files effectively
- Configure and manage services using systemd
- Demonstrate security awareness in system administration

### Self-Assessment Questions
1. Can you confidently navigate any Linux system using only the command line?
2. Can you write a script to automate a multi-step task?
3. Can you diagnose why a service isn't starting?
4. Can you analyze logs to identify issues?
5. Can you configure network settings and troubleshoot connectivity?
6. Can you manage users and permissions securely?
7. Can you monitor system resources and identify bottlenecks?

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- Linux man pages (available on any system via `man` command)
- The Linux Documentation Project (tldp.org)
- Ubuntu Official Documentation
- Red Hat Enterprise Linux Documentation

### Recommended Books
- "The Linux Command Line" by William Shotts (free online)
- "Unix and Linux System Administration Handbook" by Evi Nemeth et al.
- "Learning the bash Shell" by Cameron Newham

### Online Learning
- Linux Journey (linuxjourney.com)
- OverTheWire: Bandit (wargames challenges)
- Digital Ocean Tutorials
- Red Hat Learning Subscription

### Practice Environments
- Local VM (VirtualBox, VMware, Hyper-V)
- Windows Subsystem for Linux (WSL2)
- Cloud instances (AWS EC2 free tier, GCP, Azure)
- Docker containers for safe experimentation

## Getting Started

### Step 1: Set Up Your Environment
1. Install or access a Linux system (Ubuntu 22.04 LTS recommended)
2. Ensure you have terminal access
3. Verify you can execute basic commands
4. Set up a text editor you're comfortable with

### Step 2: Review Prerequisites
- Ensure you have basic computer literacy
- Review Python fundamentals if you completed Module 001
- Familiarize yourself with the concept of a terminal/shell

### Step 3: Begin with Lecture 1
- Read the lecture notes for Introduction to Linux
- Watch any supplementary videos
- Complete the setup lab
- Practice basic commands

### Step 4: Follow the Learning Path
- Work through lectures sequentially
- Complete exercises after each section
- Take quizzes to verify understanding
- Build your script portfolio as you progress

### Step 5: Practice Regularly
- Use Linux for daily tasks when possible
- Experiment with commands safely
- Read man pages for commands you use
- Join Linux communities for support

## Tips for Success

1. **Practice Daily:** Even 15-30 minutes of daily practice is more effective than long infrequent sessions
2. **Read Man Pages:** Get comfortable with reading documentation
3. **Break Things Safely:** Use VMs or containers to experiment without fear
4. **Build a Cheat Sheet:** Keep notes on commands and concepts you use frequently
5. **Teach Others:** Explaining concepts reinforces your understanding
6. **Automate Everything:** Look for opportunities to script repetitive tasks
7. **Join Communities:** Linux forums and IRC channels are welcoming and helpful
8. **Stay Curious:** Explore how things work under the hood

## Troubleshooting and Support

### Common Challenges

**Challenge:** Overwhelming number of commands
- **Solution:** Focus on most common commands first, build muscle memory through repetition

**Challenge:** Understanding permissions
- **Solution:** Use visual tools, practice with test files, draw diagrams

**Challenge:** Scripting seems difficult
- **Solution:** Start with simple scripts, gradually add complexity, study examples

**Challenge:** Not sure when to use which tool
- **Solution:** Practice common scenarios, build a decision tree, analyze examples

### Getting Help
- Use man pages and `--help` flags first
- Search error messages online
- Ask in module discussion forums
- Consult with mentors or study groups
- Review solutions to similar problems

## Next Steps

After completing this module, you'll be ready to:
- **Module 003:** Git and Version Control (uses command line extensively)
- **Module 005:** Docker and Containers (builds on Linux knowledge)
- **Module 010:** Cloud Platforms (applies Linux skills in cloud environments)

The skills learned here are foundational and will be used in every subsequent module.

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure and learning objectives
- Detailed topic breakdown
- Lecture outline
- Exercise framework
- Assessment criteria

**In Development:**
- Full lecture notes (300-400 lines per lecture)
- Complete exercise instructions
- Interactive quizzes
- Solution guides
- Video demonstrations
- Additional practice scenarios

**Planned Updates:**
- Advanced troubleshooting scenarios
- Container-specific Linux concepts
- Kubernetes node management
- Cloud-specific administration
- Security hardening guides

## Feedback and Contributions

This module is continuously being improved. If you have suggestions, found errors, or want to contribute:
- Open an issue in the repository
- Submit a pull request with improvements
- Share your learning experience
- Suggest additional resources

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
