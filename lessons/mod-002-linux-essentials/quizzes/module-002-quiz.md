# Module 002: Linux Essentials - Comprehensive Quiz

## Instructions

This quiz covers all topics from Module 002: Linux Essentials. It includes 30 questions covering:
- Linux fundamentals and navigation
- File systems and permissions
- Process management
- Shell scripting
- Package management
- Log analysis
- Troubleshooting

**Scoring:**
- Each question is worth 1 point
- Total: 30 points
- Passing score: 24/30 (80%)

**Time Estimate:** 45-60 minutes

Answer all questions, then check your answers at the end.

---

## Section 1: Linux Fundamentals and Navigation (Questions 1-6)

### Question 1: File System Hierarchy
What directory in Linux typically contains user home directories?

A) /usr
B) /home
C) /var
D) /etc

**Answer:** B

**Explanation:** /home contains user home directories (e.g., /home/alice, /home/bob). /usr contains user programs and data, /var contains variable data like logs, and /etc contains system configuration files.

---

### Question 2: Absolute vs Relative Paths
Which of the following is an absolute path?

A) ../data/train.csv
B) ./models/model.h5
C) /var/ml/datasets/train
D) models/checkpoint

**Answer:** C

**Explanation:** Absolute paths start from the root directory (/). Relative paths start from the current directory and may use . (current) or .. (parent). Option C starts with / making it absolute.

---

### Question 3: File Types
In the output of `ls -l`, what does the first character 'd' indicate?

A) A deleted file
B) A directory
C) A disk file
D) A device file

**Answer:** B

**Explanation:** In `ls -l` output, the first character indicates file type:
- = regular file, d = directory, l = symbolic link, b = block device, c = character device, p = pipe, s = socket.

---

### Question 4: Hidden Files
Which command will show hidden files (those starting with .)?

A) ls
B) ls -h
C) ls -a
D) ls --hidden

**Answer:** C

**Explanation:** `ls -a` shows all files including hidden ones (starting with .). `ls -h` shows human-readable sizes, not hidden files.

---

### Question 5: Creating Nested Directories
Which command creates nested directories in a single command?

A) mkdir -r /path/to/nested/dir
B) mkdir -p /path/to/nested/dir
C) mkdir --recursive /path/to/nested/dir
D) mkdir /path /path/to /path/to/nested /path/to/nested/dir

**Answer:** B

**Explanation:** `mkdir -p` (or --parents) creates parent directories as needed. Option D would work but is inefficient. There is no -r flag for mkdir.

---

### Question 6: Finding Files
You need to find all Python files (.py) in your project directory and subdirectories. Which command is best?

A) ls *.py
B) locate *.py
C) find . -name "*.py"
D) grep -r "*.py"

**Answer:** C

**Explanation:** `find . -name "*.py"` recursively searches from current directory (.) for files matching the pattern. `ls *.py` only checks current directory, `locate` searches a database (may be outdated), and `grep` searches file contents, not names.

---

## Section 2: File Permissions (Questions 7-12)

### Question 7: Permission Numeric Notation
What do the permissions 755 mean in numeric notation?

A) rwxr-xr-x
B) rwxrwxrwx
C) rw-r--r--
D) r-xr-xr-x

**Answer:** A

**Explanation:** 755 = rwxr-xr-x. First digit (7=rwx) for owner, second digit (5=r-x) for group, third digit (5=r-x) for others. 7=4+2+1 (read+write+execute), 5=4+1 (read+execute).

---

### Question 8: chmod Command
Which command makes a script executable by everyone?

A) chmod 644 script.sh
B) chmod +x script.sh
C) chmod 755 script.sh
D) Both B and C

**Answer:** D

**Explanation:** Both `chmod +x script.sh` (symbolic) and `chmod 755 script.sh` (numeric) make the file executable. `chmod +x` adds execute permission for all, and 755 = rwxr-xr-x (owner can write, everyone can read and execute).

---

### Question 9: File Ownership
You need to change the owner of a file to 'mluser' and group to 'mlteam'. Which command is correct?

