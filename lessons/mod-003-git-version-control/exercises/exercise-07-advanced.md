# Exercise 07: Advanced Git Techniques

## Overview

**Difficulty**: Advanced
**Estimated Time**: 120-150 minutes
**Prerequisites**: Exercises 01-06, Lecture 04 - Advanced Git

In this exercise, you'll master advanced Git techniques including interactive rebasing, Git hooks, cherry-picking, stashing advanced workflows, bisecting to find bugs, submodules, and recovery techniques. These skills are essential for complex ML infrastructure projects.

## Learning Objectives

By completing this exercise, you will:

- Use interactive rebase to clean up commit history
- Implement custom Git hooks for automation
- Cherry-pick specific commits across branches
- Master stashing workflows
- Use git bisect to find bug-introducing commits
- Work with Git submodules
- Recover from Git mistakes
- Reflog for time travel
- Advanced merging strategies

## Scenario

You're maintaining a large ML infrastructure codebase with complex history. You need to:
- Clean up messy commit history before merging to main
- Automate code quality checks with hooks
- Selectively apply fixes from one branch to another
- Find when a performance regression was introduced
- Manage third-party dependencies as submodules
- Recover from accidental data loss

## Prerequisites

```bash
# Create project for advanced techniques
mkdir ml-platform-advanced
cd ml-platform-advanced
git init
git config init.defaultBranch main

# Create initial structure
mkdir -p src/{api,models,pipeline} tests scripts
touch README.md
git add .
git commit -m "Initial commit"
```

---

## Part 1: Interactive Rebase

### Task 1.1: Clean Up Commit History

Use interactive rebase to reorganize commits.

**Instructions:**

```bash
# Create a messy feature branch
git switch -c feature/model-serving

# Make several small commits (simulating messy development)
echo "class ModelServer:" > src/api/server.py
git add src/api/server.py
git commit -m "wip"

echo "    def __init__(self):" >> src/api/server.py
git add src/api/server.py
git commit -m "add init"

echo "        self.model = None" >> src/api/server.py
git add src/api/server.py
git commit -m "add model attr"

echo "    def load_model(self, path):" >> src/api/server.py
git add src/api/server.py
git commit -m "load method"

echo "        self.model = load(path)" >> src/api/server.py
git add src/api/server.py
git commit -m "fix: typo in load"

echo "    def predict(self, data):" >> src/api/server.py
git add src/api/server.py
git commit -m "predict method"

# View the messy history
git log --oneline -6

# Clean it up with interactive rebase
git rebase -i HEAD~5

# Editor opens with:
# pick abc123 wip
# pick def456 add init
# pick ghi789 add model attr
# pick jkl012 load method
# pick mno345 fix: typo in load
# pick pqr678 predict method

# Change to:
# pick abc123 wip
# squash def456 add init
# squash ghi789 add model attr
# squash jkl012 load method
# fixup mno345 fix: typo in load
# pick pqr678 predict method

# Save and close. Editor opens again for commit message:
# Change to:
# "feat(api): add model serving infrastructure
#
# Implement ModelServer class with:
# - Model loading from path
# - Prediction interface
#
# Foundation for ML model deployment."

# View cleaned history
git log --oneline -3
```

**Rebase Commands:**
- `pick` - keep commit as-is
- `reword` - keep changes, edit message
- `edit` - pause to amend commit
- `squash` - merge with previous, keep both messages
- `fixup` - merge with previous, discard this message
- `drop` - remove commit entirely

---

### Task 1.2: Reorder Commits

Reorganize commit order logically.

**Instructions:**

```bash
# Create commits in wrong order
echo "# Tests" > tests/test_server.py
git add tests/test_server.py
git commit -m "test: add server tests"

echo "# Documentation" > docs/server.md
git add docs/server.md
git commit -m "docs: document server API"

# Oops, should have added docs before tests
git rebase -i HEAD~2

# Reorder:
# pick <hash> docs: document server API
# pick <hash> test: add server tests

# Save - commits are now in logical order
git log --oneline -4
```

---

### Task 1.3: Split a Large Commit

Break one commit into multiple logical commits.

**Instructions:**

