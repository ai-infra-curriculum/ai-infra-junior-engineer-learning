# Lecture 01: Git Fundamentals

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Version Control](#understanding-version-control)
3. [Git Architecture and Concepts](#git-architecture-and-concepts)
4. [Repository Initialization](#repository-initialization)
5. [The Three States of Git](#the-three-states-of-git)
6. [Basic Git Operations](#basic-git-operations)
7. [Viewing History](#viewing-history)
8. [Git for AI/ML Projects](#git-for-aiml-projects)
9. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

---

## Introduction

### Why Version Control is Critical for AI Infrastructure

Picture this: You're developing a machine learning training pipeline. After weeks of work, it's finally running stable experiments. Then you make "just a small optimization" to the data preprocessing. Suddenly, your model accuracy drops by 15%. Panic sets in. What changed? Which line of code caused this? Can you undo it?

Without version control, you're stuck comparing files manually, or worse, you've overwritten the working version entirely.

This is where Git saves the day—and your career.

For AI infrastructure engineers, Git isn't just about code. It's about:
- **Reproducibility**: Every experiment must be traceable to exact code versions
- **Collaboration**: Multiple engineers working on the same infrastructure
- **Safety**: Ability to revert problematic deployments instantly
- **Documentation**: Commits tell the story of why decisions were made
- **CI/CD**: Automated testing and deployment triggered by Git operations

### Learning Objectives

By the end of this lecture, you will:

- Understand Git's distributed architecture and how it differs from centralized version control
- Master Git's three-state model (working directory, staging area, repository)
- Initialize repositories and configure Git for ML projects
- Perform essential Git operations: add, commit, status, diff, log
- Write effective commit messages for infrastructure code
- Create comprehensive .gitignore files for AI/ML projects
- Understand Git's role in reproducible ML experiments
- Troubleshoot common Git issues

### The AI Infrastructure Context

AI infrastructure projects have unique version control needs:

**What to track:**
- Infrastructure as Code (Terraform, Kubernetes manifests)
- Training and deployment scripts
- Configuration files
- Data preprocessing pipelines
- Model serving code
- Monitoring and logging configurations

**What NOT to track:**
- Large model files (use Git LFS or DVC instead)
- Training datasets (use data versioning tools)
- Virtual environments
- Compiled binaries
- Temporary files and logs
- API keys and secrets

We'll address all of these throughout this lecture.

---

## Understanding Version Control

### What is Version Control?

Version control is a system that records changes to files over time so you can recall specific versions later. It answers critical questions:

- **What** changed?
- **When** did it change?
- **Who** changed it?
- **Why** was it changed?

### Centralized vs Distributed Version Control

#### Centralized VCS (SVN, Perforce)

```
        Central Server
             |
    +--------+--------+
    |        |        |
  Dev A    Dev B    Dev C
```

Characteristics:
- Single source of truth on a central server
- Developers check out files from the server
- Network required for most operations
- Server is a single point of failure

#### Distributed VCS (Git, Mercurial)

```
    Remote Repository (GitHub)
             |
    +--------+--------+
    |        |        |
  Dev A    Dev B    Dev C
  (full)   (full)   (full)
  clone    clone    clone
```

Characteristics:
- Every developer has the complete repository history
- Most operations are local and fast
- Can work offline
- No single point of failure
- More complex but more powerful

### Why Git Won

Git dominates for several reasons:

1. **Speed**: Blazingly fast local operations
2. **Branching**: Cheap and easy branching/merging
3. **Distributed**: Full repository history locally
4. **Data Integrity**: Cryptographic SHA-1 hashes prevent corruption
5. **Ecosystem**: GitHub, GitLab, Bitbucket provide collaboration platforms
6. **CI/CD Integration**: Native integration with modern DevOps tools

---

## Git Architecture and Concepts

### The Git Object Model

Git stores everything as objects in a content-addressable filesystem. There are four object types:

#### 1. Blob (Binary Large Object)
Stores file contents. Each unique file content gets one blob.

```
blob 14
Hello, Git!
```

#### 2. Tree
Represents a directory. Points to blobs and other trees.

```
tree
100644 blob a906cb  README.md
100644 blob 3b18e5  main.py
040000 tree 8a7d00  src/
```

#### 3. Commit
Snapshot of the project at a point in time.

```
commit
tree 8a7d00
parent e3a2b1
author John Doe <john@example.com> 1698765432 +0000
committer John Doe <john@example.com> 1698765432 +0000

Add model training pipeline
```

#### 4. Tag
Named reference to a specific commit.

### The SHA-1 Hash

Every Git object gets a unique 40-character SHA-1 hash:

```
a906cb2a4a904a152e80877d4088654daad0c859
```

This hash is calculated from the object's content, making Git tamper-proof. If a single byte changes, the hash changes entirely.

### Repository Structure

When you initialize a Git repository, this structure is created:

```
my-ml-project/
├── .git/                    # Git repository data (hidden)
│   ├── objects/            # All Git objects (blobs, trees, commits)
│   ├── refs/               # References (branches, tags)
│   │   ├── heads/         # Local branches
│   │   └── remotes/       # Remote branches
│   ├── HEAD                # Points to current branch
│   ├── config              # Repository configuration
│   ├── index               # Staging area
│   └── hooks/              # Git hooks (automation)
└── [your project files]
```

**Important**: Never manually edit files in `.git/` unless you know exactly what you're doing.

---

## Repository Initialization

### Starting a New Repository

There are two ways to start with Git:

#### Option 1: Create a New Repository

```bash
# Create project directory
mkdir ml-inference-api
cd ml-inference-api

# Initialize Git repository
git init

# Output:
# Initialized empty Git repository in /path/to/ml-inference-api/.git/
```

This creates the `.git` directory and turns your folder into a Git repository.

#### Option 2: Clone an Existing Repository

```bash
# Clone from GitHub
git clone https://github.com/username/ml-inference-api.git

# Clone with a different directory name
git clone https://github.com/username/ml-inference-api.git my-api

# Clone a specific branch
git clone -b develop https://github.com/username/ml-inference-api.git
```

Cloning downloads the entire repository history, not just the latest version.

### Initial Git Configuration

Before making commits, configure your identity:

```bash
# Set your name and email (global configuration)
git config --global user.name "Jane Smith"
git config --global user.email "jane.smith@company.com"

# Verify configuration
git config --list

# Set default branch name to 'main' (modern convention)
git config --global init.defaultBranch main

# Set default editor for commit messages
git config --global core.editor "vim"  # or "nano", "code --wait", etc.

# Enable colored output
git config --global color.ui auto
```

Configuration levels:
- `--system`: All users on the system
- `--global`: Current user (stored in `~/.gitconfig`)
- `--local`: Current repository only (stored in `.git/config`)

### Configuration for AI/ML Projects

Additional configurations useful for ML infrastructure:

```bash
# Handle line endings (important for cross-platform teams)
git config --global core.autocrlf input  # Linux/Mac
git config --global core.autocrlf true   # Windows

# Increase HTTP buffer for large files
git config --global http.postBuffer 524288000  # 500 MB

# Set up credential caching (avoid typing passwords repeatedly)
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'  # 1 hour

# Set up aliases for common commands
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
```

---

## The Three States of Git

Understanding Git's three-state architecture is fundamental. Files can be in one of three states:

```
Working Directory  →  Staging Area  →  Git Repository
  (modified)           (staged)         (committed)
      ↓                    ↓                  ↓
   git add          git commit         history
```

### 1. Working Directory (Modified)

Your actual project files. When you edit a file, it's in the "modified" state.

```bash
# Edit a file
echo "import torch" > model.py
```

The file `model.py` is now modified in your working directory.

### 2. Staging Area / Index (Staged)

A holding area for changes you want to include in the next commit. Think of it as preparing a package for shipping.

```bash
# Stage the file
git add model.py
```

Now `model.py` is staged and ready to be committed.

### 3. Git Repository (Committed)

Permanently stored in the Git database with a snapshot of your changes.

```bash
# Commit staged changes
git commit -m "Add initial model implementation"
```

Now the changes are committed to the repository history.

### Visual Representation

```
+-------------------+       +------------------+       +------------------+
|     WORKING       |       |     STAGING      |       |       GIT        |
|    DIRECTORY      | ----> |      AREA        | ----> |    REPOSITORY    |
|                   |       |    (INDEX)       |       |    (.git dir)    |
+-------------------+       +------------------+       +------------------+
| model.py          |       | model.py         |       | commit abc123:   |
| (modified)        |       | (staged)         |       | + model.py       |
| data_prep.py      |       |                  |       |                  |
| (untracked)       |       |                  |       |                  |
+-------------------+       +------------------+       +------------------+
        ↓                           ↓                          ↓
   git add                    git commit                  permanent
                                                          history
```

### Why Three States?

The staging area provides fine-grained control:

1. **Selective commits**: Stage only specific changes, even within the same file
2. **Logical grouping**: Combine related changes into meaningful commits
3. **Review before commit**: Double-check what you're committing
4. **Atomic commits**: Ensure each commit is a complete, logical unit

---

## Basic Git Operations

### Checking Repository Status

The most-used Git command:

```bash
git status
```

Output example:

```
On branch main
Your branch is up to date with 'origin/main'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   src/model.py

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   src/train.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        src/inference.py
```

Status tells you:
- Current branch
- Sync status with remote
- Staged changes
- Unstaged changes
- Untracked files

**Pro tip**: Run `git status` constantly. Make it a habit.

### Adding Files to Staging Area

```bash
# Stage a single file
git add src/model.py

# Stage multiple files
git add src/model.py src/train.py

# Stage all files in a directory
git add src/

# Stage all changes in the repository
git add .

# Stage all modified and deleted files (not new files)
git add -u

# Stage interactively (review each change)
git add -i

# Stage specific parts of a file (patch mode)
git add -p src/model.py
```

#### Interactive Staging Example

```bash
git add -p model.py

# Git will show each change and prompt:
Stage this hunk [y,n,q,a,d,s,e,?]?
  y - stage this hunk
  n - do not stage this hunk
  q - quit; do not stage this or remaining hunks
  a - stage this and all remaining hunks
  d - do not stage this or remaining hunks
  s - split the current hunk into smaller hunks
  e - manually edit the current hunk
  ? - print help
```

This is incredibly useful for making atomic commits from messy working directories.

### Committing Changes

```bash
# Commit with inline message
git commit -m "Add PyTorch model architecture"

# Commit with detailed message (opens editor)
git commit

# Commit with inline message and description
git commit -m "Add model architecture" -m "Implemented ResNet-50 with custom head for our classification task. Includes batch normalization and dropout layers."

# Stage and commit in one command (only tracked files)
git commit -a -m "Update training configuration"

# Amend the last commit (add forgotten changes or fix message)
git add forgotten_file.py
git commit --amend

# Amend without changing the message
git commit --amend --no-edit
```

### Writing Good Commit Messages

Commit messages are documentation for your future self and your team. Follow these guidelines:

#### The Seven Rules of Great Commit Messages

1. **Separate subject from body with a blank line**
2. **Limit the subject line to 50 characters**
3. **Capitalize the subject line**
4. **Do not end the subject line with a period**
5. **Use the imperative mood in the subject line** ("Add feature" not "Added feature")
6. **Wrap the body at 72 characters**
7. **Use the body to explain what and why vs. how**

#### Example: Bad Commit Message

```
fixed bug
```

What bug? Where? Why did it happen?

#### Example: Good Commit Message

```
Fix memory leak in batch data loading

The DataLoader was not releasing GPU memory after each batch
due to improper tensor cleanup. This caused OOM errors during
long training runs.

- Added explicit tensor deletion after gradient computation
- Implemented garbage collection trigger every 100 batches
- Reduced batch size from 64 to 32 as additional safeguard

Closes #127
```

This tells a complete story: what, why, how, and what issue it fixes.

#### Commit Message Template for ML Projects

```
[Type]: Short description (50 chars)

Detailed explanation of the change (72 chars per line)

Why this change was necessary:
- Reason 1
- Reason 2

How it affects the system:
- Impact 1
- Impact 2

Testing performed:
- Test 1
- Test 2

Related: #issue-number
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `perf`, `style`, `chore`

### Viewing Differences

```bash
# Show unstaged changes (working directory vs. staging area)
git diff

# Show staged changes (staging area vs. last commit)
git diff --staged
# or
git diff --cached

# Show changes in a specific file
git diff src/model.py

# Show changes between commits
git diff abc123 def456

# Show changes between branches
git diff main feature/new-model

# Show only file names that changed
git diff --name-only

# Show statistics about changes
git diff --stat

# Show word-level diff (useful for documentation)
git diff --word-diff
```

#### Understanding Diff Output

```diff
diff --git a/src/model.py b/src/model.py
index 3a4b5c6..7d8e9f0 100644
--- a/src/model.py
+++ b/src/model.py
@@ -15,7 +15,7 @@ class NeuralNetwork(nn.Module):
         self.fc1 = nn.Linear(784, 256)
-        self.fc2 = nn.Linear(256, 128)
+        self.fc2 = nn.Linear(256, 64)
         self.fc3 = nn.Linear(128, 10)
```

Breaking this down:
- `---` indicates the old version (file a)
- `+++` indicates the new version (file b)
- `@@ -15,7 +15,7 @@` indicates the line numbers of the change
- `-` lines were removed (red)
- `+` lines were added (green)

### Removing and Moving Files

```bash
# Remove a file from Git and filesystem
git rm src/old_model.py

# Remove a file from Git but keep in filesystem (untrack it)
git rm --cached config/secrets.yaml

# Move or rename a file
git mv old_name.py new_name.py

# This is equivalent to:
mv old_name.py new_name.py
git rm old_name.py
git add new_name.py
```

Always use `git mv` and `git rm` instead of regular shell commands so Git can track the changes properly.

---

## Viewing History

### Basic Log Commands

```bash
# Show commit history
git log

# Show concise history (one line per commit)
git log --oneline

# Show history with graph
git log --graph --oneline --all

# Show last N commits
git log -5

# Show commits with full diffs
git log -p

# Show statistics for each commit
git log --stat

# Show commits in date range
git log --since="2 weeks ago"
git log --until="2023-10-01"

# Show commits by author
git log --author="Jane Smith"

# Search commit messages
git log --grep="training"

# Show commits that modified a specific file
git log -- src/model.py

# Show commits that added or removed a specific string
git log -S "batch_size" --oneline
```

### Pretty Log Formatting

```bash
# Custom format
git log --pretty=format:"%h - %an, %ar : %s"

# Output:
# a1b2c3d - Jane Smith, 2 hours ago : Add model training script
# e4f5g6h - John Doe, 1 day ago : Fix data preprocessing bug
```

Common format placeholders:
- `%h` - Abbreviated commit hash
- `%an` - Author name
- `%ar` - Author date, relative
- `%s` - Commit subject
- `%b` - Commit body

### Useful Aliases

Add these to your `.gitconfig`:

```bash
git config --global alias.lg "log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative"

git config --global alias.last "log -1 HEAD --stat"

git config --global alias.today "log --since='midnight' --oneline"
```

Then use:
```bash
git lg      # Beautiful graph log
git last    # Show last commit with stats
git today   # Show today's commits
```

### Viewing Specific Commits

```bash
# Show details of a specific commit
git show abc123

# Show only files changed
git show --name-only abc123

# Show specific file from a commit
git show abc123:src/model.py

# Compare working directory to specific commit
git diff abc123
```

---

## Git for AI/ML Projects

### The .gitignore File

This is crucial for ML projects. You don't want to track:
- Large model files
- Datasets
- Virtual environments
- Experiment outputs
- Cached files

Create a `.gitignore` file in your repository root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environments
.env
.venv
ENV/
env/
venv/

# Jupyter Notebooks
.ipynb_checkpoints
*.ipynb_checkpoints/

# Machine Learning
*.h5
*.hdf5
*.pkl
*.pickle
*.pt
*.pth
*.onnx
*.pb
saved_models/
checkpoints/
models/
*.model

# Datasets
data/
datasets/
*.csv
*.tsv
*.dat
*.json
!config.json
*.parquet

# Experiment Tracking
mlruns/
.mlflow/
wandb/
runs/
tensorboard/
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Docker
*.tar
.dockerignore

# Credentials
.env
.env.local
secrets/
*.key
*.pem
credentials.json
service-account.json

# AWS
.aws/

# GCP
.gcloud/

# Large files (even if tracked, can cause issues)
*.zip
*.tar.gz
*.rar
```

### Negation Patterns

Sometimes you want to ignore a directory but track specific files in it:

```gitignore
# Ignore all files in config/
config/*

# But track this specific file
!config/default.yaml
```

### Global .gitignore

For OS and editor files that should never be tracked:

```bash
# Create global gitignore
cat > ~/.gitignore_global << EOF
.DS_Store
Thumbs.db
*.swp
.vscode/
.idea/
EOF

# Configure Git to use it
git config --global core.excludesfile ~/.gitignore_global
```

### Checking if a File is Ignored

```bash
# Check if a file is ignored
git check-ignore -v data/train.csv

# Output: .gitignore:45:*.csv  data/train.csv
# Shows the file in .gitignore, line number, and pattern that matches
```

### Untracking Already-Tracked Files

If you accidentally committed files before adding them to `.gitignore`:

```bash
# Remove from Git but keep in filesystem
git rm --cached models/large_model.pth

# Remove entire directory
git rm -r --cached data/

# Commit the removal
git commit -m "Stop tracking large data files"
```

### Handling Large Files with Git LFS

For model files that must be versioned:

```bash
# Install Git LFS
git lfs install

# Track large file types
git lfs track "*.pth"
git lfs track "*.h5"
git lfs track "*.onnx"

# This creates/updates .gitattributes
git add .gitattributes

# Now add and commit large files normally
git add models/resnet50.pth
git commit -m "Add pre-trained ResNet-50 model"
```

Git LFS stores large files separately and keeps only pointers in the repository.

### Repository Structure for ML Projects

```
ml-training-pipeline/
├── .git/
├── .gitignore
├── .gitattributes           # For Git LFS
├── README.md
├── requirements.txt
├── setup.py
├── .env.example            # Template, not actual secrets
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── preprocessing.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── resnet.py
│   ├── training/
│   │   ├── __init__.py
│   │   └── train.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── configs/
│   ├── default.yaml
│   └── experiment_001.yaml
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   └── test_model.py
├── scripts/
│   ├── setup_env.sh
│   └── run_training.sh
└── notebooks/              # For exploration only
    └── eda.ipynb
```

---

## Common Issues and Troubleshooting

### Issue 1: Committed Secrets by Accident

**Symptom**: You accidentally committed API keys or passwords.

**Solution**:
```bash
# If not pushed yet
git reset --soft HEAD~1   # Undo commit, keep changes
# Remove sensitive file, add to .gitignore
git add .gitignore
git commit -m "Add .gitignore for secrets"

# If already pushed (nuclear option)
# Use git-filter-branch or BFG Repo-Cleaner
# Then rotate all compromised credentials immediately
```

**Prevention**: Use `.env.example` files as templates, never commit `.env`.

### Issue 2: File Not Being Ignored

**Symptom**: File appears in `git status` despite being in `.gitignore`.

**Cause**: File was tracked before being added to `.gitignore`.

**Solution**:
```bash
# Untrack the file
git rm --cached filename
git commit -m "Stop tracking filename"
```

### Issue 3: Large Files Slowing Down Operations

**Symptom**: `git clone` or `git pull` takes forever.

**Cause**: Large files (models, datasets) committed directly.

**Solution**:
```bash
# Use Git LFS for large files
git lfs migrate import --include="*.pth,*.h5"

# Or use shallow clones for CI/CD
git clone --depth 1 <repository>
```

### Issue 4: Detached HEAD State

**Symptom**: Message says "You are in 'detached HEAD' state".

**Cause**: Checked out a specific commit instead of a branch.

**Solution**:
```bash
# To look around and leave
git checkout main

# To keep changes made in detached HEAD
git branch temp-branch
git checkout main
git merge temp-branch
```

### Issue 5: Wrong Commit Message

**Symptom**: Typo in the last commit message.

**Solution**:
```bash
# If not pushed yet
git commit --amend -m "Corrected message"

# If already pushed (avoid if others have pulled)
git commit --amend -m "Corrected message"
git push --force-with-lease
```

**Warning**: Never force push to shared branches without team coordination.

### Issue 6: Forgot to Add Files to Last Commit

**Solution**:
```bash
git add forgotten_file.py
git commit --amend --no-edit
```

### Git Troubleshooting Commands

```bash
# See what Git is actually doing
git status -vv

# Check Git configuration
git config --list --show-origin

# Verify repository integrity
git fsck

# Clean untracked files (be careful!)
git clean -n    # Dry run, shows what would be deleted
git clean -f    # Actually delete untracked files
git clean -fd   # Delete untracked files and directories

# Restore corrupted repository from remote
git fetch origin
git reset --hard origin/main
```

---

## Summary and Key Takeaways

### Core Concepts

1. **Git is distributed**: Every developer has the full repository history
2. **Three states**: Working Directory → Staging Area → Repository
3. **Commits are snapshots**: Each commit is a complete snapshot, not a diff
4. **SHA-1 hashes**: Every object is uniquely identified and tamper-proof
5. **Staging area**: Provides fine-grained control over commits

### Essential Commands Cheat Sheet

```bash
# Repository setup
git init                    # Initialize repository
git clone <url>            # Clone existing repository

# Configuration
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Basic workflow
git status                 # Check repository status
git add <file>            # Stage changes
git commit -m "message"   # Commit staged changes
git diff                  # View unstaged changes
git diff --staged         # View staged changes

# History
git log                   # View commit history
git log --oneline         # Concise history
git show <commit>         # Show commit details

# File operations
git rm <file>             # Remove file
git mv <old> <new>        # Move/rename file

# Undoing
git restore <file>        # Discard working directory changes
git restore --staged <file>  # Unstage changes
git reset HEAD~1          # Undo last commit (keep changes)
git commit --amend        # Modify last commit
```

### Best Practices for AI Infrastructure

1. **Commit frequently**: Small, logical commits are easier to review and revert
2. **Write descriptive messages**: Explain why, not just what
3. **Use .gitignore properly**: Never commit large files, datasets, or secrets
4. **Stage selectively**: Use `git add -p` for atomic commits
5. **Review before committing**: Always run `git diff --staged`
6. **Configure Git LFS**: For model files that must be versioned
7. **Never commit secrets**: Use environment variables and `.env` files
8. **Keep commits atomic**: One logical change per commit
9. **Test before committing**: Run tests before committing code
10. **Use branches**: Never commit directly to main (covered in next lecture)

### AI/ML-Specific Considerations

- **Reproducibility**: Commit code and configs together
- **Model versioning**: Use Git LFS or external model registries
- **Data versioning**: Use DVC, not Git
- **Experiment tracking**: Commit experiment configs, not outputs
- **Large files**: Always use .gitignore or Git LFS
- **Credentials**: Use secret management tools, not Git

### What's Next

In the next lecture, we'll cover:
- Branching strategies for ML development
- Merging and conflict resolution
- Git workflows for teams
- Feature branches and release management

### Further Reading

- Official Git documentation: https://git-scm.com/doc
- Pro Git book (free): https://git-scm.com/book/en/v2
- Git LFS documentation: https://git-lfs.github.com/
- DVC for data versioning: https://dvc.org/

---

**Practice Exercises**: Complete Exercise 01 and 02 to reinforce these concepts through hands-on practice with real ML project scenarios.
