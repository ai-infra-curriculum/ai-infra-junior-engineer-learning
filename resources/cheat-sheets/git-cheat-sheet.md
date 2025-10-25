# Git Cheat Sheet

Quick reference guide for essential Git commands and workflows.

---

## Table of Contents

- [Setup and Configuration](#setup-and-configuration)
- [Basic Commands](#basic-commands)
- [Branching](#branching)
- [Remote Repositories](#remote-repositories)
- [Undoing Changes](#undoing-changes)
- [Viewing History](#viewing-history)
- [Advanced Operations](#advanced-operations)
- [Git Workflows](#git-workflows)
- [Troubleshooting](#troubleshooting)

---

## Setup and Configuration

### Initial Setup
```bash
# Set username
git config --global user.name "Your Name"

# Set email
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "vim"
git config --global core.editor "code --wait"  # VS Code

# Set default branch name
git config --global init.defaultBranch main

# Enable color output
git config --global color.ui auto

# View configuration
git config --list
git config --global --list
git config user.name
```

### SSH Setup
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Add to GitHub/GitLab settings

# Test connection
ssh -T git@github.com
```

### Aliases
```bash
# Create shortcuts
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.lg 'log --oneline --graph --decorate --all'
```

---

## Basic Commands

### Repository Initialization
```bash
# Initialize new repository
git init

# Clone existing repository
git clone <repository-url>
git clone <repository-url> <directory-name>

# Clone specific branch
git clone -b <branch-name> <repository-url>
```

### Status and Information
```bash
# Check status
git status
git status -s  # short format

# Show changes
git diff  # unstaged changes
git diff --staged  # staged changes
git diff HEAD  # all changes

# Show commit log
git log
git log --oneline
git log --graph --oneline --all
git log --author="John"
git log --since="2 weeks ago"
git log --until="yesterday"
git log -p  # with patches
git log -3  # last 3 commits
```

### Staging and Committing
```bash
# Stage files
git add <file>
git add .  # all files
git add *.py  # all Python files
git add -A  # all changes including deletions

# Unstage files
git reset <file>
git restore --staged <file>  # new syntax

# Commit changes
git commit -m "Commit message"
git commit -am "Message"  # add and commit tracked files
git commit --amend  # modify last commit
git commit --amend --no-edit  # keep commit message

# Remove files
git rm <file>  # remove from repo and filesystem
git rm --cached <file>  # remove from repo only

# Move/rename files
git mv <old-name> <new-name>
```

---

## Branching

### Creating and Switching Branches
```bash
# List branches
git branch  # local branches
git branch -r  # remote branches
git branch -a  # all branches

# Create branch
git branch <branch-name>

# Switch to branch
git checkout <branch-name>
git switch <branch-name>  # new syntax

# Create and switch in one command
git checkout -b <branch-name>
git switch -c <branch-name>  # new syntax

# Create branch from specific commit
git branch <branch-name> <commit-hash>

# Delete branch
git branch -d <branch-name>  # safe delete
git branch -D <branch-name>  # force delete

# Rename branch
git branch -m <old-name> <new-name>
git branch -m <new-name>  # rename current branch
```

### Merging
```bash
# Merge branch into current branch
git merge <branch-name>

# Merge with commit message
git merge <branch-name> -m "Merge message"

# Abort merge
git merge --abort

# Merge strategies
git merge --no-ff <branch-name>  # always create merge commit
git merge --squash <branch-name>  # squash commits
```

### Rebasing
```bash
# Rebase current branch onto another
git rebase <branch-name>

# Interactive rebase
git rebase -i HEAD~3  # last 3 commits
git rebase -i <commit-hash>

# Continue after resolving conflicts
git rebase --continue

# Skip current commit
git rebase --skip

# Abort rebase
git rebase --abort
```

---

## Remote Repositories

### Managing Remotes
```bash
# List remotes
git remote
git remote -v  # with URLs

# Add remote
git remote add origin <repository-url>
git remote add <name> <url>

# Remove remote
git remote remove <name>

# Rename remote
git remote rename <old-name> <new-name>

# Change remote URL
git remote set-url origin <new-url>

# Show remote info
git remote show origin
```

### Fetching and Pulling
```bash
# Fetch from remote (doesn't merge)
git fetch
git fetch origin
git fetch --all  # all remotes

# Pull (fetch + merge)
git pull
git pull origin main

# Pull with rebase
git pull --rebase
```

### Pushing
```bash
# Push to remote
git push
git push origin main

# Push and set upstream
git push -u origin main
git push --set-upstream origin feature-branch

# Push all branches
git push --all

# Push tags
git push --tags

# Force push (dangerous!)
git push --force
git push --force-with-lease  # safer force push

# Delete remote branch
git push origin --delete <branch-name>
```

### Tracking Branches
```bash
# Create tracking branch
git checkout -b <branch> origin/<branch>
git checkout --track origin/<branch>

# Set upstream for existing branch
git branch --set-upstream-to=origin/main main

# View tracking branches
git branch -vv
```

---

## Undoing Changes

### Discard Changes
```bash
# Discard unstaged changes in file
git checkout -- <file>
git restore <file>  # new syntax

# Discard all unstaged changes
git checkout -- .
git restore .  # new syntax

# Unstage file
git reset HEAD <file>
git restore --staged <file>  # new syntax
```

### Reset
```bash
# Soft reset (keep changes staged)
git reset --soft HEAD~1

# Mixed reset (keep changes unstaged) - default
git reset HEAD~1
git reset --mixed HEAD~1

# Hard reset (discard all changes)
git reset --hard HEAD~1
git reset --hard <commit-hash>

# Reset to remote state
git reset --hard origin/main
```

### Revert
```bash
# Revert commit (creates new commit)
git revert <commit-hash>

# Revert without committing
git revert -n <commit-hash>

# Revert merge commit
git revert -m 1 <merge-commit-hash>
```

### Clean
```bash
# Remove untracked files
git clean -n  # dry run
git clean -f  # force remove files
git clean -fd  # remove files and directories
git clean -fX  # remove ignored files
git clean -fx  # remove all untracked files
```

---

## Viewing History

### Log Commands
```bash
# Basic log
git log
git log --oneline

# Graphical log
git log --graph --oneline --all
git log --graph --pretty=format:'%h %d %s (%cr) <%an>'

# Filter by author
git log --author="John"

# Filter by date
git log --since="2 weeks ago"
git log --after="2023-01-01" --before="2023-12-31"

# Filter by file
git log <file>
git log --follow <file>  # follow renames

# Search commits
git log --grep="bug fix"
git log -S"function_name"  # search code

# Show stats
git log --stat
git log --shortstat
```

### Show Command
```bash
# Show commit details
git show <commit-hash>
git show HEAD
git show HEAD~2

# Show specific file from commit
git show <commit-hash>:<file>

# Show file at specific commit
git show HEAD~3:path/to/file
```

### Diff Commands
```bash
# Show unstaged changes
git diff

# Show staged changes
git diff --staged
git diff --cached

# Compare branches
git diff main..feature
git diff main...feature  # since common ancestor

# Compare commits
git diff <commit1> <commit2>
git diff HEAD~2 HEAD

# Diff specific file
git diff <file>
git diff main..feature <file>
```

### Blame
```bash
# Show who changed each line
git blame <file>

# Show with line numbers
git blame -L 10,20 <file>

# Show with commit info
git blame -l <file>
```

---

## Advanced Operations

### Stashing
```bash
# Stash changes
git stash
git stash save "Work in progress"

# List stashes
git stash list

# Apply stash
git stash apply  # keep stash
git stash pop  # apply and delete stash

# Apply specific stash
git stash apply stash@{2}

# Drop stash
git stash drop stash@{0}

# Clear all stashes
git stash clear

# Create branch from stash
git stash branch <branch-name>
```

### Cherry-picking
```bash
# Apply specific commit to current branch
git cherry-pick <commit-hash>

# Cherry-pick without committing
git cherry-pick -n <commit-hash>

# Cherry-pick range
git cherry-pick <commit1>..<commit2>
```

### Tags
```bash
# List tags
git tag
git tag -l "v1.*"

# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Version 1.0.0"

# Tag specific commit
git tag v1.0.0 <commit-hash>

# Push tags
git push origin v1.0.0
git push origin --tags  # all tags

# Delete tag
git tag -d v1.0.0  # local
git push origin --delete v1.0.0  # remote

# Checkout tag
git checkout v1.0.0
```

### Submodules
```bash
# Add submodule
git submodule add <repository-url> <path>

# Initialize submodules
git submodule init

# Update submodules
git submodule update
git submodule update --remote

# Clone with submodules
git clone --recursive <repository-url>

# Update all submodules
git submodule foreach git pull origin main
```

---

## Git Workflows

### Feature Branch Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push to remote
git push -u origin feature/new-feature

# 4. Create pull request (on GitHub/GitLab)

# 5. After PR approved, merge and delete branch
git checkout main
git pull origin main
git branch -d feature/new-feature
```

### Gitflow Workflow
```bash
# Main branches: main, develop

# Start feature
git checkout develop
git checkout -b feature/new-feature

# Finish feature
git checkout develop
git merge --no-ff feature/new-feature
git branch -d feature/new-feature
git push origin develop

# Start release
git checkout -b release/1.0.0 develop
# Make release commits
git checkout main
git merge --no-ff release/1.0.0
git tag -a v1.0.0
git checkout develop
git merge --no-ff release/1.0.0
git branch -d release/1.0.0

# Hotfix
git checkout -b hotfix/1.0.1 main
# Fix bug
git checkout main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1
git checkout develop
git merge --no-ff hotfix/1.0.1
git branch -d hotfix/1.0.1
```

### Rebase Workflow
```bash
# Keep feature branch up-to-date with main
git checkout feature/my-feature
git fetch origin
git rebase origin/main

# Resolve conflicts if any
# ... edit files ...
git add <resolved-files>
git rebase --continue

# Force push (rewriting history)
git push --force-with-lease origin feature/my-feature
```

---

## Troubleshooting

### Common Issues

#### Merge Conflicts
```bash
# 1. See conflicted files
git status

# 2. Edit files to resolve conflicts
# Look for conflict markers: <<<<<<<, =======, >>>>>>>

# 3. Mark as resolved
git add <resolved-files>

# 4. Complete merge
git commit  # for merge
git rebase --continue  # for rebase
```

#### Undo Last Commit
```bash
# Keep changes staged
git reset --soft HEAD~1

# Keep changes unstaged
git reset HEAD~1

# Discard changes
git reset --hard HEAD~1
```

#### Recover Deleted Branch
```bash
# Find commit hash
git reflog

# Recreate branch
git branch <branch-name> <commit-hash>
```

#### Remove Committed File
```bash
# Remove from history (dangerous!)
git filter-branch --tree-filter 'rm -f <file>' HEAD

# Better: use git filter-repo (install separately)
git filter-repo --path <file> --invert-paths
```

#### Fix Commit Message
```bash
# Last commit
git commit --amend -m "New message"

# Older commit (interactive rebase)
git rebase -i HEAD~3
# Change 'pick' to 'reword' for commits to edit
```

#### Sync Fork with Upstream
```bash
# Add upstream remote
git remote add upstream <original-repo-url>

# Fetch upstream
git fetch upstream

# Merge upstream into local
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## Best Practices

### Commit Messages
```bash
# Good commit message format:
# <type>(<scope>): <subject>
#
# <body>
#
# <footer>

# Examples:
git commit -m "feat(api): add user authentication endpoint"
git commit -m "fix(database): resolve connection timeout issue"
git commit -m "docs(readme): update installation instructions"

# Types: feat, fix, docs, style, refactor, test, chore
```

### .gitignore
```bash
# Python
__pycache__/
*.py[cod]
*.so
.env
venv/
.venv/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Project specific
/data/
/logs/
*.log
```

### Tips
1. **Commit often**: Small, focused commits
2. **Pull before push**: Avoid conflicts
3. **Use branches**: Keep main stable
4. **Write good messages**: Explain why, not what
5. **Review before commit**: `git diff --staged`
6. **Don't commit secrets**: Use .gitignore
7. **Use .gitignore early**: Before first commit

---

## Quick Reference

### Essential Commands
```bash
# Clone
git clone <url>

# Status
git status

# Add
git add <file>
git add .

# Commit
git commit -m "message"

# Push
git push origin main

# Pull
git pull origin main

# Branch
git branch <name>
git checkout <name>
git checkout -b <name>

# Merge
git merge <branch>

# Log
git log --oneline
```

### Useful Aliases
```bash
# Add to ~/.gitconfig or use git config --global alias.* commands

[alias]
    st = status -s
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    lg = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
    undo = reset --soft HEAD~1
    amend = commit --amend --no-edit
```

---

## Additional Resources

- [Official Git Documentation](https://git-scm.com/doc)
- [Pro Git Book](https://git-scm.com/book/en/v2) (free online)
- [GitHub Git Cheat Sheet](https://training.github.com/downloads/github-git-cheat-sheet/)
- [Learn Git Branching](https://learngitbranching.js.org/) (interactive tutorial)
- [Oh Shit, Git!?!](https://ohshitgit.com/) (fixing mistakes)

---

**Master these commands for effective version control!**