```bash
# Make large commit with multiple changes
cat >> src/api/server.py << 'EOF'

    def health_check(self):
        """Check server health."""
        return {"status": "healthy"}

    def metrics(self):
        """Get server metrics."""
        return {"requests": 0}
EOF

cat > src/api/config.py << 'EOF'
"""Server configuration."""

CONFIG = {
    "port": 8000,
    "host": "0.0.0.0"
}
EOF

git add src/api/
git commit -m "Add features"

# Oops, too many things in one commit. Split it:
git rebase -i HEAD~1

# Change "pick" to "edit"
# Git pauses at the commit

# Reset the commit but keep changes
git reset HEAD^

# Now commit parts separately
git add src/api/server.py
git commit -m "feat(api): add health check and metrics endpoints"

git add src/api/config.py
git commit -m "feat(config): add server configuration module"

# Continue rebase
git rebase --continue

# View split commits
git log --oneline -3
```

---

## Part 2: Git Hooks

### Task 2.1: Pre-Commit Hook

Create hook to run checks before committing.

**Instructions:**

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook: Run code quality checks

echo "Running pre-commit checks..."

# Check for Python syntax errors
echo "1. Checking Python syntax..."
python_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$python_files" ]; then
    for file in $python_files; do
        python -m py_compile "$file"
        if [ $? -ne 0 ]; then
            echo "❌ Syntax error in $file"
            exit 1
        fi
    done
    echo "✅ Python syntax OK"
fi

# Check for debug statements
echo "2. Checking for debug statements..."
if git diff --cached | grep -i "print(\|pdb\|breakpoint("; then
    echo "❌ Found debug statements. Remove before committing:"
    git diff --cached | grep -n -i "print(\|pdb\|breakpoint("
    echo ""
    echo "To commit anyway: git commit --no-verify"
    exit 1
fi
echo "✅ No debug statements found"

# Check for large files
echo "3. Checking file sizes..."
max_size=1048576  # 1 MB
for file in $(git diff --cached --name-only --diff-filter=ACM); do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt $max_size ]; then
            echo "❌ File too large: $file ($size bytes > $max_size bytes)"
            echo "Consider using Git LFS for large files"
            exit 1
        fi
    fi
done
echo "✅ File sizes OK"

# Check for AWS keys (security)
echo "4. Checking for secrets..."
if git diff --cached | grep -E "AKIA[0-9A-Z]{16}"; then
    echo "❌ Possible AWS key detected!"
    exit 1
fi
echo "✅ No secrets detected"

echo ""
echo "✅ All pre-commit checks passed!"
exit 0
EOF

chmod +x .git/hooks/pre-commit

# Test the hook
echo "print('debug')" > src/test.py
git add src/test.py
git commit -m "test commit"

# Hook should block it!

# Remove debug
echo "# No debug" > src/test.py
git add src/test.py
git commit -m "feat: add test module"

# Should succeed
```

---

### Task 2.2: Post-Commit Hook

Run actions after successful commit.

**Instructions:**

```bash
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# Post-commit hook: Log commits

commit_hash=$(git rev-parse HEAD)
commit_msg=$(git log -1 --pretty=%B)
timestamp=$(date +"%Y-%m-%d %H:%M:%S")

echo "[$timestamp] $commit_hash: $commit_msg" >> .git/commit-log.txt

# Notify about commit
echo "✅ Commit logged: $commit_hash"
EOF

chmod +x .git/hooks/post-commit

# Test it
echo "# Update" >> README.md
git add README.md
git commit -m "docs: update README"

# Check log
cat .git/commit-log.txt
```

---

### Task 2.3: Pre-Push Hook

Validate before pushing to remote.

**Instructions:**

```bash
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook: Run tests before push

echo "Running pre-push checks..."

# Run tests
echo "1. Running tests..."
# pytest tests/ -v
echo "✅ Tests passed (simulated)"

# Check branch name
current_branch=$(git branch --show-current)
if [ "$current_branch" = "main" ]; then
    echo "⚠️  Pushing directly to main!"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Push aborted"
        exit 1
    fi
fi