A) chmod mluser:mlteam file.txt
B) chown mluser:mlteam file.txt
C) chgrp mluser:mlteam file.txt
D) chown mlteam:mluser file.txt

**Answer:** B

**Explanation:** `chown user:group file` changes both owner and group. The syntax is user:group, so mluser:mlteam is correct. `chmod` changes permissions, not ownership. `chgrp` only changes group.

---

### Question 10: Directory Permissions
Why do directories need execute (x) permission?

A) To run scripts inside them
B) To access their contents
C) To delete the directory
D) To create files in them

**Answer:** B

**Explanation:** Execute permission on a directory allows you to access its contents (cd into it, list files, access files). Without x permission, you cannot enter the directory even if you have read permission.

---

### Question 11: umask
If umask is set to 0022, what are the default permissions for a newly created file?

A) 777
B) 755
C) 644
D) 600

**Answer:** C

**Explanation:** Files default to 666, directories to 777. umask 0022 subtracts: 666 - 022 = 644 (rw-r--r--) for files. For directories: 777 - 022 = 755 (rwxr-xr-x).

---

### Question 12: Secure File Creation
You need to create a file containing API keys that only you can read. Which command ensures proper permissions from creation?

A) touch api_keys.txt && chmod 600 api_keys.txt
B) umask 0077 && touch api_keys.txt
C) touch api_keys.txt && chown $(whoami) api_keys.txt
D) Both A and B

**Answer:** D

**Explanation:** Both approaches work. Option A creates file then sets permissions to 600 (rw-------). Option B sets restrictive umask first, so file is created with 600 permissions. Option C only changes ownership, not permissions.

---

## Section 3: Process Management (Questions 13-18)

### Question 13: Process States
In the output of `ps aux`, what does the STAT value 'D' indicate?

A) Dead/zombie process
B) Uninterruptible sleep (usually I/O)
C) Running on CPU
D) Stopped/suspended

**Answer:** B

**Explanation:** D = uninterruptible sleep, usually waiting for I/O. R = running, S = sleeping (interruptible), T = stopped, Z = zombie. Processes in D state cannot be killed until the I/O completes.

---

### Question 14: Killing Processes
Your training process (PID 5432) is not responding to Ctrl+C. Which sequence should you try?

A) kill -9 5432 immediately
B) kill -15 5432, wait, then kill -9 5432 if needed
C) killall python
D) reboot

**Answer:** B

**Explanation:** Always try graceful termination first (kill -15 or SIGTERM) which allows the process to clean up. If it doesn't respond after waiting (e.g., 10 seconds), then use kill -9 (SIGKILL) to force kill. SIGKILL should be last resort.

---

### Question 15: Background Processes
Which command runs a training script in the background and protects it from hangup signals?

A) python train.py &
B) nohup python train.py &
C) python train.py > /dev/null
D) bg python train.py

**Answer:** B

**Explanation:** `nohup command &` runs in background (&) and is immune to hangup signals (nohup), so it continues even if you log out. Just & runs in background but will terminate on logout. `bg` resumes a suspended job, doesn't start new ones.

---

### Question 16: Process Monitoring
Which command shows real-time CPU and memory usage sorted by CPU?

A) ps aux
B) top
C) htop
D) Both B and C

**Answer:** D

**Explanation:** Both `top` and `htop` show real-time resource usage. Both default to sorting by CPU. `htop` has a more user-friendly interface with color coding. `ps aux` is a snapshot, not real-time.

---

### Question 17: GPU Process Management
How do you find which process is using GPU 0?

A) ps aux | grep gpu
B) nvidia-smi
C) lspci | grep nvidia
D) top -gpu

**Answer:** B

**Explanation:** `nvidia-smi` shows GPU utilization and processes using each GPU. `lspci | grep nvidia` shows GPU hardware but not usage. There's no `-gpu` flag for top. `ps aux | grep gpu` wouldn't show GPU usage.

---

### Question 18: Persistent Sessions
You need to start a training job that will continue after you disconnect from SSH. Which tool is best?

A) screen
B) tmux
C) nohup
D) All of the above

**Answer:** D

