# Lecture 03: Collaboration with Git

## Table of Contents
1. [Introduction](#introduction)
2. [Remote Repositories](#remote-repositories)
3. [GitHub and GitLab Fundamentals](#github-and-gitlab-fundamentals)
4. [Cloning and Forking](#cloning-and-forking)
5. [Push and Pull Operations](#push-and-pull-operations)
6. [Pull Requests and Code Review](#pull-requests-and-code-review)
7. [Issues and Project Management](#issues-and-project-management)
8. [Collaborative Workflows](#collaborative-workflows)
9. [Team Collaboration Best Practices](#team-collaboration-best-practices)
10. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
11. [Summary and Key Takeaways](#summary-and-key-takeaways)

---

## Introduction

### Why Collaboration Tools Matter

You've mastered Git locally—committing, branching, and merging. But AI infrastructure is never a solo endeavor. You'll collaborate with:
- **Data scientists** who need your infrastructure for experiments
- **ML engineers** who deploy models using your pipelines
- **DevOps engineers** who manage production deployments
- **Other infrastructure engineers** on your team
- **Open source contributors** improving shared tools

Without proper collaboration workflows, chaos ensues:
- Conflicting changes overwrite each other
- Code reviews are impossible
- No one knows who changed what or why
- Deployments happen without approval
- Knowledge exists only in individuals' heads

This lecture transforms you from a solo Git user into an effective team collaborator.

### Learning Objectives

By the end of this lecture, you will:

- Understand remote repositories and how they enable collaboration
- Configure and manage remote connections
- Push your work to share with others and pull others' work
- Create and review Pull Requests (PRs) / Merge Requests (MRs)
- Implement effective code review practices for infrastructure
- Use issues for bug tracking and feature planning
- Contribute to open-source projects
- Apply GitHub Actions / GitLab CI for automation
- Protect critical branches with rules and policies
- Resolve collaboration conflicts systematically

### The AI Infrastructure Context

In AI infrastructure, collaboration involves:

**Code sharing:**
- Infrastructure as Code (Terraform, Kubernetes manifests)
- Training scripts and pipelines
- Model serving APIs
- Monitoring and logging configurations

**Knowledge sharing:**
- Architecture decisions
- Deployment procedures
- Troubleshooting guides
- Experiment results

**Quality control:**
- Peer code reviews
- Automated testing (CI/CD)
- Security scanning
- Performance benchmarking

**Project coordination:**
- Feature planning
- Bug tracking
- Release management
- On-call rotation

---

## Remote Repositories

### What is a Remote Repository?

A remote repository is a version of your project hosted on the internet or network. It's the shared copy that everyone synchronizes with.

```
Developer A's     Remote Repo        Developer B's
Local Repo        (GitHub)          Local Repo
    ↓                ↓                   ↓
  [Repo]  ←push→  [Repo]  ←pull→     [Repo]
           ←pull→          ←push→
```

Everyone pushes their changes to the remote and pulls others' changes from it.

### Common Remote Hosting Services

1. **GitHub** (most popular)
   - Free for public and private repos
   - Strong community and ecosystem
   - GitHub Actions for CI/CD
   - Best for open source

2. **GitLab** (strong CI/CD)
   - Self-hosted or cloud
   - Built-in CI/CD pipelines
   - DevOps-focused features
   - Popular in enterprises

3. **Bitbucket** (Atlassian ecosystem)
   - Integrates with Jira
   - Free for small teams
   - Good for enterprises using Atlassian tools

4. **Self-hosted** (full control)
   - GitLab CE (Community Edition)
   - Gitea (lightweight)
   - Custom solutions

For this course, we'll focus on GitHub, but concepts apply to all platforms.

### Viewing Remote Repositories

```bash
# List configured remotes
git remote

# Output:
# origin

# Show remote URLs
git remote -v

# Output:
# origin  https://github.com/user/repo.git (fetch)
# origin  https://github.com/user/repo.git (push)
```

The name `origin` is the default name for the remote you cloned from.

### Adding Remote Repositories

```bash
# Add a new remote
git remote add <name> <url>

# Example: add origin
git remote add origin https://github.com/user/ml-pipeline.git

# Add additional remote (e.g., for contributing to forks)
git remote add upstream https://github.com/original-owner/ml-pipeline.git
```

### Remote Naming Conventions

Common remote names:
- **origin**: Your main remote (your fork or the primary repo)
- **upstream**: The original repo (when you've forked)
- **production**: Production deployment remote
- **staging**: Staging environment remote

### Changing and Removing Remotes

```bash
# Change remote URL (e.g., switching from HTTPS to SSH)
git remote set-url origin git@github.com:user/repo.git

# Rename a remote
git remote rename old-name new-name

# Remove a remote
git remote remove origin

# Show detailed information about a remote
git remote show origin
```

### HTTPS vs SSH Authentication

**HTTPS** (simpler but requires credentials):
```bash
git remote add origin https://github.com/user/repo.git
# Prompts for username/password or token
```

**SSH** (more secure, no repeated authentication):
```bash
git remote add origin git@github.com:user/repo.git
# Uses SSH keys, no prompts after setup
```

Setting up SSH keys (one-time):
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

### Remote Branches

Remote branches are references to the state of branches in your remote repositories:

```bash
# List all branches (local and remote)
git branch -a

# Output:
# * main
#   feature/new-model
#   remotes/origin/main
#   remotes/origin/develop
#   remotes/origin/feature/api-v2
```

`remotes/origin/main` is a remote-tracking branch—a local reference to the remote branch.

---

## GitHub and GitLab Fundamentals

### Creating a Repository on GitHub

**Via Web Interface:**
1. Click "+" → "New repository"
2. Enter repository name: `ml-inference-api`
3. Choose public or private
4. Optionally add README, .gitignore, license
5. Click "Create repository"

**Connecting Local Repository:**
```bash
# If you have an existing local repository
git remote add origin https://github.com/user/ml-inference-api.git
git branch -M main
git push -u origin main
```

**Starting Fresh:**
```bash
# Clone the new (empty) repository
git clone https://github.com/user/ml-inference-api.git
cd ml-inference-api

# Add files
echo "# ML Inference API" > README.md
git add README.md
git commit -m "Initial commit"
git push origin main
```

### Repository Settings

Key settings to configure:

**General:**
- Repository name and description
- Default branch (main vs master)
- Features (Issues, Wiki, Projects)

**Collaborators:**
- Add team members with different permissions
- Permissions: Read, Write, Maintain, Admin

**Branches:**
- Branch protection rules
- Required status checks (CI/CD)
- Required reviews before merging
- Restrict who can push

**Secrets:**
- Store sensitive data for CI/CD
- API keys, credentials, tokens
- Encrypted and not visible after creation

### Understanding .github Directory

The `.github` directory holds GitHub-specific configurations:

```
.github/
├── workflows/              # GitHub Actions (CI/CD)
│   ├── test.yml
│   └── deploy.yml
├── ISSUE_TEMPLATE/         # Issue templates
│   ├── bug_report.md
│   └── feature_request.md
├── PULL_REQUEST_TEMPLATE.md  # PR template
├── CODEOWNERS              # Automatic PR reviewers
└── dependabot.yml          # Dependency updates
```

### GitHub vs GitLab: Key Differences

| Feature | GitHub | GitLab |
|---------|--------|--------|
| CI/CD | GitHub Actions | Built-in CI/CD (more mature) |
| Pull Requests | Pull Requests | Merge Requests |
| Hosting | Cloud (GitHub.com) | Cloud or self-hosted |
| Pricing | Free for public, limited for private | More free features |
| Integration | Broad ecosystem | DevOps-focused |
| Container Registry | GitHub Packages | Built-in Container Registry |
| Planning Tools | Projects, Issues | Issues, Boards, Epics |

Both are excellent—choice often depends on organizational preference.

---

## Cloning and Forking

### Cloning a Repository

Cloning creates a local copy of a remote repository:

```bash
# Clone via HTTPS
git clone https://github.com/user/ml-pipeline.git

# Clone via SSH
git clone git@github.com:user/ml-pipeline.git

# Clone into specific directory
git clone https://github.com/user/ml-pipeline.git my-pipeline

# Clone specific branch
git clone -b develop https://github.com/user/ml-pipeline.git

# Shallow clone (faster, less history)
git clone --depth 1 https://github.com/user/ml-pipeline.git
```

After cloning:
- Git automatically adds `origin` remote
- Sets up remote-tracking branches
- Checks out the default branch

### Forking a Repository

Forking creates your own copy of someone else's repository on GitHub:

```
Original Repo          Your Fork
(upstream)            (origin)
    |                     |
    |------ fork ------→ |
    |                     |
    ↓                     ↓
[github.com/owner/repo] [github.com/you/repo]
```

**When to fork:**
- Contributing to open-source projects
- Experimenting with someone else's code
- Creating your own version of a project

**Workflow:**
1. Click "Fork" on GitHub
2. Clone YOUR fork (not the original)
3. Add original as upstream remote
4. Work on your fork
5. Submit Pull Request to original

```bash
# Clone your fork
git clone https://github.com/YOU/ml-toolkit.git
cd ml-toolkit

# Add upstream remote (original repo)
git remote add upstream https://github.com/ORIGINAL-OWNER/ml-toolkit.git

# Verify remotes
git remote -v
# origin    https://github.com/YOU/ml-toolkit.git (fetch)
# origin    https://github.com/YOU/ml-toolkit.git (push)
# upstream  https://github.com/ORIGINAL-OWNER/ml-toolkit.git (fetch)
# upstream  https://github.com/ORIGINAL-OWNER/ml-toolkit.git (push)
```

### Syncing a Fork

Keep your fork up-to-date with the original:

```bash
# Fetch changes from upstream
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# Or rebase (cleaner history)
git rebase upstream/main

# Push updates to your fork
git push origin main
```

Automate this with GitHub's "Sync fork" button on the web interface.

---

## Push and Pull Operations

### Fetching Changes

Fetch downloads commits from remote but doesn't merge them:

```bash
# Fetch from default remote (origin)
git fetch

# Fetch from specific remote
git fetch upstream

# Fetch specific branch
git fetch origin main

# Fetch all remotes
git fetch --all

# Prune deleted remote branches
git fetch --prune
```

After fetching, remote-tracking branches are updated:
```bash
git log origin/main  # View remote commits
```

### Pulling Changes

Pull fetches AND merges in one command:

```bash
# Pull from tracked branch (default)
git pull

# Equivalent to:
git fetch origin
git merge origin/main

# Pull from specific remote and branch
git pull origin develop

# Pull with rebase instead of merge
git pull --rebase

# Pull all branches
git pull --all
```

**Pull with merge vs rebase:**

Merge (default):
```
Before pull:
  origin/main: A ← B ← C
  local main:  A ← B ← D

After git pull:
  main: A ← B ← C ← D ← M
               ↘_____↗
          (merge commit M)
```

Rebase:
```
Before pull:
  origin/main: A ← B ← C
  local main:  A ← B ← D

After git pull --rebase:
  main: A ← B ← C ← D'
          (D replayed on top of C)
```

### Pushing Changes

Push sends your commits to the remote:

```bash
# Push current branch to its remote tracking branch
git push

# Push to specific remote and branch
git push origin main

# Push and set upstream (first time)
git push -u origin feature/new-api

# After -u, just use:
git push

# Push all branches
git push --all

# Push tags
git push --tags

# Force push (dangerous!)
git push --force

# Safer force push (only if no one else pushed)
git push --force-with-lease
```

### Understanding Tracking Branches

When you clone a repository, branches automatically track remote branches:

```bash
# See tracking information
git branch -vv

# Output:
# * main    abc123 [origin/main] Latest commit message
#   feature def456 [origin/feature: ahead 2] Feature commit
```

`[origin/main]` means the local `main` branch tracks `origin/main`.

Set up tracking manually:
```bash
# Create local branch tracking remote branch
git checkout -b feature origin/feature

# Or set tracking for existing branch
git branch --set-upstream-to=origin/feature feature
```

### Push Rejection: Handling Non-Fast-Forward Updates

**Problem**: Someone pushed to the remote before you:

```bash
git push

# Output:
# ! [rejected]        main -> main (non-fast-forward)
# error: failed to push some refs to 'origin'
# hint: Updates were rejected because the tip of your current branch is behind
```

**Solution**:
```bash
# Option 1: Pull and merge
git pull origin main
# (resolve any conflicts)
git push origin main

# Option 2: Pull and rebase
git pull --rebase origin main
# (resolve any conflicts)
git push origin main

# Option 3: Force push (ONLY if you're sure!)
git push --force-with-lease origin main
```

**Never force push to shared branches** unless coordinated with the team.

---

## Pull Requests and Code Review

### What is a Pull Request?

A Pull Request (PR) on GitHub (Merge Request on GitLab) is a request to merge your branch into another branch. It enables:
- Code review before merging
- Discussion about changes
- Automated testing (CI/CD)
- Approval workflows
- Change documentation

### Creating a Pull Request

**Via GitHub Web Interface:**

1. Push your feature branch:
```bash
git checkout -b feature/add-caching
# make changes
git add .
git commit -m "Implement Redis caching"
git push -u origin feature/add-caching
```

2. Navigate to repository on GitHub
3. Click "Compare & pull request" button
4. Fill in PR details:
   - Title: "Add Redis caching layer"
   - Description: Explain what, why, and how
   - Reviewers: Select team members
   - Assignees: Who will merge the PR
   - Labels: bug, feature, documentation, etc.
   - Milestone: Release version
   - Projects: Link to project board

5. Click "Create pull request"

### Pull Request Template

Create `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description
<!-- Describe your changes in detail -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
<!-- Describe the tests you ran -->
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Related Issues
<!-- Link to related issues -->
Closes #123
```

### Code Review Best Practices

**For Authors (creating PR):**

1. **Keep PRs small**: 200-400 lines maximum, focus on one thing
2. **Write descriptive titles**: "Add Redis caching" not "Update code"
3. **Provide context**: Explain why, not just what
4. **Self-review first**: Read your own diff before requesting review
5. **Respond promptly**: Address feedback quickly
6. **Don't take it personally**: Reviews are about code quality

**For Reviewers:**

1. **Review promptly**: Within 24 hours
2. **Be constructive**: Suggest improvements, not just criticisms
3. **Explain your reasoning**: "This could cause X issue because Y"
4. **Distinguish**: Must-fix vs. nice-to-have vs. nit
5. **Approve generously**: Don't block on minor style issues
6. **Test locally**: For critical changes, pull and test

**Review Comments:**

```
❌ Bad: "This is wrong."
✅ Good: "This could lead to a race condition if two requests access
         the cache simultaneously. Consider using a lock here."

❌ Bad: "Why did you do this?"
✅ Good: "I'm curious about the reasoning for this approach. Have you
         considered using X instead? It might be more performant."

❌ Bad: "Nit: space"
✅ Good: "Nit (non-blocking): Extra space here. Our linter should
         catch this in CI."
```

### Reviewing AI/ML Infrastructure Code

Special considerations:

**Configuration changes:**
- Verify values are correct for environment
- Check for hardcoded secrets
- Ensure backward compatibility

**Performance:**
- Will this handle expected load?
- Any memory leaks or resource issues?
- Impact on inference latency?

**Reproducibility:**
- Are random seeds set?
- Dependencies versioned?
- Results reproducible?

**Testing:**
- Unit tests for logic
- Integration tests for pipelines
- Performance benchmarks

**Documentation:**
- API changes documented?
- README updated?
- Comments for complex logic?

### Handling Review Feedback

```bash
# Make requested changes
git checkout feature/add-caching
# edit files
git add .
git commit -m "Address review feedback: improve error handling"
git push origin feature/add-caching
```

The PR automatically updates with new commits.

### Merging Pull Requests

**Three merge strategies on GitHub:**

1. **Create a merge commit** (default)
   - Preserves all commits
   - Creates merge commit
   - Full history visible

2. **Squash and merge**
   - Combines all commits into one
   - Clean linear history
   - Loses individual commit history

3. **Rebase and merge**
   - Replays commits onto base branch
   - Linear history
   - No merge commit
   - Preserves individual commits

**Merge button workflow:**
```
1. Ensure CI passes (green checkmarks)
2. Ensure required reviews are approved
3. Resolve any merge conflicts
4. Click "Merge pull request"
5. Choose merge strategy
6. Confirm merge
7. Delete branch (optional but recommended)
```

### Branch Protection Rules

Protect critical branches (main, production) with rules:

**Settings → Branches → Branch protection rules:**

- ✅ Require pull request reviews before merging
  - Required approving reviews: 1-2
  - Dismiss stale reviews on new commits

- ✅ Require status checks to pass before merging
  - Tests must pass
  - Linting must pass
  - Security scans must pass

- ✅ Require branches to be up to date before merging
  - Forces merge of main before merging PR

- ✅ Require conversation resolution before merging
  - All review comments must be resolved

- ✅ Restrict who can push to matching branches
  - Only maintainers can push directly

- ✅ Require signed commits
  - All commits must be GPG signed

These rules enforce quality and prevent accidental damage.

---

## Issues and Project Management

### GitHub Issues

Issues track bugs, features, and tasks:

**Creating an issue:**
1. Navigate to "Issues" tab
2. Click "New issue"
3. Choose template (if available)
4. Fill in title and description
5. Add labels, assignees, milestone
6. Submit issue

### Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run training script with config '...'
2. Observe error '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python version: [e.g. 3.11]
 - GPU: [e.g. NVIDIA A100]
 - CUDA version: [e.g. 12.1]

**Additional context**
Add any other context about the problem here.
```

Feature request template (`.github/ISSUE_TEMPLATE/feature_request.md`):

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features.

**Additional context**
Any other context, screenshots, or examples.
```

### Linking Issues to Pull Requests

In PR description or commits:
```
Closes #123
Fixes #456
Resolves #789
Related to #321
```

When the PR is merged, these issues automatically close.

### Labels for ML Projects

Organize issues with labels:

**Type:**
- `bug` - Something broken
- `feature` - New functionality
- `enhancement` - Improve existing feature
- `documentation` - Documentation improvement

**Priority:**
- `critical` - Production down
- `high` - Important, blocks work
- `medium` - Should be done soon
- `low` - Nice to have

**Component:**
- `training` - Training pipeline issues
- `inference` - Model serving issues
- `data-pipeline` - Data processing
- `infrastructure` - IaC, Kubernetes
- `monitoring` - Logging, metrics
- `security` - Security vulnerabilities

**Status:**
- `in-progress` - Someone working on it
- `blocked` - Can't proceed
- `needs-review` - Awaiting feedback
- `wontfix` - Won't be addressed

### Projects and Milestones

**Projects**: Kanban boards for organizing issues
- Columns: Backlog, To Do, In Progress, In Review, Done
- Drag issues between columns
- Track sprint/release progress

**Milestones**: Group issues for releases
- `v1.0.0` - Initial release
- `v1.1.0` - First feature update
- `Q4 2024` - Quarterly goals

---

## Collaborative Workflows

### Workflow 1: Centralized (Simple Teams)

Everyone works on the same repository:

```
   Shared Repository (GitHub)
            |
    +-------+-------+
    |       |       |
  Dev A   Dev B   Dev C
```

Process:
1. Clone repository
2. Create feature branch
3. Push branch, create PR
4. Review, merge, delete branch

### Workflow 2: Forking (Open Source)

Contributors fork the main repository:

```
   Main Repository
   (original owner)
         |
    fork | fork | fork
    +----+----+----+
    |    |    |    |
 Fork  Fork  Fork  Fork
 (A)   (B)   (C)   (D)
```

Process:
1. Fork the repository
2. Clone your fork
3. Create feature branch
4. Push to your fork
5. Create PR from your fork to main repo
6. Maintainers review and merge

### Workflow 3: Shared Repository with Protected Main

Most common for teams:

```
     Main Repository
           |
        main (protected)
           |
    +------+------+
    |      |      |
feature  fix  enhance
 branch branch branch
```

Process:
1. Clone shared repository
2. Create feature branch from main
3. Commit to feature branch
4. Push feature branch
5. Create PR to main
6. CI/CD runs automatically
7. Reviews required
8. Merge after approval

### AI/ML Team Collaboration Patterns

**Experiment tracking:**
```
main
 ├── experiment/baseline-resnet
 ├── experiment/resnet-dropout
 ├── experiment/vit-transformer
 └── experiment/ensemble
```

Each team member runs experiments on separate branches, commits results, and the best one merges to main.

**Feature development:**
```
develop
 ├── feature/add-model-v2
 ├── feature/optimize-preprocessing
 └── feature/add-monitoring
```

**Environment separation:**
```
main (production)
 ├── staging (pre-prod testing)
 └── develop (integration)
```

---

## Team Collaboration Best Practices

### Communication

1. **Write clear commit messages**: Others need to understand your changes
2. **Document in PRs**: Explain context and reasoning
3. **Comment in issues**: Keep stakeholders informed
4. **Use discussions**: For design decisions and questions
5. **Update README**: Keep documentation current

### Code Standards

1. **Style guide**: Agree on code style (PEP 8 for Python)
2. **Linting**: Automate style checking (Black, Flake8)
3. **Testing**: Require tests for new features
4. **Documentation**: Document public APIs
5. **Type hints**: Use type annotations in Python

### Automation

1. **CI/CD**: Automated testing on every PR
2. **Pre-commit hooks**: Catch issues before commit
3. **Dependency updates**: Dependabot for security
4. **Code scanning**: Security vulnerability detection
5. **Performance benchmarks**: Catch performance regressions

### Security

1. **Never commit secrets**: Use environment variables
2. **Use GitHub Secrets**: For CI/CD credentials
3. **Review dependencies**: Check for vulnerabilities
4. **Sign commits**: GPG signature verification
5. **Two-factor auth**: Required for all team members

### Onboarding New Team Members

1. **CONTRIBUTING.md**: Document contribution process
2. **CODE_OF_CONDUCT.md**: Set community standards
3. **Good first issues**: Label easy issues for newcomers
4. **Mentorship**: Pair new members with experienced ones
5. **Documentation**: Maintain up-to-date setup guides

---

## Common Issues and Troubleshooting

### Issue 1: Merge Conflicts in Pull Request

**Symptom**: PR shows conflicts with base branch.

**Solution**:
```bash
# Update feature branch with main
git checkout feature/my-feature
git fetch origin
git merge origin/main
# Resolve conflicts
git add .
git commit
git push origin feature/my-feature
```

The PR automatically updates and conflicts are resolved.

### Issue 2: Accidentally Pushed Secrets

**Symptom**: API key or password committed and pushed.

**Immediate action**:
1. Rotate the compromised secret immediately
2. Remove from repository history (use BFG Repo-Cleaner)
3. Add to .gitignore
4. Educate team on proper secret management

### Issue 3: Can't Push to Remote

**Symptom**: Permission denied when pushing.

**Causes and solutions**:
```bash
# Wrong remote URL
git remote -v
git remote set-url origin <correct-url>

# SSH key issues
ssh -T git@github.com  # Test SSH connection
# Add SSH key to GitHub if not set up

# No write permissions
# Ask repository owner to add you as collaborator
```

### Issue 4: Diverged Branches

**Symptom**: Local and remote branches have diverged.

**Solution**:
```bash
# See differences
git fetch origin
git log --oneline --graph --all

# Option 1: Merge remote changes
git pull origin main

# Option 2: Rebase onto remote
git pull --rebase origin main

# Option 3: Reset to remote (discards local commits)
git reset --hard origin/main
```

### Issue 5: Pull Request Too Large

**Symptom**: PR with 1000+ lines, hard to review.

**Solution**:
```bash
# Split into multiple PRs
git checkout main
git checkout -b feature/part1
# Cherry-pick relevant commits
git cherry-pick abc123 def456
git push origin feature/part1
# Create PR for part 1

# Repeat for other parts
```

### Issue 6: Outdated Fork

**Symptom**: Fork is behind upstream by many commits.

**Solution**:
```bash
# Sync fork
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

Or use GitHub's "Sync fork" button.

---

## Summary and Key Takeaways

### Core Concepts

1. **Remote repositories**: Shared copies on GitHub/GitLab
2. **Clone vs Fork**: Clone for collaboration, fork for contribution
3. **Fetch vs Pull**: Fetch downloads, pull downloads + merges
4. **Pull Requests**: Enable code review before merging
5. **Issues**: Track bugs and features
6. **Protection rules**: Enforce quality standards

### Essential Commands Cheat Sheet

```bash
# Remotes
git remote add <name> <url>     # Add remote
git remote -v                   # List remotes
git remote show origin          # Show remote info

# Fetching and pulling
git fetch origin                # Fetch from origin
git pull origin main            # Fetch and merge
git pull --rebase origin main   # Fetch and rebase

# Pushing
git push origin main            # Push to remote
git push -u origin feature      # Push and set upstream
git push --force-with-lease     # Safe force push

# Cloning and forking
git clone <url>                 # Clone repository
git remote add upstream <url>   # Add upstream (for forks)
```

### Pull Request Workflow

```
1. Create feature branch
2. Make commits
3. Push branch to remote
4. Create Pull Request
5. Address review feedback
6. CI/CD passes
7. Approval received
8. Merge PR
9. Delete feature branch
```

### Best Practices

1. **Small, frequent PRs**: Easier to review, faster to merge
2. **Descriptive PR titles**: Explain what changed
3. **Comprehensive PR descriptions**: Explain why changed
4. **Self-review first**: Catch issues before reviewers
5. **Respond to feedback promptly**: Keep PRs moving
6. **Sync regularly**: Pull from main frequently
7. **Protect main branch**: Require reviews and passing tests
8. **Use issue templates**: Standardize bug reports and feature requests
9. **Link PRs to issues**: Automatic tracking and closure
10. **Clean up branches**: Delete after merging

### For AI/ML Teams

- **Experiment branches**: Track experiments separately
- **Model versioning**: Tag releases with model versions
- **Data privacy**: Never commit real data to public repos
- **Reproducibility**: Document exact dependencies and seeds
- **Performance testing**: Benchmark inference latency in CI/CD
- **A/B testing**: Use branches for competing model versions

### What's Next

In the next lecture, we'll cover:
- Advanced Git techniques (rebase, cherry-pick, stash)
- Git hooks for automation
- Submodules for managing dependencies
- Git strategies for ML-specific challenges
- Advanced troubleshooting

### Further Reading

- GitHub Docs: https://docs.github.com/
- GitLab Docs: https://docs.gitlab.com/
- Pro Git book (Chapters 5-6): https://git-scm.com/book/en/v2
- GitHub Flow guide: https://guides.github.com/introduction/flow/

---

**Practice Exercises**: Complete Exercise 05 to practice collaborative workflows through realistic team scenarios.