# Check commit messages
echo "2. Validating commit messages..."
commits=$(git log @{u}.. --pretty=format:"%s")
while read -r msg; do
    if ! echo "$msg" | grep -E "^(feat|fix|docs|test|refactor|chore)(\(.+\))?: .+"; then
        echo "❌ Invalid commit message format: $msg"
        echo "Use: type(scope): message"
        echo "Example: feat(api): add new endpoint"
        exit 1
    fi
done <<< "$commits"
echo "✅ Commit messages valid"

echo ""
echo "✅ All pre-push checks passed!"
exit 0
EOF

chmod +x .git/hooks/pre-push

# Test (simulated - no actual remote)
# git push origin feature-branch
```

---

## Part 3: Cherry-Picking

### Task 3.1: Apply Specific Commits

Selectively apply commits to another branch.

**Instructions:**

```bash
# Create hotfix on main
git switch main
git switch -c hotfix/critical-bug

echo "def fix_critical_bug():" > src/api/fixes.py
echo "    return 'fixed'" >> src/api/fixes.py
git add src/api/fixes.py
git commit -m "fix: critical security vulnerability in auth"

echo "def another_fix():" >> src/api/fixes.py
git add src/api/fixes.py
git commit -m "fix: memory leak in model loading"

# Return to feature branch
git switch feature/model-serving

# Cherry-pick only the security fix
git log hotfix/critical-bug --oneline
# Note the commit hash of security fix

git cherry-pick <security-fix-hash>

# Now feature branch has the security fix without other changes

# View history
git log --oneline --graph --all -10
```

---

### Task 3.2: Cherry-Pick Multiple Commits

Pick a range of commits.

**Instructions:**

```bash
# Cherry-pick multiple commits
git cherry-pick <hash1> <hash2> <hash3>

# Or cherry-pick a range
git cherry-pick <start-hash>..<end-hash>

# If conflicts occur:
# 1. Resolve conflicts
# 2. git add <resolved-files>
# 3. git cherry-pick --continue

# To abort:
# git cherry-pick --abort
```

---

## Part 4: Stashing Advanced Workflows

### Task 4.1: Stash with Message

Save work in progress with description.

**Instructions:**

```bash
# Make changes
echo "# WIP feature" >> src/api/server.py

# Stash with description
git stash push -m "WIP: new caching feature for predictions"

# List stashes
git stash list

# Output:
# stash@{0}: On feature/model-serving: WIP: new caching feature

# Apply later
git stash pop

# Or apply without removing from stash
# git stash apply stash@{0}
```

---

### Task 4.2: Partial Stashing

Stash only specific files.

**Instructions:**

```bash
# Make changes to multiple files
echo "# Change 1" >> src/api/server.py
echo "# Change 2" >> src/models/model.py
echo "# Change 3" >> tests/test_api.py

# Stash only server.py
git stash push -m "server changes" src/api/server.py

# Other files still have changes
git status

# Apply stash
git stash pop
```

---

### Task 4.3: Create Branch from Stash

Turn stashed work into a branch.

**Instructions:**

```bash
# Stash some work
echo "# Experimental feature" >> src/api/server.py
git stash

# Create branch from stash
git stash branch experiment/new-feature

# Now on new branch with stashed changes applied
git status
```

---

## Part 5: Git Bisect

### Task 5.1: Find Bug with Bisect

Use binary search to find bug introduction.

**Instructions:**

```bash
# Create history with a bug introduced
git switch main
git switch -c debug/find-bug

# Make good commits
for i in {1..10}; do
    echo "version $i" >> src/models/model.py
    git add src/models/model.py
    git commit -m "Update model v$i"
done

# Introduce bug in commit 6
git checkout HEAD~4
echo "BUGGY_CODE = True" >> src/models/model.py
git add src/models/model.py
git commit -m "Update model v6"

# Continue with more commits
for i in {7..10}; do
    echo "version $i" >> src/models/model.py
    git add src/models/model.py
    git commit -m "Update model v$i"
done

# Now use bisect to find when bug was introduced
git bisect start

# Mark current as bad
git bisect bad

# Mark earlier commit as good (before the bug)
git bisect good HEAD~10

# Git checks out middle commit
# Test it (manually or with script)
cat src/models/model.py | grep "BUGGY_CODE"

# If bug exists:
git bisect bad

# If no bug:
# git bisect good

# Git continues binary search
# Repeat until Git finds the exact commit