**Explanation:** All three work. `screen` and `tmux` provide persistent terminal sessions you can reattach to. `nohup` makes a process ignore hangup signals. tmux is more modern than screen. Choice depends on whether you need to monitor (screen/tmux) or just run (nohup).

---

## Section 4: Shell Scripting (Questions 19-22)

### Question 19: Bash Shebang
What is the purpose of `#!/bin/bash` at the start of a script?

A) It's a comment
B) It specifies which interpreter to use
C) It makes the script executable
D) It sets the working directory

**Answer:** B

**Explanation:** The shebang (#!) tells the system which interpreter to use to execute the script. #!/bin/bash uses bash, #!/usr/bin/env python3 uses Python. It's processed by the kernel, not a comment. You still need chmod +x to make it executable.

---

### Question 20: Exit on Error
Which command should be near the top of scripts to exit immediately if any command fails?

A) set -e
B) exit 1
C) trap ERR
D) set -x

**Answer:** A

**Explanation:** `set -e` (or `set -o errexit`) causes script to exit immediately if any command returns non-zero. `set -u` exits on undefined variables, `set -o pipefail` fails on pipe errors. `set -x` enables debug mode (prints commands). `exit 1` exits with error code 1.

---

### Question 21: Command Substitution
Which syntax correctly captures command output into a variable?

A) VAR=`ls`
B) VAR=$(ls)
C) VAR=${ls}
D) Both A and B

**Answer:** D

**Explanation:** Both backticks `command` and $(...) perform command substitution. $(command) is preferred (POSIX standard, easier to nest). ${var} is variable expansion, not command substitution.

---

### Question 22: Checking Command Success
How do you check if the previous command succeeded in a bash script?

A) if [ $? -eq 0 ]; then
B) if [ $SUCCESS ]; then
C) if [ $RESULT == "ok" ]; then
D) if [ last_command ]; then

**Answer:** A

**Explanation:** `$?` contains the exit code of the last command. 0 = success, non-zero = failure. So `if [ $? -eq 0 ]` checks for success. Can also use `if command; then` directly without checking $?.

---

## Section 5: Package Management (Questions 23-26)

### Question 23: System Packages
Which command updates the package index on Ubuntu/Debian?

A) sudo apt upgrade
B) sudo apt update
C) sudo apt install updates
D) sudo apt refresh

**Answer:** B

**Explanation:** `sudo apt update` updates the package index (list of available packages). `sudo apt upgrade` installs updates for installed packages. Always run `apt update` before `apt upgrade`.

---

### Question 24: Python Virtual Environments
Why should you use Python virtual environments for ML projects?

A) They provide better performance
B) They isolate project dependencies
C) They require less disk space
D) They enable GPU support

**Answer:** B

**Explanation:** Virtual environments isolate dependencies, preventing conflicts between projects. Different projects can use different versions of packages. They don't improve performance or enable GPU support. They use more disk space (duplicate packages).

---

### Question 25: pip vs conda
Which statement about pip and conda is TRUE?

A) pip can only install Python packages
B) conda can only install Python packages
C) pip is faster than conda
D) conda cannot use virtual environments

**Answer:** A

**Explanation:** pip installs Python packages from PyPI. Conda installs both Python packages and system libraries (CUDA, etc.) from conda channels. Conda also manages environments. Speed varies by situation. Both support isolation.

---

### Question 26: CUDA Installation
After installing CUDA, which environment variable must be set for applications to find CUDA libraries?

A) CUDA_PATH
B) LD_LIBRARY_PATH
C) LIBRARY_PATH
D) CUDA_HOME

**Answer:** B

**Explanation:** `LD_LIBRARY_PATH` tells the dynamic linker where to find shared libraries. Must include CUDA lib directory (e.g., /usr/local/cuda/lib64). `PATH` should include bin directory for executables. CUDA_HOME and CUDA_PATH are optional helper variables.

---

## Section 6: Log Analysis (Questions 27-29)

### Question 27: Viewing Log Files
Which command follows a log file in real-time, showing new entries as they are written?

A) cat -f /var/log/syslog
B) tail /var/log/syslog
C) tail -f /var/log/syslog
D) head -f /var/log/syslog

