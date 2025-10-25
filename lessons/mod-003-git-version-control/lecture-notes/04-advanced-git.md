# Lecture 04: Advanced Git Techniques

## Table of Contents
1. [Introduction](#introduction)
2. [Interactive Rebasing](#interactive-rebasing)
3. [Cherry-Picking Commits](#cherry-picking-commits)
4. [Stashing Changes](#stashing-changes)
5. [Git Hooks](#git-hooks)
6. [Submodules and Subtrees](#submodules-and-subtrees)
7. [Tags and Releases](#tags-and-releases)
8. [Advanced History Manipulation](#advanced-history-manipulation)
9. [Git for Machine Learning](#git-for-machine-learning)
10. [Performance and Optimization](#performance-and-optimization)
11. [Recovery and Disaster Management](#recovery-and-disaster-management)
12. [Summary and Key Takeaways](#summary-and-key-takeaways)

---

## Introduction

### Why Master Advanced Git?

You've learned Git basics, branching, and collaboration. You can handle day-to-day work. So why go further?

Advanced Git techniques transform you from competent to exceptional:
- **Clean up messy history** before others see it
- **Automate repetitive tasks** with hooks
- **Recover from disasters** that would panic others
- **Optimize workflows** for ML-specific challenges
- **Manage complex projects** with submodules
- **Handle emergencies** with surgical precision

In AI infrastructure, these skills separate junior from senior engineers.

### Learning Objectives

By the end of this lecture, you will:

- Use interactive rebase to clean up commit history
- Cherry-pick specific commits between branches
- Stash work-in-progress to switch contexts quickly
- Create Git hooks to automate testing, linting, and deployment
- Manage large ML projects with submodules
- Tag releases properly for model versioning
- Use advanced commands: reflog, bisect, filter-branch
- Recover from seemingly catastrophic mistakes
- Apply Git best practices specific to ML workflows
- Optimize Git performance for large repositories

### The AI Infrastructure Context

Advanced Git enables:

**Experiment management:**
- Clean up experimental commits before merging
- Cherry-pick successful experiments to production
- Tag model versions for reproducibility

**Automation:**
- Pre-commit hooks: Lint code, check for secrets
- Pre-push hooks: Run tests before pushing
- Post-merge hooks: Trigger model retraining

**Project organization:**
- Submodules for shared libraries (data utils, model architectures)
- Subtrees for vendored dependencies
- Tags for model releases and deployments

**Disaster recovery:**
- Recover deleted branches
- Fix accidentally pushed secrets
- Undo problematic merges

---

## Interactive Rebasing

### What is Interactive Rebase?

Interactive rebase (`git rebase -i`) lets you edit commit history:
- Reorder commits
- Squash multiple commits into one
- Edit commit messages
- Split commits
- Delete commits

**Golden Rule**: Only rebase commits that haven't been pushed to shared branches.

### When to Use Interactive Rebase

**Use cases:**
- Clean up messy local commits before creating PR
- Fix typos in commit messages
- Reorder commits logically
- Combine WIP commits into meaningful commits

**Example scenario**:
```
Your local commits:
* 789 Fix typo
* 456 WIP: still working
* 123 WIP: add feature
```

You want clean history:
```
* abc Implement user authentication feature
```

### Interactive Rebase: Step by Step

#### Step 1: Start Interactive Rebase

```bash
# Rebase last 3 commits
git rebase -i HEAD~3

# Rebase from specific commit (not including that commit)
git rebase -i abc123

# Rebase from branch point
git rebase -i main
```

#### Step 2: Choose Actions

Git opens an editor showing commits:

```
pick 123 WIP: add feature
pick 456 WIP: still working
pick 789 Fix typo

# Rebase abc..789 onto abc (3 commands)
#
# Commands:
# p, pick = use commit
# r, reword = use commit, but edit the commit message
# e, edit = use commit, but stop for amending
# s, squash = use commit, but meld into previous commit
# f, fixup = like "squash", but discard this commit's log message
# x, exec = run command (the rest of the line) using shell
# d, drop = remove commit
```

#### Step 3: Modify the Plan

**To squash all commits into one:**
```
pick 123 WIP: add feature
squash 456 WIP: still working
squash 789 Fix typo
```

Save and close the editor.

#### Step 4: Edit Commit Message

Git opens another editor for the combined commit message:

```
# This is a combination of 3 commits.
# The first commit's message is:
WIP: add feature

# This is the 2nd commit message:
WIP: still working

# This is the 3rd commit message:
Fix typo
```

Replace with:
```
Implement user authentication feature

Added login/logout functionality with JWT tokens.
Includes input validation and error handling.
```

Save and close.

#### Step 5: Result

```bash
git log --oneline
# abc Implement user authentication feature
```

Three messy commits are now one clean commit.

### Interactive Rebase Actions

**Pick** (default): Use commit as-is
```
pick 123 Add feature
```

**Reword**: Change commit message
```
reword 123 Add feature
# Git will open editor to change message
```

**Edit**: Stop at commit to amend
```
edit 123 Add feature
# Git pauses; you can make changes
git add modified_file.py
git commit --amend
git rebase --continue
```

**Squash**: Combine with previous commit, keep both messages
```
pick 123 Add feature
squash 456 Add tests
# Git combines commits, lets you edit combined message
```

**Fixup**: Combine with previous commit, discard this message
```
pick 123 Add feature
fixup 456 Fix typo
# Git combines commits, keeps only first message
```

**Drop**: Remove commit
```
drop 123 Experimental change
```

**Exec**: Run shell command
```
pick 123 Add feature
exec pytest tests/
pick 456 Add another feature
exec pytest tests/
# Runs tests after each commit; stops if tests fail
```

### Reordering Commits

Simply reorder lines:

```
pick 789 Fix documentation
pick 123 Add feature
pick 456 Add tests
```

Commits will be applied in this order.

### Splitting a Commit

**Scenario**: One commit did too much; you want to split it.

```bash
git rebase -i HEAD~1
# Mark the commit as 'edit'

# Git pauses at the commit
git reset HEAD^   # Unstage everything

# Now commit changes separately
git add file1.py
git commit -m "Add feature A"

git add file2.py
git commit -m "Add feature B"

# Continue rebase
git rebase --continue
```

### Aborting a Rebase

If things go wrong:
```bash
git rebase --abort
```

Returns to pre-rebase state.

---

## Cherry-Picking Commits

### What is Cherry-Picking?

Cherry-pick applies a specific commit from one branch to another without merging the entire branch.

```
main:     A ← B ← C
                    ↑ cherry-pick D
feature:  A ← B ← D ← E ← F
```

After cherry-pick:
```
main:     A ← B ← C ← D'
feature:  A ← B ← D ← E ← F
```

Note: `D'` is a new commit with same changes as `D` but different hash.

### When to Cherry-Pick

**Use cases:**
- Hotfix: Apply urgent fix from develop to production
- Selective merging: Want specific commits, not entire branch
- Bug fix: Apply fix from feature branch to main before feature is ready
- Experiment: Try a commit from another branch

### Cherry-Pick: Basic Usage

```bash
# Cherry-pick a single commit
git checkout main
git cherry-pick abc123

# Cherry-pick multiple commits
git cherry-pick abc123 def456 ghi789

# Cherry-pick a range of commits
git cherry-pick abc123..def456
```

### Cherry-Pick with Options

```bash
# Cherry-pick without committing (review first)
git cherry-pick -n abc123
# Make changes if needed
git commit

# Cherry-pick and edit commit message
git cherry-pick -e abc123

# Cherry-pick without recording original commit
git cherry-pick -x abc123
# Adds "(cherry picked from commit abc123)" to message
```

### Handling Cherry-Pick Conflicts

If conflicts occur:

```bash
git cherry-pick abc123

# CONFLICT (content): Merge conflict in model.py
# Automatic cherry-pick failed; fix conflicts and commit

# Fix conflicts in files
git add model.py
git cherry-pick --continue

# Or abort
git cherry-pick --abort
```

### Cherry-Pick Use Case: Hotfix

**Scenario**: Critical bug in production, fix exists on develop branch.

```bash
# Current state:
# main:    A ← B ← C (production)
# develop: A ← B ← D ← E ← F (fix in E)

# Apply fix to production
git checkout main
git cherry-pick <commit-hash-of-E>
git push origin main

# Deploy to production
# main:    A ← B ← C ← E'
```

---

## Stashing Changes

### What is Stashing?

Stash temporarily shelves (stashes) changes so you can switch branches without committing.

**Scenario**:
- Working on feature A
- Urgent bug requires switching to another branch
- Changes aren't ready to commit
- Solution: Stash them

### Basic Stashing

```bash
# Stash current changes
git stash

# Output:
# Saved working directory and index state WIP on main: abc123 Last commit message

# Now working directory is clean
git status
# nothing to commit, working tree clean

# Switch branches, do urgent work
git checkout hotfix
# fix bug, commit, push

# Return to original work
git checkout main
git stash pop   # Apply and remove from stash
```

### Stash Commands

```bash
# Stash with a message
git stash push -m "WIP: implementing caching"

# Stash including untracked files
git stash -u

# Stash including ignored files
git stash -a

# List stashes
git stash list
# stash@{0}: WIP on main: abc123 Last commit
# stash@{1}: WIP on feature: def456 Previous commit

# Show stash contents
git stash show stash@{0}

# Show detailed diff
git stash show -p stash@{0}
```

### Applying Stashes

```bash
# Apply most recent stash (keep in stash list)
git stash apply

# Apply specific stash
git stash apply stash@{1}

# Apply and remove from stash list
git stash pop

# Apply to different branch
git checkout other-branch
git stash apply stash@{0}
```

### Managing Stashes

```bash
# Delete specific stash
git stash drop stash@{0}

# Delete all stashes
git stash clear

# Create branch from stash
git stash branch feature/new-work stash@{0}
# Creates branch, applies stash, drops stash
```

### Partial Stashing

```bash
# Stash only specific files
git stash push -m "Partial stash" file1.py file2.py

# Interactive stashing
git stash -p
# Git asks for each change:
# Stash this hunk [y,n,q,a,d,/,s,e,?]?
```

### Stash Use Case: Context Switching

**Scenario**: Implementing new model architecture when critical production issue arises.

```bash
# Working on new model
# Multiple files modified, not ready to commit

# Urgent: production issue
git stash push -u -m "WIP: transformer architecture"

# Fix production issue
git checkout main
git checkout -b hotfix/memory-leak
# fix issue
git add .
git commit -m "Fix memory leak in batch processing"
git push origin hotfix/memory-leak

# Return to model work
git checkout feature/transformer
git stash pop

# Continue working
```

---

## Git Hooks

### What are Git Hooks?

Git hooks are scripts that Git executes automatically at certain points:
- Before/after commits
- Before/after pushes
- Before/after merges
- etc.

Hooks enable automation:
- Lint code before committing
- Run tests before pushing
- Check for secrets
- Format commit messages
- Deploy after merge

### Where Hooks Live

Hooks are stored in `.git/hooks/`:

```bash
ls .git/hooks/
# applypatch-msg.sample
# pre-commit.sample
# pre-push.sample
# ...
```

Remove `.sample` extension to activate.

### Client-Side Hooks

**pre-commit**: Runs before commit is created
- Lint code
- Check for secrets
- Run quick tests

**prepare-commit-msg**: Modify commit message template
- Add ticket numbers
- Enforce message format

**commit-msg**: Validate commit message
- Enforce message conventions
- Check message length

**post-commit**: Runs after commit
- Send notifications
- Log commits

**pre-push**: Runs before push
- Run full test suite
- Check branch naming
- Prevent force push

### Creating a Pre-Commit Hook

**Example**: Prevent committing files with "TODO" comments.

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for TODO comments
if git grep -n "TODO" -- '*.py'; then
    echo "Error: Commit contains TODO comments"
    echo "Remove TODOs or skip this check with --no-verify"
    exit 1
fi

echo "Pre-commit checks passed"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

Test it:
```bash
echo "# TODO: fix this" >> model.py
git add model.py
git commit -m "Add model"

# Output:
# model.py:1:# TODO: fix this
# Error: Commit contains TODO comments
# Remove TODOs or skip this check with --no-verify
```

### Pre-Commit Hook: Linting

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running Black (formatter)..."
black --check .
if [ $? -ne 0 ]; then
    echo "Formatting issues found. Run 'black .' to fix."
    exit 1
fi

echo "Running Flake8 (linter)..."
flake8 .
if [ $? -ne 0 ]; then
    echo "Linting issues found. Fix them before committing."
    exit 1
fi

echo "Running MyPy (type checker)..."
mypy src/
if [ $? -ne 0 ]; then
    echo "Type checking failed."
    exit 1
fi

echo "All pre-commit checks passed!"
exit 0
```

### Pre-Push Hook: Testing

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running tests before push..."
pytest tests/ -v

if [ $? -ne 0 ]; then
    echo "Tests failed. Fix them before pushing."
    exit 1
fi

echo "All tests passed!"
exit 0
```

### Pre-Commit Hook: Secrets Detection

Critical for ML projects that handle credentials:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for potential secrets
if git diff --cached | grep -iE "(api[_-]?key|secret|password|token|credentials).*=.*['\"][^'\"]{10,}['\"]"; then
    echo "Error: Potential secret detected in staged changes"
    echo "Never commit API keys, passwords, or tokens"
    exit 1
fi

# Check for AWS keys
if git diff --cached | grep -E "AKIA[0-9A-Z]{16}"; then
    echo "Error: AWS access key detected"
    exit 1
fi

echo "No secrets detected"
exit 0
```

### Using Pre-Commit Framework

Instead of manual hook scripts, use the `pre-commit` framework:

Install:
```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=10000']
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install hooks:
```bash
pre-commit install
```

Now hooks run automatically on every commit.

Run manually:
```bash
pre-commit run --all-files
```

### Server-Side Hooks

**pre-receive**: Enforce policies on server
- Reject commits without ticket numbers
- Enforce branch naming
- Prevent force pushes to main

**post-receive**: Trigger actions after push
- Deploy to production
- Send notifications
- Trigger CI/CD

**Note**: Server-side hooks require server access (not possible on GitHub/GitLab free tier). Use GitHub Actions or GitLab CI instead.

---

## Submodules and Subtrees

### What are Submodules?

Submodules let you include one Git repository inside another. Useful for:
- Shared libraries
- Vendored dependencies
- Common utilities

### Adding a Submodule

```bash
# Add submodule
git submodule add https://github.com/org/ml-utils.git lib/ml-utils

# This creates:
# - lib/ml-utils/ directory (the submodule)
# - .gitmodules file (submodule configuration)

# Commit the submodule
git add .gitmodules lib/ml-utils
git commit -m "Add ml-utils submodule"
```

### Cloning Repository with Submodules

```bash
# Clone repository
git clone https://github.com/org/ml-pipeline.git

# Initialize and update submodules
cd ml-pipeline
git submodule init
git submodule update

# Or in one command:
git clone --recurse-submodules https://github.com/org/ml-pipeline.git
```

### Updating Submodules

```bash
# Update submodule to latest commit
cd lib/ml-utils
git pull origin main

# Return to main repo
cd ../..
git add lib/ml-utils
git commit -m "Update ml-utils submodule"

# Update all submodules at once
git submodule update --remote --merge
```

### Removing Submodules

```bash
# Remove submodule
git submodule deinit lib/ml-utils
git rm lib/ml-utils
rm -rf .git/modules/lib/ml-utils
git commit -m "Remove ml-utils submodule"
```

### Submodule Challenges

Submodules are powerful but tricky:
- Easy to forget to update
- Detached HEAD state confusing
- Requires extra commands after clone
- Collaboration can be difficult

**Alternative**: Git subtree (simpler but less flexible).

### Git Subtree

Subtree integrates another repository into a subdirectory:

```bash
# Add subtree
git subtree add --prefix lib/ml-utils https://github.com/org/ml-utils.git main --squash

# Pull updates
git subtree pull --prefix lib/ml-utils https://github.com/org/ml-utils.git main --squash

# Push changes back to upstream
git subtree push --prefix lib/ml-utils https://github.com/org/ml-utils.git main
```

**Subtree advantages:**
- No `.gitmodules` file
- Clones work normally
- Simpler for collaborators

**Subtree disadvantages:**
- History can get messy
- Harder to contribute changes upstream

### ML Project Use Case

**Scenario**: Multiple ML projects share data preprocessing utilities.

**Option 1: Submodule**
```
ml-training-pipeline/
├── .gitmodules
├── src/
└── lib/
    └── data-utils/  (submodule: github.com/org/data-utils)

ml-inference-api/
├── .gitmodules
├── src/
└── lib/
    └── data-utils/  (submodule: github.com/org/data-utils)
```

Both projects reference the same shared library. Updates in `data-utils` are reflected in both.

**Option 2: Package**
Better for ML: Publish as pip package.

```bash
# In data-utils repo
python -m build
twine upload dist/*

# In other projects
pip install data-utils
```

More maintainable for Python projects.

---

## Tags and Releases

### What are Tags?

Tags are named references to specific commits. Unlike branches, tags don't move.

**Use cases:**
- Mark releases (v1.0.0, v2.1.3)
- Mark model versions (model-v1, model-v2)
- Mark important points (experiment-baseline)

### Lightweight vs Annotated Tags

**Lightweight tag** (simple pointer):
```bash
git tag v1.0.0
```

**Annotated tag** (full object with metadata):
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
```

Annotated tags include:
- Tagger name and email
- Date
- Message
- GPG signature (optional)

**Always use annotated tags for releases.**

### Creating Tags

```bash
# Create annotated tag
git tag -a v1.0.0 -m "First production release"

# Tag specific commit
git tag -a v0.9.0 abc123 -m "Beta release"

# Signed tag (with GPG key)
git tag -s v1.0.0 -m "Signed release"
```

### Listing Tags

```bash
# List all tags
git tag

# List tags matching pattern
git tag -l "v1.*"
# v1.0.0
# v1.0.1
# v1.1.0

# Show tag details
git show v1.0.0
```

### Pushing Tags

Tags aren't pushed automatically:

```bash
# Push specific tag
git push origin v1.0.0

# Push all tags
git push origin --tags

# Push annotated tags only
git push origin --follow-tags
```

### Deleting Tags

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
```

### Checking Out Tags

```bash
# Checkout tag (detached HEAD)
git checkout v1.0.0

# Create branch from tag
git checkout -b hotfix/v1.0.1 v1.0.0
```

### Semantic Versioning for ML

Use semantic versioning (semver): `MAJOR.MINOR.PATCH`

**For model versions:**
- `MAJOR`: Breaking API changes, different model architecture
- `MINOR`: New features, backward-compatible improvements
- `PATCH`: Bug fixes, minor tweaks

Examples:
- `model-v1.0.0`: Initial production model
- `model-v1.1.0`: Added support for new input features
- `model-v1.1.1`: Fixed preprocessing bug
- `model-v2.0.0`: Switched from ResNet to Transformer (breaking change)

### Creating GitHub Releases

```bash
# Create tag
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

On GitHub:
1. Go to "Releases"
2. Click "Draft a new release"
3. Select tag v1.0.0
4. Add release notes
5. Attach binaries (model files, if appropriate)
6. Publish release

Or use GitHub CLI:
```bash
gh release create v1.0.0 --notes "Release notes here" model.onnx
```

---

## Advanced History Manipulation

### Git Reflog: Your Safety Net

Reflog records every change to HEAD:

```bash
git reflog

# Output:
# abc123 HEAD@{0}: commit: Add feature
# def456 HEAD@{1}: checkout: moving from main to feature
# ghi789 HEAD@{2}: commit: Fix bug
```

Reflog entries expire after ~90 days but can save you from disasters.

### Recovering Deleted Branches

```bash
# Oops, deleted branch with important work
git branch -D important-feature

# Find it in reflog
git reflog
# abc123 HEAD@{5}: commit: Important feature work

# Recreate branch
git checkout -b important-feature abc123
```

### Recovering Lost Commits

```bash
# Reset to wrong commit, lost work
git reset --hard HEAD~10

# Find lost commits in reflog
git reflog
# abc123 HEAD@{3}: commit: The commit I need

# Create branch from lost commit
git branch recovered abc123
```

### Git Bisect: Binary Search for Bugs

**Scenario**: Tests passed 100 commits ago, failing now. Which commit broke it?

Manual testing would take hours. Bisect automates it using binary search.

```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good abc123

# Git checks out middle commit
# Test it manually or automatically
pytest tests/

# If tests pass:
git bisect good

# If tests fail:
git bisect bad

# Git continues binary search
# After ~log2(n) steps, identifies problematic commit

# Reset after finding
git bisect reset
```

Automated bisect:
```bash
git bisect start HEAD abc123
git bisect run pytest tests/
# Git automatically tests each commit until it finds the breakage
```

### Git Filter-Branch: Rewriting History

**Warning**: Powerful and dangerous. Only use if you know what you're doing.

**Use case**: Remove sensitive file from entire history.

```bash
# Remove file from all commits
git filter-branch --tree-filter 'rm -f secrets.yaml' HEAD

# Remove file from index
git filter-branch --index-filter 'git rm --cached --ignore-unmatch secrets.yaml' HEAD
```

**Better alternative**: Use BFG Repo-Cleaner (faster, safer).

```bash
# Install BFG
brew install bfg  # or download JAR

# Remove file
bfg --delete-files secrets.yaml

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Rewriting Author Information

```bash
# Change author for last commit
git commit --amend --author="New Name <new@email.com>"

# Change author for multiple commits
git rebase -i HEAD~5
# Mark commits as 'edit'
# For each:
git commit --amend --author="New Name <new@email.com>"
git rebase --continue
```

---

## Git for Machine Learning

### DVC: Data Version Control

Git isn't designed for large files. DVC extends Git for ML:

```bash
# Install DVC
pip install dvc

# Initialize DVC
dvc init

# Track large file
dvc add data/train.csv
git add data/train.csv.dvc .gitignore
git commit -m "Add training data"

# Push data to remote storage (S3, GCS, etc.)
dvc push

# Clone and get data
git clone repo.git
dvc pull
```

DVC creates `.dvc` files that Git tracks, while actual data goes to cloud storage.

### MLflow Integration

Track experiments with Git integration:

```python
import mlflow

# Log Git metadata automatically
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_metric("accuracy", 0.95)

    # MLflow records:
    # - Git commit hash
    # - Git branch
    # - Git repo URL
```

Reproduce experiments:
```bash
# Find experiment's Git commit
mlflow experiments list

# Checkout that commit
git checkout abc123

# Rerun experiment
python train.py
```

### Git Workflow for Experiments

```bash
# Create experiment branch
git checkout -b experiment/resnet-dropout-05

# Modify config
cat > config.yaml << EOF
model: resnet50
dropout: 0.5
learning_rate: 0.001
EOF

# Run experiment
python train.py --config config.yaml

# Commit results
git add config.yaml results.json
git commit -m "Experiment: ResNet50 with dropout=0.5, acc=0.89"

# Tag for future reference
git tag -a exp-dropout-05 -m "Dropout experiment, accuracy=0.89"

# If successful, merge to main
git checkout main
git merge experiment/resnet-dropout-05
```

### .gitattributes for ML Projects

```
# .gitattributes

# Mark large files as binary (don't try to diff)
*.pkl binary
*.h5 binary
*.pth binary
*.onnx binary

# Track notebooks without output (cleaner diffs)
*.ipynb filter=nbstrip_full

# Use LFS for large files
*.pth filter=lfs diff=lfs merge=lfs -text
*.h5 filter=lfs diff=lfs merge=lfs -text
```

### Jupyter Notebook Version Control

Notebooks are JSON, hard to diff. Solutions:

**Option 1: Strip output before committing**

Install nbstripout:
```bash
pip install nbstripout
nbstripout --install
```

Now notebooks are committed without output (cleaner diffs).

**Option 2: ReviewNB (GitHub App)**

Provides visual notebook diffs in Pull Requests.

**Option 3: Jupytext**

Convert notebooks to .py files:
```bash
pip install jupytext
jupytext --to py notebook.ipynb
```

Track the .py version in Git.

---

## Performance and Optimization

### Shallow Clones

For CI/CD, you don't need full history:

```bash
# Clone only latest commit
git clone --depth 1 https://github.com/org/repo.git

# Clone last 10 commits
git clone --depth 10 https://github.com/org/repo.git
```

**Pros**: Much faster, smaller download
**Cons**: Limited history, can't push

### Partial Clones

Clone without large files:

```bash
git clone --filter=blob:limit=1m https://github.com/org/repo.git
# Only downloads files < 1MB
# Larger files downloaded on demand
```

### Git LFS for Large Files

```bash
# Install Git LFS
git lfs install

# Track file types
git lfs track "*.pth"
git lfs track "*.h5"

# Git LFS stores pointers in repo, actual files in LFS storage
```

### Optimizing Repository

```bash
# Garbage collect
git gc --aggressive --prune=now

# Verify repository integrity
git fsck

# Count objects
git count-objects -vH
```

### Git Configuration for Performance

```bash
# Increase HTTP buffer for large files
git config --global http.postBuffer 524288000

# Enable parallel fetch
git config --global fetch.parallel 4

# Enable file system cache (Windows)
git config --global core.fscache true

# Enable commit graph for faster operations
git config --global core.commitGraph true
git config --global gc.writeCommitGraph true
```

---

## Recovery and Disaster Management

### Recovering from Reset --hard

```bash
# Accidentally ran:
git reset --hard HEAD~5

# Recover with reflog
git reflog
# Find the commit before reset
git reset --hard HEAD@{1}
```

### Recovering from Rebase Disaster

```bash
# Rebase went wrong
git rebase --abort  # If still in progress

# If already finished
git reflog
# Find pre-rebase state
git reset --hard HEAD@{5}
```

### Undoing Git Push

```bash
# Pushed wrong commit to remote

# Option 1: Revert (safe, creates new commit)
git revert abc123
git push origin main

# Option 2: Force push (dangerous!)
git reset --hard HEAD~1
git push --force-with-lease origin main
```

### Recovering from Deleted Repository

If you have local clone:
```bash
# Your local clone is a full backup
# Recreate remote repository
# Push everything
git push --all origin
git push --tags origin
```

If you don't have local clone: Contact GitHub support.

---

## Summary and Key Takeaways

### Core Concepts

1. **Interactive rebase**: Clean up history before sharing
2. **Cherry-pick**: Apply specific commits between branches
3. **Stash**: Temporarily save work to switch context
4. **Hooks**: Automate tasks at Git lifecycle points
5. **Tags**: Mark important points (releases, experiments)
6. **Reflog**: Safety net for recovering lost work

### Essential Commands Cheat Sheet

```bash
# Interactive rebase
git rebase -i HEAD~3          # Rebase last 3 commits
git rebase -i main            # Rebase from branch point

# Cherry-pick
git cherry-pick abc123        # Apply specific commit
git cherry-pick abc..def      # Apply range of commits

# Stash
git stash                     # Stash changes
git stash pop                 # Apply and remove stash
git stash list                # List stashes

# Tags
git tag -a v1.0.0 -m "msg"   # Create annotated tag
git push origin v1.0.0        # Push tag
git push origin --tags        # Push all tags

# Recovery
git reflog                    # View reflog
git reset --hard HEAD@{1}     # Reset to reflog entry

# Bisect
git bisect start              # Start bisect
git bisect good/bad           # Mark commits
git bisect reset              # End bisect
```

### Best Practices

1. **Never rebase shared branches**: Only rebase local, unpushed commits
2. **Use pre-commit hooks**: Catch issues before they enter history
3. **Tag releases**: Always tag production deployments
4. **Keep reflog**: Don't run `git reflog expire` unless necessary
5. **Cherry-pick sparingly**: Prefer merging when possible
6. **Stash frequently**: Better than messy commits
7. **Test interactive rebase**: Practice on test repos first
8. **Document hooks**: Add README explaining what hooks do
9. **Use DVC for data**: Not Git
10. **Sign tags**: For verified releases

### For AI/ML Projects

- **Experiment branches**: One branch per experiment, tag successful ones
- **Pre-commit hooks**: Check for large files, secrets, and lint code
- **DVC integration**: Version data and models properly
- **MLflow tracking**: Record Git metadata with experiments
- **Semantic versioning**: Tag model releases properly
- **Jupyter notebooks**: Strip output or use Jupytext
- **Git LFS**: For model weights that must be in Git

### What's Next

This completes the Git module. You now know:
- Git fundamentals (Lecture 1)
- Branching and merging (Lecture 2)
- Collaboration (Lecture 3)
- Advanced techniques (Lecture 4)

**Next steps:**
1. Complete all exercises to practice these concepts
2. Set up pre-commit hooks in your projects
3. Contribute to an open-source project
4. Implement Git workflows in your team

### Further Reading

- Pro Git book (entire book): https://git-scm.com/book/en/v2
- Git documentation: https://git-scm.com/doc
- DVC documentation: https://dvc.org/doc
- Pre-commit framework: https://pre-commit.com/
- Semantic versioning: https://semver.org/

---

**Practice Exercises**: Complete Exercises 06 and 07 to master advanced Git techniques through hands-on ML project scenarios.