# Reset when done
git bisect reset
```

---

### Task 5.2: Automate Bisect with Script

Let Git automate the bisect process.

**Instructions:**

```bash
# Create test script
cat > scripts/test_for_bug.sh << 'EOF'
#!/bin/bash
# Return 0 if good, 1 if bad

if grep -q "BUGGY_CODE" src/models/model.py; then
    echo "Bug found!"
    exit 1
else
    echo "No bug"
    exit 0
fi
EOF

chmod +x scripts/test_for_bug.sh

# Run automated bisect
git bisect start HEAD HEAD~10
git bisect run scripts/test_for_bug.sh

# Git automatically finds the bad commit!
```

---

## Part 6: Git Reflog and Recovery

### Task 6.1: Recover Lost Commits

Use reflog to find and recover commits.

**Instructions:**

```bash
# Make some commits
echo "important work" > important.txt
git add important.txt
git commit -m "Important work"

# Note the commit hash
git log --oneline -1

# Accidentally reset (lose the commit)
git reset --hard HEAD~1

# Commit is gone!
git log --oneline -1

# Use reflog to find it
git reflog

# Output shows:
# abc123 HEAD@{0}: reset: moving to HEAD~1
# def456 HEAD@{1}: commit: Important work

# Recover the commit
git checkout HEAD@{1}

# Or create branch at that point
git branch recovery HEAD@{1}
git switch recovery

# Your work is recovered!
```

---

### Task 6.2: Undo Rebase

Recover from bad rebase.

**Instructions:**

```bash
# Before rebase
git log --oneline -5

# Do rebase
git rebase -i HEAD~3
# Make changes and complete

# Oops, messed up the rebase!

# Find pre-rebase state in reflog
git reflog

# Look for: "rebase -i (start)"
# The entry before that is pre-rebase state

# Reset to pre-rebase
git reset --hard HEAD@{5}  # Adjust number based on reflog

# Rebase undone!
```

---

## Part 7: Git Submodules

### Task 7.1: Add Submodule

Manage external dependencies as submodules.

**Instructions:**

```bash
# Add a submodule (external library)
# git submodule add https://github.com/user/ml-utils.git libs/ml-utils

# Simulated for exercise:
mkdir -p libs
cd libs
mkdir ml-utils
cd ml-utils
git init
echo "# ML Utilities" > README.md
git add README.md
git commit -m "Initial commit"
cd ../..

# Register as submodule
git submodule add ./libs/ml-utils libs/ml-utils

# .gitmodules file created
cat .gitmodules

git add .gitmodules libs/ml-utils
git commit -m "chore: add ml-utils submodule"
```

---

### Task 7.2: Update Submodule

Update to latest version of submodule.

**Instructions:**

```bash
# Update submodule
cd libs/ml-utils
# git pull origin main  # If real remote

# Update to specific commit
git checkout <commit-hash>
cd ../..

# Commit submodule update
git add libs/ml-utils
git commit -m "chore: update ml-utils submodule to v2.0"
```

---

### Task 7.3: Clone Repository with Submodules

**Instructions:**

```bash
# When cloning a repo with submodules:
# git clone --recursive <repo-url>

# Or if already cloned:
# git submodule init
# git submodule update

# Or in one command:
# git submodule update --init --recursive
```

---

## Part 8: Advanced Merge Strategies

### Task 8.1: Octopus Merge

Merge multiple branches at once.

**Instructions:**

```bash
# Create multiple feature branches
git switch -c feature/a
echo "Feature A" > feature-a.txt
git add feature-a.txt
git commit -m "feat: add feature A"

git switch main
git switch -c feature/b
echo "Feature B" > feature-b.txt
git add feature-b.txt
git commit -m "feat: add feature B"

git switch main
git switch -c feature/c
echo "Feature C" > feature-c.txt
git add feature-c.txt
git commit -m "feat: add feature C"

# Merge all at once (if no conflicts)
git switch main
git merge feature/a feature/b feature/c -m "Merge features A, B, and C"

# All three merged in one commit!
git log --oneline --graph -5
```

---

### Task 8.2: Ours/Theirs Strategy

Resolve conflicts automatically.

**Instructions:**

```bash
# When merging, use strategy to prefer one side