**Answer:** C

**Explanation:** `tail -f` follows a file, continuously displaying new lines. Similar to `tail --follow`. `cat` and `head` don't have -f option. Plain `tail` shows last 10 lines but doesn't follow.

---

### Question 28: Filtering Logs
You need to find all ERROR messages in training logs from the last hour. Which command works best?

A) cat training.log | grep ERROR
B) grep ERROR training.log
C) journalctl --since "1 hour ago" | grep ERROR
D) Both B and C

**Answer:** D

**Explanation:** For application logs, `grep ERROR training.log` is direct. For system logs managed by systemd, `journalctl --since "1 hour ago" | grep ERROR` works. Option A works but is inefficient (useless use of cat). Choice depends on log location.

---

### Question 29: Extracting Metrics
Which tool is best for extracting structured data from logs (like extracting loss values from training logs)?

A) grep
B) awk
C) sed
D) cat

**Answer:** B

**Explanation:** `awk` excels at processing structured text and extracting fields. Can easily extract values matching patterns, perform calculations, format output. `grep` finds patterns but doesn't extract values well. `sed` is for text transformation. `cat` just displays.

---

## Section 7: Troubleshooting (Question 30)

### Question 30: Systematic Troubleshooting
Your ML training job fails with "No space left on device". What should be your FIRST step?

A) Delete all checkpoint files immediately
B) Check disk usage with df -h
C) Reboot the system
D) Increase swap space

**Answer:** B

**Explanation:** First step is always diagnosis: verify the problem and understand the situation with `df -h`. Only after confirming disk is full should you decide what to clean up. Deleting files blindly could lose important data. Rebooting doesn't free disk space. Swap helps memory, not disk.

---

## Answer Key Summary

1. B
2. C
3. B
4. C
5. B
6. C
7. A
8. D
9. B
10. B
11. C
12. D
13. B
14. B
15. B
16. D
17. B
18. D
19. B
20. A
21. D
22. A
23. B
24. B
25. A
26. B
27. C
28. D
29. B
30. B

---

## Scoring Guide

**27-30 correct (90-100%):** Excellent! You have mastered Linux essentials for ML infrastructure.

**24-26 correct (80-89%):** Good! You pass, but review areas where you made mistakes.

**20-23 correct (67-79%):** Fair. Review the module materials and retake the quiz.

**Below 20 (< 67%):** Needs improvement. Carefully review all lectures and exercises before retaking.

---

## Topic Review Recommendations

Based on common mistakes, review these areas:

**If you missed questions 1-6:** Review Lecture 01 (Linux Fundamentals) and Exercise 01 (Navigation)

**If you missed questions 7-12:** Review Lecture 02 (File Permissions) and Exercise 02 (Permissions)

**If you missed questions 13-18:** Review Lecture 03 (Process Management) and Exercise 03 (Processes)

**If you missed questions 19-22:** Review Lecture 04 (Shell Scripting) and Exercise 04 (Scripting)

**If you missed questions 23-26:** Review Lecture 05 (Package Management) and Exercise 05 (Package Management)

**If you missed questions 27-29:** Review Exercise 06 (Log Analysis)

**If you missed question 30:** Review Exercise 07 (Troubleshooting)

---

## Additional Practice

To reinforce your learning:

1. **Hands-on Practice:** Complete all exercises if you haven't already
2. **Real-world Application:** Set up a test ML environment and practice these commands
3. **Create Cheat Sheets:** Summarize key commands for quick reference
4. **Teach Others:** Explaining concepts helps solidify understanding
5. **Build Projects:** Apply skills to actual ML infrastructure projects

---

## Next Steps

Once you've achieved at least 80% on this quiz:

1. Move to **Module 003: Containerization with Docker**
2. Keep this module's materials as reference
3. Practice these skills regularly in your projects
4. Build automation scripts using what you've learned

---

**Congratulations on completing the Module 002 Quiz!**

If you scored 80% or higher, you're ready to advance. If not, review the suggested materials and retake the quiz. Remember, mastery of Linux fundamentals is crucial for success as an AI Infrastructure Engineer.
