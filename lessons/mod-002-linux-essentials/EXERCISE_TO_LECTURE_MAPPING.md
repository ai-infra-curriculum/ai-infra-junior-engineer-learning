# Module 002: Exercise to Lecture Mapping Analysis

**Generated**: 2025-10-28
**Module**: Linux Essentials for AI Infrastructure
**Total Exercises**: 8
**Total Lectures**: 8

---

## Executive Summary

This document provides a comprehensive analysis of all 8 exercises in Module 002, mapping them to the 8-lecture structure. Key findings:

- **Alignment Status**: 7/8 exercises need prerequisite updates
- **Coverage**: Good distribution across all lectures
- **Gaps**: Exercise 08 appears to need networking concepts from Lecture 08
- **Recommendations**: Update prerequisites to reflect new 8-lecture structure

---

## Exercise 01: Linux Navigation and File System Mastery

### Overview
- **File**: `exercise-01-navigation.md`
- **Focus**: File system navigation, directory structures, file operations, symbolic links
- **Time Required**: 60-90 minutes
- **Difficulty**: Beginner

### Current Prerequisites
- ✗ Lecture 01: Linux Fundamentals (OUTDATED - doesn't exist)
- Access to Linux system
- Terminal emulator
- 1GB free disk space

### Topics Covered
1. File system navigation (pwd, cd, ls)
2. Creating ML project directory structures
3. File operations (copy, move, delete)
4. Finding files (find, locate)
5. Symbolic links
6. ML project organization best practices

### Skills Practiced
- Navigation commands (cd, pwd, ls)
- Creating nested directories (mkdir -p)
- File operations (cp, mv, rm)
- Search commands (find)
- Symbolic link creation (ln -s)
- Creating backup scripts
- Project organization

### Mapping to NEW Lecture Structure

**Primary Lecture**: Lecture 02: File System and Navigation
- ✓ File system hierarchy
- ✓ Navigation commands
- ✓ Directory operations
- ✓ File operations
- ✓ Find command
- ✓ Symbolic links

**Secondary Lecture**: Lecture 01: Introduction to Linux and Command Line
- ✓ Basic command line usage
- ✓ Terminal basics

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed Lecture 01: Introduction to Linux and Command Line
- Completed Lecture 02: File System and Navigation
- Access to a Linux system (VM, WSL, or cloud instance)
- Terminal emulator
- At least 1GB free disk space
```

**Alignment Score**: 95% - Excellent alignment with Lecture 02

---

## Exercise 02: File Permissions and Access Control for ML Teams

### Overview
- **File**: `exercise-02-permissions.md`
- **Focus**: Linux permission model, chmod, chown, ACLs, umask
- **Time Required**: 75-90 minutes
- **Difficulty**: Intermediate

### Current Prerequisites
- ✓ Completed Exercise 01: Linux Navigation
- ✗ Completed Lecture 02: File Systems and Permissions (OUTDATED)
- Access to Linux system with sudo privileges
- Understanding of Linux user and group concepts
- 2GB free disk space

### Topics Covered
1. Linux permission model (user, group, other)
2. Numeric and symbolic chmod
3. File ownership (chown, chgrp)
4. Access Control Lists (ACLs)
5. Default permissions (umask)
6. Security best practices for ML infrastructure
7. Multi-user collaboration

### Skills Practiced
- Reading permission strings (rwxr-xr-x)
- Numeric permission calculation (755, 644, etc.)
- Using chmod (numeric and symbolic)
- Changing ownership with chown
- Setting ACLs with setfacl/getfacl
- Configuring umask
- Creating secure shared directories
- Implementing least privilege principle

### Mapping to NEW Lecture Structure

**Primary Lecture**: Lecture 03: Permissions and Security
- ✓ Permission model (rwx, ugo)
- ✓ chmod command
- ✓ chown/chgrp commands
- ✓ ACLs
- ✓ umask
- ✓ Security best practices

**Supporting Lectures**:
- Lecture 02: File System and Navigation (prerequisite knowledge)

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed Exercise 01: Linux Navigation
- Completed Lecture 02: File System and Navigation
- Completed Lecture 03: Permissions and Security
- Access to a Linux system with sudo privileges
- Understanding of Linux user and group concepts
- At least 2GB free disk space
```

**Alignment Score**: 100% - Perfect alignment with Lecture 03

---

## Exercise 03: Process Management for ML Training Jobs

### Overview
- **File**: `exercise-03-processes.md`
- **Focus**: Process monitoring, job control, signals, GPU processes, systemd services, screen/tmux
- **Time Required**: 75-90 minutes
- **Difficulty**: Intermediate

### Current Prerequisites
- ✓ Completed Exercise 01 and 02
- ✗ Completed Lecture 03: Process Management (OUTDATED - should be Lecture 04)
- Access to a Linux system
- Basic Python knowledge
- Optional: NVIDIA GPU
- 2GB RAM and 2 CPU cores

### Topics Covered
1. Process viewing (ps, top, htop)
2. Job control (background/foreground)
3. Process signals (SIGTERM, SIGKILL, etc.)
4. Monitoring ML training processes
5. GPU process management (nvidia-smi)
6. systemd service management
7. Persistent sessions (screen, tmux)
8. Troubleshooting hung processes

### Skills Practiced
- Using ps, top, htop
- Background job management (&, fg, bg, jobs)
- Sending signals (kill command)
- Creating process management wrappers
- Monitoring resource usage
- GPU process monitoring
- Using screen/tmux
- Diagnosing process issues

### Mapping to NEW Lecture Structure

**Primary Lecture**: Lecture 04: System Administration Basics
- ✓ Process concepts
- ✓ ps, top, htop commands
- ✓ Job control
- ✓ kill signals
- ✓ systemd services
- ✓ Resource monitoring

**Supporting Content**: (Not in lectures, exercise-specific)
- GPU monitoring with nvidia-smi
- ML training-specific scenarios
- screen/tmux (may need to add to lecture)

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed Exercise 01 and 02
- Completed Lecture 04: System Administration Basics
- Access to a Linux system
- Basic Python knowledge (for ML training examples)
- Optional: NVIDIA GPU for GPU monitoring sections
- At least 2GB RAM and 2 CPU cores
```

**Alignment Score**: 90% - Strong alignment, screen/tmux may need lecture coverage

---

## Exercise 04: Bash Scripting for ML Deployment Automation

### Overview
- **File**: `exercise-04-scripting.md`
- **Focus**: Bash scripting fundamentals, functions, error handling, deployment automation
- **Time Required**: 90 minutes
- **Difficulty**: Intermediate

### Current Prerequisites
- ✓ Completed Exercises 01-03
- ✗ Completed Lecture 04: Shell Scripting Basics (OUTDATED - should be Lecture 05)
- Comfortable with Linux command line
- Basic understanding of ML workflows
- Text editor (vim, nano, or VS Code)

### Topics Covered
1. Bash script structure and best practices
2. Variables and arrays
3. Control structures (if/else, loops, case)
4. Functions
5. Error handling (set -euo pipefail, trap)
6. Command-line arguments
7. Logging
8. ML deployment automation
9. Data pipeline automation
10. System monitoring scripts
11. Backup and restore scripts

### Skills Practiced
- Writing structured bash scripts
- Using functions effectively
- Handling errors gracefully
- Parsing command-line arguments
- Creating deployment scripts
- Building data pipelines
- Implementing monitoring
- Automating backups

### Mapping to NEW Lecture Structure

**Primary Lectures**:
- Lecture 05: Introduction to Shell Scripting
  - ✓ Script basics
  - ✓ Variables
  - ✓ Control structures
  - ✓ Functions

- Lecture 06: Advanced Shell Scripting
  - ✓ Error handling
  - ✓ Advanced patterns
  - ✓ Real-world examples

**Supporting Lectures**:
- Lecture 02: File System (for file operations in scripts)
- Lecture 04: System Administration (for service management scripts)

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed Exercises 01-04
- Completed Lecture 05: Introduction to Shell Scripting
- Completed Lecture 06: Advanced Shell Scripting
- Comfortable with Linux command line
- Basic understanding of ML workflows
- Text editor (vim, nano, or VS Code)
```

**Alignment Score**: 95% - Excellent alignment with Lectures 05 and 06

---

## Exercise 05: Package Management for ML Stack Installation

### Overview
- **File**: `exercise-05-package-mgmt.md`
- **Focus**: Installing system packages, Python environments, CUDA, Docker, ML frameworks
- **Time Required**: 75-90 minutes
- **Difficulty**: Intermediate

### Current Prerequisites
- ✓ Completed Exercises 01-04
- ✗ Completed Lecture 05: Package Management (OUTDATED - doesn't exist in new structure)
- Access to Linux system (Ubuntu/Debian or RHEL/CentOS)
- Sudo privileges
- Internet connection

### Topics Covered
1. Package manager basics (apt, yum, dnf)
2. System package installation
3. Python package management (pip, conda)
4. Virtual environments
5. CUDA and GPU driver installation
6. Docker installation
7. ML framework installation (TensorFlow, PyTorch)
8. Dependency management
9. Creating reproducible installations

### Skills Practiced
- Using apt/yum package managers
- Managing Python environments
- Installing system libraries
- Setting up CUDA
- Docker installation
- Creating installation scripts
- Handling dependency conflicts

### Mapping to NEW Lecture Structure

**GAP IDENTIFIED**: No dedicated lecture for package management in new structure!

**Closest Lecture**: Lecture 04: System Administration Basics
- Partial coverage of system package management
- May need to be expanded

**Recommendation**: This topic should be covered in:
- Option A: Expand Lecture 04 to include package management
- Option B: Create supplemental material for package management
- Option C: Integrate into Lecture 01 as "System Setup"

### Recommendations

**SUGGESTED UPDATE** (assuming Lecture 04 covers this):
```markdown
## Prerequisites
- Completed Exercises 01-04
- Completed Lecture 04: System Administration Basics (package management section)
- Access to a Linux system (Ubuntu/Debian or RHEL/CentOS)
- Sudo privileges (for system package installation)
- Internet connection for downloading packages
```

**Alignment Score**: 60% - SIGNIFICANT GAP, needs lecture content

**ACTION REQUIRED**: Add package management content to lectures or create supplemental material

---

## Exercise 06: Log File Analysis for ML Systems

### Overview
- **File**: `exercise-06-logs.md`
- **Focus**: Reading logs, grep/awk/sed, log analysis, journalctl, log rotation
- **Time Required**: 60-75 minutes
- **Difficulty**: Intermediate

### Current Prerequisites
- ✓ Completed Exercises 01-05
- Understanding of Linux command line
- Basic regex knowledge
- Text editor familiarity

### Topics Covered
1. Common log file locations
2. Reading logs (cat, head, tail, less)
3. Filtering with grep
4. Parsing with awk and sed
5. Training metrics extraction
6. Error pattern analysis
7. journalctl usage
8. Log rotation configuration
9. Creating log analysis scripts

### Skills Practiced
- Reading and navigating log files
- Using grep with regex patterns
- Parsing logs with awk
- Extracting metrics from logs
- Analyzing error patterns
- Using journalctl
- Configuring logrotate
- Creating analysis scripts

### Mapping to NEW Lecture Structure

**Primary Lecture**: Lecture 07: Text Processing Tools
- ✓ grep command
- ✓ awk basics
- ✓ sed basics
- ✓ Text manipulation

**Secondary Lectures**:
- Lecture 04: System Administration Basics (for journalctl, system logs)
- Lecture 06: Advanced Shell Scripting (for log analysis scripts)

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed Exercises 01-05
- Completed Lecture 07: Text Processing Tools
- Completed Lecture 04: System Administration Basics (for journalctl)
- Understanding of Linux command line
- Basic regex knowledge
- Text editor familiarity
```

**Alignment Score**: 90% - Strong alignment with Lecture 07

---

## Exercise 07: Real-World Troubleshooting Scenarios

### Overview
- **File**: `exercise-07-troubleshooting.md`
- **Focus**: Diagnosing and fixing real-world issues (disk full, permissions, hung processes, OOM, CUDA, network)
- **Time Required**: 90 minutes
- **Difficulty**: Intermediate to Advanced

### Current Prerequisites
- ✓ Completed all previous exercises (01-06)
- ✓ All lectures in Module 002
- Confidence with Linux command line
- Access to a test Linux system

### Topics Covered
1. Disk space troubleshooting
2. Permission issues
3. Hung/zombie processes
4. Out of Memory (OOM) issues
5. CUDA/GPU problems
6. Network connectivity debugging
7. Systematic troubleshooting approach
8. Creating troubleshooting checklists

### Skills Practiced
- Diagnosing disk space issues
- Fixing permission problems
- Handling stuck processes
- Managing memory issues
- Troubleshooting GPU/CUDA
- Debugging network problems
- Creating systematic workflows
- Documenting solutions

### Mapping to NEW Lecture Structure

**This exercise is INTEGRATIVE** - pulls from ALL lectures:
- Lecture 02: File System (disk space)
- Lecture 03: Permissions (permission issues)
- Lecture 04: System Administration (processes, services)
- Lecture 05/06: Shell Scripting (diagnostic scripts)
- Lecture 07: Text Processing (log analysis)
- Lecture 08: Networking Fundamentals (network issues)

### Recommendations

**Current prerequisite is CORRECT**:
```markdown
## Prerequisites
- Completed all previous exercises (01-06)
- All lectures in Module 002
- Confidence with Linux command line
- Access to a test Linux system
```

**Alignment Score**: 100% - Perfect capstone exercise integrating all concepts

---

## Exercise 08: System Automation and Maintenance for ML Infrastructure

### Overview
- **File**: `exercise-08-system-automation.md`
- **Focus**: Automated backups, monitoring, log rotation, cleanup tasks, health checks
- **Time Required**: 120 minutes
- **Difficulty**: Intermediate to Advanced

### Current Prerequisites
- ✓ Completed exercises 01-07
- ✗ All lectures in Module 002, especially Lecture 06 (Networking & System Services) (OUTDATED)
- Understanding of systemd and cron
- Access to Linux system with sudo privileges
- Basic understanding of ML workflows

### Topics Covered
1. Automated backup scripts
2. Scheduling with cron and systemd timers
3. GPU health monitoring
4. Log rotation configuration
5. Automated cleanup tasks
6. System health checks
7. Integration testing
8. Creating master automation workflows

### Skills Practiced
- Writing backup scripts
- Creating systemd services and timers
- Setting up cron jobs
- Implementing monitoring
- Configuring logrotate
- Building cleanup automation
- Creating health check scripts
- Testing automation pipelines

### Mapping to NEW Lecture Structure

**Primary Lectures**:
- Lecture 04: System Administration Basics
  - ✓ systemd services
  - ✓ cron jobs
  - ✓ System maintenance

- Lecture 06: Advanced Shell Scripting
  - ✓ Complex automation scripts
  - ✓ Error handling

**Networking Component**:
- Lecture 08: Networking Fundamentals
  - The exercise mentions "especially Lecture 06 (Networking & System Services)"
  - However, Exercise 08 doesn't heavily rely on networking concepts
  - May be a legacy reference

### Recommendations

**REQUIRED UPDATE**:
```markdown
## Prerequisites
- Completed exercises 01-07 in this module
- All lectures in Module 002, especially:
  - Lecture 04: System Administration Basics (systemd, cron)
  - Lecture 06: Advanced Shell Scripting (automation)
- Understanding of systemd and cron
- Access to a Linux system with sudo privileges
- Basic understanding of ML workflows
```

**Alignment Score**: 95% - Excellent alignment, networking reference may be outdated

---

## Summary Matrix: Exercise to Lecture Mapping

| Exercise | Primary Lecture(s) | Secondary Lecture(s) | Alignment Score | Update Needed? |
|----------|-------------------|---------------------|----------------|----------------|
| 01: Navigation | Lecture 02 | Lecture 01 | 95% | ✓ Yes - Update prereqs |
| 02: Permissions | Lecture 03 | Lecture 02 | 100% | ✓ Yes - Update prereqs |
| 03: Processes | Lecture 04 | - | 90% | ✓ Yes - Update prereqs |
| 04: Scripting | Lectures 05, 06 | Lectures 02, 04 | 95% | ✓ Yes - Update prereqs |
| 05: Package Mgmt | **GAP** | Lecture 04 (partial) | 60% | ✓ **YES - Major gap** |
| 06: Logs | Lecture 07 | Lectures 04, 06 | 90% | ✓ Yes - Update prereqs |
| 07: Troubleshooting | ALL (integrative) | - | 100% | ✗ No - Already correct |
| 08: Automation | Lectures 04, 06 | - | 95% | ✓ Yes - Update prereqs |

---

## Key Findings and Recommendations

### 1. Critical Gap: Package Management (Exercise 05)

**Issue**: Exercise 05 extensively covers package management, but there's no corresponding lecture in the 8-lecture structure.

**Impact**: HIGH - Students may not have lecture material to prepare for this exercise.

**Recommendations**:
- **Option A** (Preferred): Expand Lecture 04 to include a dedicated section on package management
  - Add apt/yum basics
  - Cover pip and virtual environments
  - Include system library installation

- **Option B**: Create supplemental reading material
  - Separate document on package management
  - Reference in Exercise 05 prerequisites

- **Option C**: Split package management across multiple lectures
  - Lecture 01: Basic package installation
  - Lecture 04: Advanced package management

### 2. Prerequisite Updates Required

**All exercises except 07** reference outdated lecture numbers. Recommended updates:

| Exercise | Current Prereq | Should Be |
|----------|---------------|-----------|
| 01 | Lecture 01: Linux Fundamentals | Lectures 01 + 02 |
| 02 | Lecture 02: File Systems | Lectures 02 + 03 |
| 03 | Lecture 03: Process Mgmt | Lecture 04 |
| 04 | Lecture 04: Shell Scripting | Lectures 05 + 06 |
| 05 | Lecture 05: Package Mgmt | **GAP - needs content** |
| 06 | (Not specified) | Lectures 07 + 04 |
| 08 | Lecture 06: Networking | Lectures 04 + 06 |

### 3. Content Coverage Analysis

**Well Covered**:
- File system navigation (Exercise 01 → Lecture 02)
- Permissions (Exercise 02 → Lecture 03)
- Processes (Exercise 03 → Lecture 04)
- Shell scripting (Exercise 04 → Lectures 05, 06)
- Text processing (Exercise 06 → Lecture 07)

**Partially Covered**:
- Package management (Exercise 05 → No primary lecture)

**Not Explicitly Covered but Used**:
- screen/tmux (Exercise 03)
- CUDA installation (Exercise 05)
- Docker setup (Exercise 05)

### 4. Exercise Difficulty Progression

Appropriate progression from beginner to advanced:
1. Exercise 01: Beginner (navigation)
2. Exercise 02: Intermediate (permissions)
3. Exercise 03: Intermediate (processes)
4. Exercise 04: Intermediate (scripting)
5. Exercise 05: Intermediate (packages)
6. Exercise 06: Intermediate (logs)
7. Exercise 07: Intermediate-Advanced (troubleshooting)
8. Exercise 08: Intermediate-Advanced (automation)

### 5. Time Allocation

Total exercise time: **9-11 hours**
- Exercise 01: 60-90 min
- Exercise 02: 75-90 min
- Exercise 03: 75-90 min
- Exercise 04: 90 min
- Exercise 05: 75-90 min
- Exercise 06: 60-75 min
- Exercise 07: 90 min
- Exercise 08: 120 min

This is reasonable for a comprehensive Linux module.

### 6. Lecture 08 (Networking) Usage

**Finding**: Lecture 08 (Networking Fundamentals) is only lightly referenced:
- Exercise 07 uses networking troubleshooting
- Exercise 08 incorrectly references it

**Recommendation**:
- Exercise 07 correctly uses networking concepts
- Exercise 08 reference should be updated
- Consider adding a dedicated networking exercise, or
- Ensure networking is covered in troubleshooting scenarios

---

## Action Items

### Immediate (High Priority)

1. **Fix Exercise 05 Gap**
   - [ ] Add package management section to Lecture 04, OR
   - [ ] Create supplemental package management guide
   - [ ] Update Exercise 05 prerequisites accordingly

2. **Update All Exercise Prerequisites**
   - [ ] Exercise 01: Update to Lectures 01, 02
   - [ ] Exercise 02: Update to Lectures 02, 03
   - [ ] Exercise 03: Update to Lecture 04
   - [ ] Exercise 04: Update to Lectures 05, 06
   - [ ] Exercise 05: Update based on #1 above
   - [ ] Exercise 06: Update to Lectures 04, 07
   - [ ] Exercise 08: Update to Lectures 04, 06

### Medium Priority

3. **Enhance Lecture Content**
   - [ ] Add screen/tmux coverage (for Exercise 03)
   - [ ] Ensure package management is comprehensively covered
   - [ ] Verify all lecture examples align with exercise topics

4. **Add Networking Exercise** (Optional)
   - [ ] Consider adding Exercise 09 for dedicated networking practice
   - [ ] Or ensure Exercise 07 adequately covers networking troubleshooting

### Low Priority

5. **Documentation**
   - [ ] Create exercise-to-lecture quick reference guide
   - [ ] Add "recommended lecture order" to module introduction
   - [ ] Update module README with exercise flow

---

## Recommended Exercise Sequence

Based on lecture dependencies:

**Phase 1: Foundation** (Complete Lectures 01-02 first)
1. Exercise 01: Navigation

**Phase 2: System Basics** (Complete Lecture 03-04)
2. Exercise 02: Permissions
3. Exercise 03: Processes
4. Exercise 05: Package Management (after gap is fixed)

**Phase 3: Automation** (Complete Lectures 05-06)
5. Exercise 04: Scripting

**Phase 4: Analysis** (Complete Lecture 07)
6. Exercise 06: Logs

**Phase 5: Integration** (Complete all lectures)
7. Exercise 07: Troubleshooting
8. Exercise 08: Automation

---

## Conclusion

The exercises in Module 002 are well-designed and comprehensive. Key findings:

**Strengths**:
- Excellent hands-on practice
- Progressive difficulty
- Real-world ML focus
- Integration exercise (07) ties everything together

**Critical Gap**:
- Exercise 05 (Package Management) lacks corresponding lecture content

**Minor Issues**:
- Outdated prerequisite references (easy to fix)
- Some advanced topics (screen/tmux) not in lectures

**Overall Assessment**: 85/100
- Would be 95/100 once package management lecture content is added
- Exercises are production-ready after prerequisite updates

---

## Appendix: Quick Reference Table

### Exercise 01: Navigation
- **Lectures**: 01, 02
- **Topics**: File system, navigation, project structure
- **Status**: ✓ Ready (needs prereq update)

### Exercise 02: Permissions
- **Lectures**: 02, 03
- **Topics**: Permissions, chmod, chown, ACLs, umask
- **Status**: ✓ Ready (needs prereq update)

### Exercise 03: Processes
- **Lectures**: 04
- **Topics**: ps, top, kill, systemd, screen/tmux
- **Status**: ✓ Ready (needs prereq update)

### Exercise 04: Scripting
- **Lectures**: 05, 06
- **Topics**: Bash scripting, automation, deployment
- **Status**: ✓ Ready (needs prereq update)

### Exercise 05: Package Management
- **Lectures**: **NONE** (GAP)
- **Topics**: apt, pip, conda, CUDA, Docker
- **Status**: ⚠ BLOCKED (needs lecture content)

### Exercise 06: Logs
- **Lectures**: 07, 04
- **Topics**: grep, awk, sed, journalctl, log rotation
- **Status**: ✓ Ready (needs prereq update)

### Exercise 07: Troubleshooting
- **Lectures**: ALL (integrative)
- **Topics**: Real-world problem solving
- **Status**: ✓ Ready (prereqs correct)

### Exercise 08: Automation
- **Lectures**: 04, 06
- **Topics**: Cron, systemd timers, monitoring, backups
- **Status**: ✓ Ready (needs prereq update)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-28
**Status**: Final Analysis