# Always prefer current branch (ours)
# git merge -X ours feature-branch

# Always prefer incoming branch (theirs)
# git merge -X theirs feature-branch

# Useful for generated files where one version is definitely correct
```

---

## Part 9: Git Worktrees

### Task 9.1: Multiple Working Directories

Work on multiple branches simultaneously.

**Instructions:**

```bash
# Add worktree for another branch
git worktree add ../ml-platform-feature feature/model-serving

# Now you have two working directories:
# - ml-platform-advanced/ (main branch)
# - ml-platform-feature/ (feature/model-serving branch)

# Work in both simultaneously
cd ../ml-platform-feature
# Make changes

cd ../ml-platform-advanced
# Different branch, different changes

# List worktrees
git worktree list

# Remove worktree when done
git worktree remove ../ml-platform-feature
```

---

## Part 10: Troubleshooting and Recovery

### Task 10.1: Fix Detached HEAD

Recover from detached HEAD state.

**Instructions:**

```bash
# Accidentally checkout commit hash
git checkout HEAD~5

# You're in detached HEAD state!
# Make some commits
echo "work" > work.txt
git add work.txt
git commit -m "Work in detached HEAD"

# Create branch to save work
git branch temp-work

# Switch to it
git switch temp-work

# Merge into main if needed
git switch main
git merge temp-work
```

---

### Task 10.2: Remove Sensitive Data from History

Clean up committed secrets.

**Instructions:**

```bash
# If you committed a secret:
# USE: git filter-branch or BFG Repo-Cleaner

# Example with filter-branch:
# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch path/to/secret.key" \
#   --prune-empty --tag-name-filter cat -- --all

# Then force push:
# git push origin --force --all
# git push origin --force --tags

# Warning: Rewrites history! Coordinate with team.
```

---

## Validation

### Verify Your Skills

```bash
# Check your Git expertise
git log --oneline --graph --all -20
git reflog -10
git stash list
git worktree list

# Verify hooks
ls -la .git/hooks/

# Test recovery skills
# git reflog
# git fsck --lost-found
```

---

## Challenge Tasks

### Challenge 1: Create Alias for Complex Command

```bash
git config alias.lol "log --graph --decorate --oneline --all"
git lol
```

### Challenge 2: Bisect Performance Regression

Use bisect to find when inference latency increased.

### Challenge 3: Interactive Rebase Master

Rebase 20 commits into logical groups.

---

## Troubleshooting

**Issue**: "Rebase conflict I can't resolve"
```bash
git rebase --abort
# Try different approach or merge instead
```

**Issue**: "Lost important work"
```bash
git reflog
git fsck --lost-found
```

**Issue**: "Committed to wrong branch"
```bash
git log --oneline -1  # Note commit hash
git reset --hard HEAD~1  # Remove from current
git checkout correct-branch
git cherry-pick <hash>  # Add to correct branch
```

---

## Reflection Questions

1. **When should you use interactive rebase vs. merge?**
2. **What are the dangers of rewriting history?**
3. **How does bisect help debug complex issues?**
4. **When would you use submodules vs. package managers?**
5. **What's the difference between reset, revert, and checkout?**

---

## Summary

Congratulations! You've mastered advanced Git techniques:

- ✅ Interactive rebasing for clean history
- ✅ Custom Git hooks for automation
- ✅ Cherry-picking specific changes
- ✅ Advanced stashing workflows
- ✅ Bisecting to find bugs
- ✅ Reflog for recovery
- ✅ Git submodules
- ✅ Advanced merge strategies
- ✅ Worktrees for parallel work
- ✅ Troubleshooting and recovery

### Key Commands

```bash
git rebase -i HEAD~N         # Interactive rebase
git cherry-pick <hash>       # Apply specific commit
git stash push -m "msg"      # Stash with message
git bisect start             # Find bug binary search
git reflog                   # View reference log
git submodule add <url>      # Add submodule
git worktree add <path>      # Create worktree
git filter-branch            # Rewrite history
```

### Next Steps

- Apply these techniques in real projects
- Complete Module 003 quiz
- Practice advanced workflows

**Outstanding work!** You're now a Git expert ready for complex ML infrastructure projects.
