# Lecture 02: Branching and Merging

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding Branches](#understanding-branches)
3. [Branch Operations](#branch-operations)
4. [Merging Strategies](#merging-strategies)
5. [Resolving Merge Conflicts](#resolving-merge-conflicts)
6. [Git Workflows](#git-workflows)
7. [Branch Management Best Practices](#branch-management-best-practices)
8. [Branches in AI/ML Projects](#branches-in-aiml-projects)
9. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
10. [Summary and Key Takeaways](#summary-and-key-takeaways)

---

## Introduction

### Why Branching Matters for AI Infrastructure

Imagine you're maintaining a production ML inference API serving thousands of requests per second. You need to:
- Add a new model version for testing (but keep the old one serving traffic)
- Fix a critical bug in the data preprocessing pipeline
- Experiment with a new caching layer
- All simultaneously, without breaking production

Without branching, this is impossible. With branching, it's straightforward.

Branches allow parallel development. They're Git's killer feature—the reason it dominates version control. Understanding branching transforms you from a Git user into a Git master.

### Learning Objectives

By the end of this lecture, you will:

- Understand how Git implements branches (they're cheaper than you think)
- Create, switch between, and delete branches confidently
- Merge branches using different strategies (fast-forward, three-way, squash)
- Resolve merge conflicts systematically
- Implement common Git workflows (Feature Branch, Git Flow, GitHub Flow)
- Apply branching strategies to ML experiment tracking
- Use branches for environment-specific configurations (dev, staging, prod)
- Troubleshoot common branching issues

### The AI Infrastructure Context

In AI infrastructure, branches serve specific purposes:

**Development branches:**
- Feature development (new model architectures, API endpoints)
- Experiment tracking (different hyperparameters, architectures)
- Bug fixes (urgent production issues)
- Refactoring (code improvements without changing behavior)

**Environment branches:**
- `main/master`: Production-ready code
- `staging`: Pre-production testing
- `develop`: Integration branch for features

**Use cases:**
- **A/B testing**: Different model versions on separate branches
- **Environment configs**: Dev vs. production configurations
- **Experimentation**: Try new approaches without affecting main codebase
- **Hotfixes**: Emergency production fixes

---

## Understanding Branches

### What is a Branch?

In Git, a branch is simply a lightweight movable pointer to a commit. That's it. When you create a branch, Git creates a 40-byte file containing the SHA-1 hash of the commit it points to.

```
main branch:       E
                   |
                   v
A ← B ← C ← D ← E
```

Each letter is a commit. The `main` branch points to commit E.

### How Git Knows Your Current Branch

Git maintains a special pointer called `HEAD` that points to the current branch:

```
        HEAD
         |
         v
       main
         |
         v
A ← B ← C ← D ← E
```

When you make a commit, the current branch moves forward:

```
        HEAD
         |
         v
       main
         |
         v
A ← B ← C ← D ← E ← F
```

### Creating a Branch

```bash
# Create a new branch
git branch feature/new-model

# Branches now:
        HEAD
         |
         v
       main
         |
         v
A ← B ← C ← D ← E
         ^
         |
    feature/new-model
```

Both branches point to the same commit. No files were copied. Git just created a pointer.

### Switching Branches

```bash
# Switch to the new branch (old way)
git checkout feature/new-model

# Switch to the new branch (new way, Git 2.23+)
git switch feature/new-model

# After switching:
         main
          |
          v
A ← B ← C ← D ← E
          ^
          |
        HEAD ← feature/new-model
```

Now `HEAD` points to `feature/new-model`.

### Making Commits on a Branch

```bash
# Make changes and commit
echo "model = ResNet50()" >> model.py
git add model.py
git commit -m "Add ResNet50 model"

# Tree now:
         main
          |
          v
A ← B ← C ← D ← E
                 \
                  F ← feature/new-model
                      ^
                      |
                     HEAD
```

The `feature/new-model` branch moved forward. The `main` branch stayed put.

### Branches Are Cheap

Creating a branch in Git:
- **Takes milliseconds**
- **Uses 41 bytes** (40-byte SHA-1 + newline)
- **Doesn't copy files**
- **Doesn't duplicate history**

This is why Git encourages branching. Create branches liberally!

---

## Branch Operations

### Creating Branches

```bash
# Create a branch (doesn't switch to it)
git branch feature/add-logging

# Create and switch in one command (old way)
git checkout -b feature/add-logging

# Create and switch in one command (new way)
git switch -c feature/add-logging

# Create branch from specific commit
git branch feature/old-code abc123

# Create branch from remote branch
git checkout -b local-feature origin/remote-feature
```

### Listing Branches

```bash
# List local branches
git branch

# Output:
#   feature/add-logging
# * main
#   feature/new-model

# The * indicates current branch

# List all branches (including remote)
git branch -a

# List remote branches only
git branch -r

# Show last commit on each branch
git branch -v

# Show merged branches
git branch --merged

# Show unmerged branches
git branch --no-merged
```

### Switching Branches

```bash
# Switch to existing branch (new way)
git switch main

# Switch to existing branch (old way)
git checkout main

# Create and switch to new branch
git switch -c feature/experiment

# Switch to previous branch
git switch -

# This is like `cd -` in the shell
```

**Important**: Before switching branches:
- Commit your changes, or
- Stash your changes (covered in Lecture 04)

Otherwise, Git may prevent the switch or carry uncommitted changes to the new branch.

### Renaming Branches

```bash
# Rename current branch
git branch -m new-name

# Rename a different branch
git branch -m old-name new-name

# Example: rename master to main
git branch -m master main
```

### Deleting Branches

```bash
# Delete a merged branch (safe)
git branch -d feature/completed

# Force delete an unmerged branch (dangerous)
git branch -D feature/abandoned

# Delete remote branch
git push origin --delete feature/old-branch
```

Git prevents deleting branches with unmerged changes unless you force it with `-D`.

### Viewing Branch Differences

```bash
# Show commits in feature branch not in main
git log main..feature/new-model

# Show commits that differ between branches
git log --left-right --oneline main...feature/new-model

# Output:
# < abc123 Main branch commit
# > def456 Feature branch commit
```

---

## Merging Strategies

### Types of Merges

Git supports three main merge strategies:

1. **Fast-forward merge** (simplest)
2. **Three-way merge** (creates merge commit)
3. **Squash merge** (combines commits)

### Fast-Forward Merge

When the target branch hasn't changed since the feature branch was created:

```
Before merge:
       main
        |
        v
A ← B ← C
         \
          D ← E ← feature
                   ^
                   |
                  HEAD

After git merge feature (from main):
                  main
                   |
                   v
A ← B ← C ← D ← E
            ^
            |
          feature
```

Git simply moves the `main` pointer forward. No merge commit is created.

```bash
# Perform fast-forward merge
git checkout main
git merge feature
```

Output:
```
Updating abc123..def456
Fast-forward
 model.py | 10 ++++++++
 1 file changed, 10 insertions(+)
```

### Three-Way Merge

When both branches have diverged:

```
Before merge:
         main
          |
          v
A ← B ← C ← F ← G
         \
          D ← E ← feature
                   ^
                   |
                  HEAD

After git merge feature (from main):
              main
               |
               v
A ← B ← C ← F ← G ← M
         \         /
          D ← E ←-/  feature
```

Git creates a new merge commit (M) with two parents.

```bash
# Perform three-way merge
git checkout main
git merge feature
```

Git opens an editor for the merge commit message:
```
Merge branch 'feature' into main

# Please enter a commit message to explain why this merge is necessary.
```

### Preventing Fast-Forward (Always Create Merge Commit)

```bash
# Force creation of merge commit even if fast-forward is possible
git merge --no-ff feature

# This creates explicit merge commit showing the feature was merged
```

**When to use `--no-ff`:**
- Want to preserve that a feature branch existed
- Need to revert an entire feature as one operation
- Following Git Flow workflow

### Squash Merge

Combines all feature branch commits into a single commit:

```
Before squash merge:
       main
        |
        v
A ← B ← C
         \
          D ← E ← F ← feature
             (3 commits)

After git merge --squash feature:
              main
               |
               v
A ← B ← C ← D'
        (all changes in one commit)
```

```bash
# Squash merge
git checkout main
git merge --squash feature
git commit -m "Add new model (squashed from 3 commits)"
```

**When to use squash:**
- Feature branch has messy commit history
- Want clean, linear history on main branch
- Following GitHub/GitLab PR workflows

**Downside**: Loses commit history from feature branch.

### Rebase (Alternative to Merge)

Instead of merging, you can rebase—replaying commits from one branch onto another:

```
Before rebase:
         main
          |
          v
A ← B ← C ← F ← G
         \
          D ← E ← feature

After git rebase main (from feature):
                      feature
                       |
                       v
A ← B ← C ← F ← G ← D' ← E'

Note: D and E are replayed as D' and E' (new commits)
```

```bash
# Rebase feature onto main
git checkout feature
git rebase main

# Alternative: rebase from main
git rebase main feature
```

**Rebase creates a linear history** (no merge commits), but rewrites commits.

**Golden Rule of Rebasing**: Never rebase commits that have been pushed to a shared branch. It rewrites history and causes problems for collaborators.

### Comparison: Merge vs. Rebase

| Aspect | Merge | Rebase |
|--------|-------|--------|
| History | Preserves complete history | Creates linear history |
| Commits | Creates merge commits | No merge commits |
| Conflicts | Resolved once | May need multiple resolutions |
| Safety | Safe for shared branches | Dangerous for shared branches |
| Traceability | Shows when features merged | Harder to trace feature integration |
| Use case | Shared branches, releases | Local cleanup, feature branches |

**For AI/ML projects**: Merge is generally safer and recommended for shared branches. Rebase is useful for cleaning up local commits before pushing.

---

## Resolving Merge Conflicts

### What Causes Conflicts?

A merge conflict occurs when the same part of a file was changed differently in both branches:

```
main branch:
  batch_size = 32

feature branch:
  batch_size = 64
```

Git can't automatically decide which value to keep, so it asks you.

### Conflict Markers

When a conflict occurs, Git adds markers to the file:

```python
def train_model():
<<<<<<< HEAD (current branch: main)
    batch_size = 32
=======
    batch_size = 64
>>>>>>> feature/new-config (incoming branch)

    model.train(batch_size=batch_size)
```

Breaking down the markers:
- `<<<<<<< HEAD`: Start of your current branch's version
- `=======`: Separator between versions
- `>>>>>>> branch-name`: End of the incoming branch's version

### Resolving Conflicts: Step-by-Step

#### Step 1: Attempt the merge

```bash
git checkout main
git merge feature/new-config
```

Output:
```
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Automatic merge failed; fix conflicts and then commit the result.
```

#### Step 2: Identify conflicting files

```bash
git status
```

Output:
```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   config.py
```

#### Step 3: Open the file and resolve

```python
# Original conflicted file:
def train_model():
<<<<<<< HEAD
    batch_size = 32
=======
    batch_size = 64
>>>>>>> feature/new-config

    model.train(batch_size=batch_size)

# After resolution (choose one, or create new solution):
def train_model():
    batch_size = 64  # Chose feature branch value

    model.train(batch_size=batch_size)
```

Remove the conflict markers completely.

#### Step 4: Mark as resolved

```bash
git add config.py
```

#### Step 5: Complete the merge

```bash
git commit
```

Git provides a default merge commit message:
```
Merge branch 'feature/new-config' into main

# Conflicts:
#   config.py
```

### Advanced Conflict Resolution

#### See what changed in each branch

```bash
# See your version (current branch)
git show :2:config.py

# See their version (incoming branch)
git show :3:config.py

# See common ancestor version
git show :1:config.py
```

#### Use merge tools

```bash
# Configure merge tool (one-time setup)
git config --global merge.tool vimdiff

# Launch merge tool
git mergetool
```

Popular merge tools:
- **vimdiff** (terminal-based)
- **meld** (GUI)
- **kdiff3** (GUI)
- **VS Code** (built-in)

#### Accept all changes from one side

```bash
# Keep all changes from current branch (ours)
git checkout --ours config.py
git add config.py

# Keep all changes from incoming branch (theirs)
git checkout --theirs config.py
git add config.py
```

#### Abort a problematic merge

```bash
# Undo the merge and return to pre-merge state
git merge --abort
```

### Preventing Conflicts

1. **Pull frequently**: Stay up-to-date with the main branch
2. **Communicate**: Coordinate who works on which files
3. **Small commits**: Easier to resolve conflicts in small chunks
4. **Rebase before merging**: Update feature branch with main before merge
5. **Use .gitattributes**: Define merge strategies for specific files

Example `.gitattributes`:
```
# Never merge these files, always keep ours
config/local.yaml merge=ours

# Binary files shouldn't be merged
*.pkl binary
*.h5 binary
```

---

## Git Workflows

### Feature Branch Workflow

The simplest workflow for teams:

```
main ← always deployable

feature/user-auth ← new feature branch
feature/api-v2    ← another feature branch
```

**Process**:
1. Create branch from `main` for each feature
2. Develop and commit on feature branch
3. Merge back to `main` when complete
4. Delete feature branch

```bash
# Start feature
git checkout main
git pull origin main
git checkout -b feature/add-caching

# Develop
git add .
git commit -m "Implement Redis caching layer"

# Finish feature
git checkout main
git pull origin main
git merge feature/add-caching
git push origin main
git branch -d feature/add-caching
```

**Best for**: Small teams, simple projects, continuous deployment.

### Git Flow

A more structured workflow with multiple branch types:

```
main ← production code, tagged releases
 |
develop ← integration branch
 |
 ├─ feature/* ← feature branches
 ├─ release/* ← release preparation
 └─ hotfix/*  ← emergency fixes
```

**Branch types**:

1. **main**: Production-ready code only
2. **develop**: Integration branch for features
3. **feature/***: New features (branch from `develop`)
4. **release/***: Release preparation (branch from `develop`)
5. **hotfix/***: Emergency production fixes (branch from `main`)

**Feature workflow**:
```bash
# Start feature
git checkout develop
git checkout -b feature/new-model

# Develop and commit
git add .
git commit -m "Add transformer model"

# Finish feature
git checkout develop
git merge --no-ff feature/new-model
git branch -d feature/new-model
git push origin develop
```

**Release workflow**:
```bash
# Start release
git checkout develop
git checkout -b release/1.2.0

# Final testing, bug fixes, version bumps
git commit -m "Bump version to 1.2.0"

# Finish release
git checkout main
git merge --no-ff release/1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git checkout develop
git merge --no-ff release/1.2.0
git branch -d release/1.2.0
```

**Hotfix workflow**:
```bash
# Start hotfix
git checkout main
git checkout -b hotfix/critical-bug

# Fix bug
git commit -m "Fix memory leak in inference"

# Finish hotfix
git checkout main
git merge --no-ff hotfix/critical-bug
git tag -a v1.2.1 -m "Hotfix: memory leak"
git checkout develop
git merge --no-ff hotfix/critical-bug
git branch -d hotfix/critical-bug
```

**Best for**: Scheduled releases, larger teams, versioned software.

### GitHub Flow

Simpler than Git Flow, optimized for continuous deployment:

```
main ← always deployable
 |
 ├─ feature/branch-1
 ├─ feature/branch-2
 └─ fix/branch-3
```

**Process**:
1. `main` branch is always deployable
2. Create descriptive branch from `main`
3. Commit regularly to your branch
4. Open Pull Request for discussion
5. Deploy from branch for testing (optional)
6. Merge to `main` after review
7. Deploy immediately from `main`

```bash
# Start feature
git checkout main
git pull origin main
git checkout -b improve-model-accuracy

# Develop
git add .
git commit -m "Implement ensemble model"
git push origin improve-model-accuracy

# Create Pull Request on GitHub
# After approval and CI passes:
git checkout main
git pull origin main
```

**Best for**: Web applications, continuous deployment, GitHub/GitLab projects.

### Trunk-Based Development

Single branch with very short-lived feature branches:

```
main ← trunk (everyone commits here frequently)
 |
 └─ tiny-feature (lives < 24 hours)
```

**Key principles**:
- Commit to `main` frequently (multiple times per day)
- Feature branches are extremely short-lived (hours, not days)
- Use feature flags for incomplete features
- Heavy reliance on automated testing

**Best for**: Highly experienced teams, strong CI/CD, feature flag infrastructure.

---

## Branch Management Best Practices

### Naming Conventions

Use descriptive, hierarchical branch names:

```bash
# Feature branches
feature/add-model-serving
feature/user-authentication
feature/ml-monitoring

# Bug fix branches
fix/memory-leak
fix/api-timeout
bugfix/training-crash

# Experimental branches
experiment/new-architecture
exp/hyperparameter-tuning

# Hotfix branches
hotfix/critical-security-issue
hotfix/production-crash

# Release branches
release/v1.2.0
release/2023-10-15
```

**Patterns**:
- Use `/` to create hierarchy
- Use `-` to separate words
- Be descriptive but concise
- Include ticket/issue numbers: `feature/MOD-123-add-caching`

### Branch Lifetime

**Short-lived branches** (hours to days):
- Feature branches in trunk-based development
- Bug fixes
- Small features

**Medium-lived branches** (days to weeks):
- Feature branches in feature-branch workflow
- Experiment branches

**Long-lived branches** (permanent):
- `main` / `master`
- `develop` (in Git Flow)
- Environment branches (staging, production)

**Rule of thumb**: The longer a branch lives, the harder it is to merge. Merge early and often.

### Keeping Branches Up-to-Date

```bash
# Update feature branch with changes from main
git checkout feature/my-feature
git fetch origin
git merge origin/main

# Or use rebase for cleaner history (if branch not shared)
git checkout feature/my-feature
git fetch origin
git rebase origin/main
```

Regular updates prevent massive, difficult merges later.

### Cleaning Up Branches

```bash
# List branches merged into main
git branch --merged main

# Delete all merged branches (be careful!)
git branch --merged main | grep -v "\*" | xargs -n 1 git branch -d

# Prune remote-tracking branches that no longer exist
git fetch --prune

# Or configure automatic pruning
git config --global fetch.prune true
```

---

## Branches in AI/ML Projects

### Experiment Branches

Track different ML experiments:

```bash
# Create experiment branches
git checkout -b experiment/resnet50-baseline
git checkout -b experiment/resnet50-dropout-05
git checkout -b experiment/vit-transformer
```

Each branch contains code for a specific experiment. Commit experiment results in the branch:

```bash
# experiment/resnet50-baseline
git add config.yaml results.json
git commit -m "Baseline: accuracy=0.87, loss=0.34"

# experiment/resnet50-dropout-05
git add config.yaml results.json
git commit -m "With dropout=0.5: accuracy=0.89, loss=0.31"
```

Compare experiments:
```bash
git diff experiment/resnet50-baseline experiment/resnet50-dropout-05 -- config.yaml
```

Merge winning experiment to main:
```bash
git checkout main
git merge experiment/resnet50-dropout-05
```

### Model Version Branches

Track different model versions in production:

```
main ← current development
 |
 ├─ model/v1.0 ← production model version 1.0
 ├─ model/v1.1 ← production model version 1.1
 └─ model/v2.0-beta ← next major version
```

### Environment-Specific Branches

**Not recommended** but sometimes used:

```
production ← production environment config
staging    ← staging environment config
develop    ← development environment config
```

**Better approach**: Use a single branch with environment-specific config files:
```
configs/
  ├── dev.yaml
  ├── staging.yaml
  └── prod.yaml
```

### Data Pipeline Branches

For data engineering work:

```bash
git checkout -b pipeline/add-feature-engineering
git checkout -b pipeline/optimize-preprocessing
git checkout -b pipeline/add-data-validation
```

---

## Common Issues and Troubleshooting

### Issue 1: Accidentally Committed to Wrong Branch

**Symptom**: Made commits on `main` instead of feature branch.

**Solution**:
```bash
# Create feature branch from current position
git branch feature/my-feature

# Reset main to origin (removes commits from main)
git reset --hard origin/main

# Switch to feature branch (has your commits)
git checkout feature/my-feature
```

### Issue 2: Need to Move Uncommitted Changes to Another Branch

**Symptom**: Started working on wrong branch.

**Solution**:
```bash
# Stash your changes
git stash

# Switch to correct branch
git checkout correct-branch

# Apply stashed changes
git stash pop
```

### Issue 3: Merge Conflict Too Complex

**Symptom**: Merge conflict is overwhelming.

**Solution**:
```bash
# Abort the merge
git merge --abort

# Try rebasing one commit at a time
git rebase -i origin/main

# Or ask for help from team member
```

### Issue 4: Deleted Branch with Unmerged Work

**Symptom**: Accidentally deleted a branch.

**Solution**:
```bash
# Find the deleted branch's last commit
git reflog

# Output:
# abc123 HEAD@{0}: checkout: moving from deleted-branch to main
# def456 HEAD@{1}: commit: My last commit on deleted-branch

# Recreate the branch
git branch recovered-branch def456
```

Git keeps deleted branches in reflog for ~30 days.

### Issue 5: Branch Diverged from Remote

**Symptom**: Can't push because branches have diverged.

**Solution**:
```bash
# See what's different
git fetch origin
git log HEAD..origin/main --oneline

# Option 1: Merge remote changes
git pull origin main

# Option 2: Rebase onto remote
git pull --rebase origin main

# Option 3: Force push (dangerous!)
git push --force-with-lease origin main
```

**Never force push to shared branches** unless team is coordinated.

---

## Summary and Key Takeaways

### Core Concepts

1. **Branches are lightweight**: Just 41-byte pointers to commits
2. **HEAD tracks current branch**: Shows where you are
3. **Three merge strategies**: Fast-forward, three-way, squash
4. **Rebase rewrites history**: Useful locally, dangerous remotely
5. **Conflicts are normal**: Learn to resolve them systematically

### Essential Commands Cheat Sheet

```bash
# Branch operations
git branch                    # List branches
git branch <name>            # Create branch
git switch <name>            # Switch to branch (new)
git switch -c <name>         # Create and switch (new)
git checkout <name>          # Switch to branch (old)
git checkout -b <name>       # Create and switch (old)
git branch -d <name>         # Delete merged branch
git branch -D <name>         # Force delete branch

# Merging
git merge <branch>           # Merge branch into current
git merge --no-ff <branch>   # Force merge commit
git merge --squash <branch>  # Squash merge
git merge --abort            # Abort merge

# Rebasing
git rebase <branch>          # Rebase onto branch
git rebase -i <commit>       # Interactive rebase

# Conflict resolution
git status                   # See conflicted files
git diff                     # See conflict details
git add <file>              # Mark as resolved
git merge --abort           # Abort merge
```

### Workflow Selection Guide

| Workflow | Team Size | Release Cadence | Complexity | Best For |
|----------|-----------|-----------------|------------|----------|
| Feature Branch | Small | Continuous | Low | Startups, web apps |
| Git Flow | Medium-Large | Scheduled | High | Versioned software, mobile apps |
| GitHub Flow | Any | Continuous | Medium | Web apps, SaaS, APIs |
| Trunk-Based | Large (experienced) | Continuous | Low | Mature teams, strong CI/CD |

### Best Practices

1. **Branch early, branch often**: Branches are cheap
2. **Keep branches short-lived**: Merge within days, not weeks
3. **Name branches descriptively**: `feature/add-user-auth`, not `feature1`
4. **Update branches regularly**: Merge or rebase from main frequently
5. **Delete merged branches**: Keep repository clean
6. **Never force push shared branches**: Coordination required
7. **Review before merging**: Use Pull Requests
8. **Write meaningful merge messages**: Explain why features were merged
9. **Use consistent workflow**: Team should agree on one workflow
10. **Automate testing**: CI/CD should test all branches

### For AI/ML Projects

- **Experiment tracking**: One branch per experiment, commit results
- **Model versioning**: Tag releases with model versions
- **Data pipeline isolation**: Separate branches for data engineering
- **Reproducibility**: Commit exact configs with code
- **A/B testing**: Use branches to manage different model versions

### What's Next

In the next lecture, we'll cover:
- Collaboration with Git (remote repositories, GitHub/GitLab)
- Pull Requests and code review
- Forking and contributing to open source
- Issues and project management
- CI/CD integration

### Further Reading

- Git branching model: https://nvie.com/posts/a-successful-git-branching-model/
- GitHub Flow: https://guides.github.com/introduction/flow/
- Trunk-Based Development: https://trunkbaseddevelopment.com/

---

**Practice Exercises**: Complete Exercise 03 and 04 to master branching and conflict resolution through hands-on scenarios.
