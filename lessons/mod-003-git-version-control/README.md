# Module 003: Git and Version Control

## Module Overview

Version control is the cornerstone of modern software development and infrastructure engineering. This module provides comprehensive training in Git, the industry-standard distributed version control system, and GitHub, the leading platform for collaboration and code hosting.

You'll learn not just how to use Git commands, but understand the underlying concepts that make Git powerful. You'll practice collaborative workflows, learn best practices for commit management, branching strategies, and how to handle complex scenarios that arise in real-world projects. These skills are essential for managing infrastructure as code, collaborating with teams, and maintaining professional development standards.

By the end of this module, you'll be confident using Git for daily work, contributing to team projects, and managing code effectively throughout its lifecycle.

## Learning Objectives

By completing this module, you will be able to:

1. **Understand version control concepts** and why they matter for infrastructure engineering
2. **Use fundamental Git commands** for tracking changes and managing repositories
3. **Create effective commits** with clear messages following industry standards
4. **Work with branches** to develop features and fix bugs in isolation
5. **Collaborate using GitHub** including pull requests, code reviews, and issues
6. **Resolve merge conflicts** confidently and understand their causes
7. **Use advanced Git features** like rebasing, stashing, and cherry-picking
8. **Follow Git workflows** appropriate for team collaboration (Git Flow, GitHub Flow)
9. **Manage repositories** including remotes, tags, and releases
10. **Apply Git best practices** for infrastructure as code projects

## Prerequisites

- Completion of Module 002 (Linux Essentials) recommended
- Comfort with command-line interfaces
- Basic understanding of file systems and text files
- GitHub account (free tier is sufficient)

**Recommended Setup:**
- Git 2.30+ installed on your system
- Text editor or IDE with Git integration (VS Code recommended)
- GitHub account with SSH keys configured
- Terminal access (native Linux, macOS, WSL2, or Git Bash on Windows)

## Time Commitment

- **Total Estimated Time:** 35-45 hours
- **Lectures & Reading:** 12-15 hours
- **Hands-on Exercises:** 18-22 hours
- **Projects & Collaboration:** 5-8 hours

**Recommended Pace:**
- Part-time (5-10 hrs/week): 4-5 weeks
- Full-time (20-30 hrs/week): 2 weeks

Git mastery comes from practice. Expect to spend time experimenting, making mistakes safely, and building muscle memory for common workflows.

## Module Structure

### Week 1: Git Fundamentals
- **Topics:** Version control concepts, basic commands, commit workflow
- **Key Skills:** init, clone, add, commit, status, log, diff
- **Practice:** Creating repositories, making commits, viewing history

### Week 2: Branching and Merging
- **Topics:** Branch management, merging strategies, conflict resolution
- **Key Skills:** branch, checkout, merge, rebase, conflict resolution
- **Practice:** Feature branches, merge scenarios, conflict handling

### Week 3: Collaboration with GitHub
- **Topics:** Remote repositories, pull requests, code review, issues
- **Key Skills:** push, pull, fetch, pull requests, forking workflow
- **Practice:** Contributing to projects, code review, team collaboration

### Week 4: Advanced Techniques
- **Topics:** Advanced commands, workflows, troubleshooting, best practices
- **Key Skills:** stash, cherry-pick, reset, revert, hooks, submodules
- **Practice:** Complex scenarios, recovery techniques, automation

## Detailed Topic Breakdown

### 1. Introduction to Version Control (4-5 hours)

#### 1.1 Why Version Control Matters
- History of version control systems
- Benefits of version control for infrastructure
- Distributed vs centralized version control
- Git vs other VCS (SVN, Mercurial)
- Use cases in AI/ML infrastructure

#### 1.2 Git Fundamentals
- Git architecture and object model
- The three states: working directory, staging area, repository
- Understanding commits and the commit graph
- SHA-1 hashes and object storage
- Understanding HEAD and references

#### 1.3 Installing and Configuring Git
- Installation across platforms
- Initial configuration (user.name, user.email)
- Git configuration levels (system, global, local)
- Useful configuration options
- Setting up SSH keys for GitHub
- Credential management

#### 1.4 Getting Help
- Git documentation structure
- Using `git help` command
- Understanding man pages
- Online resources and communities
- Reading Git documentation effectively

### 2. Basic Git Operations (6-8 hours)

#### 2.1 Creating and Cloning Repositories
- Initializing new repositories (`git init`)
- Cloning existing repositories (`git clone`)
- Understanding .git directory structure
- Repository structure and conventions
- README, .gitignore, and LICENSE files

#### 2.2 Tracking Changes
- Checking repository status (`git status`)
- Adding files to staging area (`git add`)
- Understanding staging strategies
- Removing and moving files
- Viewing differences (`git diff`)
- Ignoring files with .gitignore
- Global and local ignore patterns

#### 2.3 Committing Changes
- Creating commits (`git commit`)
- Writing effective commit messages
- Commit message conventions
- Amending commits
- Understanding commit best practices
- Atomic commits
- When to commit and how often

#### 2.4 Viewing History
- Viewing commit history (`git log`)
- Formatting log output
- Filtering history
- Viewing specific commits (`git show`)
- Searching commit history
- Understanding ancestry references (HEAD^, HEAD~2)
- Graphical log visualization

#### 2.5 Undoing Changes
- Discarding working directory changes
- Unstaging files
- Modifying commits
- Understanding destructive vs non-destructive operations
- Reverting commits (`git revert`)
- Resetting commits (`git reset`)
- Safety considerations

### 3. Branching and Merging (8-10 hours)

#### 3.1 Understanding Branches
- What branches are and why they matter
- Branch as a pointer to commits
- Creating branches (`git branch`)
- Switching branches (`git checkout`, `git switch`)
- Listing and managing branches
- Branch naming conventions
- Remote tracking branches

#### 3.2 Branching Strategies
- Feature branches
- Release branches
- Hotfix branches
- Git Flow workflow
- GitHub Flow workflow
- Trunk-based development
- Choosing the right strategy

#### 3.3 Merging Branches
- Fast-forward merges
- Three-way merges
- Merge commits
- Merge strategies and options
- Understanding merge parents
- When to merge vs rebase
- Merge best practices

#### 3.4 Resolving Conflicts
- Understanding why conflicts occur
- Conflict markers and structure
- Manual conflict resolution
- Using merge tools
- Aborting and restarting merges
- Preventing conflicts
- Testing after resolution

#### 3.5 Rebasing
- What is rebasing?
- Interactive rebase
- Rebase vs merge comparison
- When to use rebase
- Dangers of rebasing published history
- Rebase best practices
- Resolving rebase conflicts

### 4. Remote Repositories and GitHub (8-10 hours)

#### 4.1 Understanding Remotes
- What are remote repositories?
- Adding remotes (`git remote`)
- Viewing remote information
- Multiple remotes
- Remote naming conventions (origin, upstream)
- Remote URLs (HTTPS vs SSH)

#### 4.2 Pushing and Pulling
- Pushing changes (`git push`)
- Fetching changes (`git fetch`)
- Pulling changes (`git pull`)
- Understanding fetch vs pull
- Tracking branches
- Push and pull options
- Force pushing (when and why not to)

#### 4.3 GitHub Fundamentals
- Creating GitHub repositories
- Repository settings and options
- README and repository documentation
- GitHub UI navigation
- Repository visibility (public vs private)
- GitHub pricing and plans
- GitHub features overview

#### 4.4 Collaboration Workflows
- Forking repositories
- Cloning vs forking
- Upstream and origin conventions
- Keeping forks synchronized
- Direct collaboration
- Organization repositories
- Access control and permissions

#### 4.5 Pull Requests
- Creating pull requests
- Pull request descriptions
- Linking issues
- Requesting reviews
- Pull request workflow
- Draft pull requests
- Pull request templates
- Converting issues to PRs

#### 4.6 Code Review
- Code review best practices
- Commenting on code
- Suggesting changes
- Approving and requesting changes
- Review etiquette
- Responding to feedback
- Iterating on pull requests

#### 4.7 Issues and Project Management
- Creating and managing issues
- Issue templates
- Labels and milestones
- Assigning issues
- Issue references and linking
- Projects and boards
- GitHub Actions introduction

### 5. Advanced Git Techniques (6-8 hours)

#### 5.1 Stashing Changes
- What is the stash?
- Stashing uncommitted changes
- Applying stashed changes
- Managing multiple stashes
- Stash options and variations
- When to use stash
- Stash vs commit

#### 5.2 Tagging and Releases
- Annotated vs lightweight tags
- Creating tags
- Pushing tags
- Semantic versioning
- GitHub releases
- Release notes
- Versioning strategies

#### 5.3 Cherry-Picking
- What is cherry-picking?
- Selecting specific commits
- Cherry-pick use cases
- Potential issues
- Cherry-pick vs merge
- When to cherry-pick
- Maintaining commit history

#### 5.4 Advanced History Manipulation
- Interactive rebase workflows
- Squashing commits
- Splitting commits
- Reordering commits
- Editing commit messages
- Fixing old commits
- History rewriting considerations

#### 5.5 Git Hooks
- Client-side hooks
- Server-side hooks
- Pre-commit hooks
- Pre-push hooks
- Commit message hooks
- Hook use cases
- Sharing hooks with team

#### 5.6 Submodules and Subtrees
- Managing dependencies with submodules
- Working with submodules
- Submodule pitfalls
- Git subtrees as alternative
- Monorepo vs multirepo
- Best practices for dependencies

#### 5.7 Advanced Troubleshooting
- Finding bugs with git bisect
- Recovering lost commits with reflog
- Finding who changed what with blame
- Searching code history
- Recovering deleted branches
- Dealing with detached HEAD
- Common problems and solutions

### 6. Git Best Practices for Infrastructure (4-5 hours)

#### 6.1 Infrastructure as Code with Git
- Why IaC belongs in version control
- Repository structure for infrastructure
- Branching strategies for infrastructure
- Environment-specific branches
- Terraform/CloudFormation in Git
- Secrets management considerations
- Configuration management

#### 6.2 Commit Hygiene
- Atomic commits principle
- Commit message standards (Conventional Commits)
- What to include in commits
- What not to commit (secrets, binaries, dependencies)
- Commit frequency
- Keeping commits focused
- Pre-commit validation

#### 6.3 Branch Management
- Long-lived vs short-lived branches
- Branch cleanup strategies
- Protected branches
- Branch policies
- Naming conventions
- When to delete branches
- Branch lifecycle

#### 6.4 Collaboration Best Practices
- Pull request guidelines
- Code review standards
- Handling feedback professionally
- Documentation in PRs
- Testing requirements
- Continuous integration integration
- Team agreements

#### 6.5 Security Considerations
- Avoiding committed secrets
- Using .gitignore effectively
- Removing sensitive data from history
- GitHub security features
- Dependency scanning
- Code scanning
- Secret scanning

#### 6.6 Performance and Maintenance
- Repository size management
- Large file handling (Git LFS)
- Keeping clean history
- Garbage collection
- Shallow clones
- Partial clones
- Archive strategies

## Lecture Outline

> **Note:** Full lecture materials are currently in development. Placeholder files are available in the `lecture-notes/` directory. Complete lecture notes will be added in upcoming updates.

### Lecture 1: Introduction to Version Control and Git (90 min)
- Why version control?
- Git history and design philosophy
- Git architecture and object model
- Installation and configuration
- First repository
- **Lab:** Setting up Git and GitHub

### Lecture 2: Basic Git Workflow (90 min)
- Working directory, staging, repository
- Making commits
- Viewing history
- Understanding diffs
- Undoing changes
- **Lab:** Complete commit workflow practice

### Lecture 3: Branching Fundamentals (90 min)
- Branch concepts and theory
- Creating and switching branches
- Merging basics
- Fast-forward vs three-way merges
- Branch visualization
- **Lab:** Feature branch workflow

### Lecture 4: Conflict Resolution (90 min)
- Why conflicts happen
- Conflict markers and structure
- Resolution strategies
- Using merge tools
- Testing after resolution
- Prevention strategies
- **Lab:** Resolving merge conflicts

### Lecture 5: Remote Repositories and GitHub (120 min)
- Remote repository concepts
- Pushing and pulling
- GitHub fundamentals
- Forking vs cloning
- Collaboration models
- **Lab:** Contributing to a project

### Lecture 6: Pull Requests and Code Review (90 min)
- Pull request workflow
- Writing effective PR descriptions
- Code review best practices
- Iteration and feedback
- Merging strategies
- **Lab:** Complete PR workflow

### Lecture 7: Advanced Git Techniques (120 min)
- Rebasing deep dive
- Stashing changes
- Cherry-picking commits
- Interactive rebase
- Git hooks introduction
- **Lab:** Advanced workflow scenarios

### Lecture 8: Git for Infrastructure as Code (90 min)
- IaC version control patterns
- Repository organization
- Branch strategies for infrastructure
- Secrets management
- CI/CD integration
- Best practices
- **Lab:** Infrastructure repository setup

## Hands-On Exercises

> **Note:** Detailed exercise instructions are being developed. Placeholder files are available in the `exercises/` directory. Complete exercises will be added in upcoming updates.

### Exercise Categories

#### Basic Operations (10 exercises)
1. Repository initialization and first commits
2. Commit message practice
3. Viewing and interpreting history
4. Working with .gitignore
5. Staging strategies
6. Undoing changes safely
7. Amending commits
8. Searching history
9. Using git diff effectively
10. Basic workflow integration

#### Branching and Merging (10 exercises)
11. Creating feature branches
12. Merge workflow practice
13. Resolving simple conflicts
14. Resolving complex conflicts
15. Fast-forward merges
16. Three-way merge scenarios
17. Rebase practice
18. Interactive rebase exercises
19. Branch management
20. Merge strategy selection

#### GitHub and Collaboration (10 exercises)
21. Setting up GitHub repository
22. Push and pull operations
23. Forking workflow
24. Creating pull requests
25. Code review practice
26. Issue management
27. Linking PRs and issues
28. Synchronizing forks
29. Managing multiple remotes
30. Collaborative project

#### Advanced Techniques (10 exercises)
31. Stashing and applying changes
32. Cherry-picking commits
33. Tagging releases
34. Using git bisect
35. Recovering with reflog
36. Git hooks implementation
37. History rewriting scenarios
38. Submodule basics
39. Advanced troubleshooting
40. Complete workflow scenarios

## Assessment and Evaluation

### Knowledge Checks
- Quiz after each major section (6 quizzes total)
- Command understanding questions
- Workflow scenario analysis
- Best practices evaluation
- Troubleshooting scenarios

### Practical Assessments
- **Command Proficiency:** Demonstrate Git commands without reference
- **Workflow Completion:** Execute complete feature development workflow
- **Conflict Resolution:** Resolve 10 different conflict scenarios
- **Collaboration:** Complete full PR cycle as author and reviewer
- **Repository Management:** Set up and maintain a project repository

### Competency Criteria
To complete this module successfully, you should be able to:
- Create and manage Git repositories confidently
- Make atomic commits with clear messages
- Use branches effectively for feature development
- Merge branches and resolve conflicts independently
- Collaborate using pull requests and code review
- Use advanced Git features when needed
- Follow best practices for infrastructure as code
- Troubleshoot common Git issues
- Explain Git concepts to others

### Portfolio Project
**Infrastructure Repository Setup:**
Create a complete infrastructure repository demonstrating:
- Proper repository structure
- Terraform or similar IaC code
- Effective branching strategy
- Pull request workflow
- Documentation standards
- CI/CD integration
- Security best practices

This project showcases your Git and IaC knowledge combined.

## Resources and References

> **Note:** See `resources/recommended-reading.md` for a comprehensive list of learning materials, books, and online resources.

### Essential Resources
- Official Git documentation (git-scm.com)
- GitHub Guides (guides.github.com)
- Pro Git Book (free online)
- Git reference manual (`man git`)

### Recommended Books
- "Pro Git" by Scott Chacon and Ben Straub (free online)
- "Git Pocket Guide" by Richard E. Silverman
- "Version Control with Git" by Jon Loeliger and Matthew McCullough

### Online Learning
- GitHub Learning Lab
- Learn Git Branching (interactive visualizations)
- Git Immersion (hands-on tutorial)
- Atlassian Git Tutorials
- Oh Shit, Git!?! (common problems and solutions)

### Tools and Extensions
- GitKraken (graphical Git client)
- Git Graph (VS Code extension)
- Hub CLI (GitHub command-line interface)
- GitHub CLI (`gh` command)
- tig (text-mode Git interface)

### Practice Platforms
- GitHub (free public repositories)
- GitLab (alternative platform)
- Bitbucket (alternative platform)
- Learn Git Branching (browser-based practice)

## Getting Started

### Step 1: Install and Configure Git
1. Install Git for your platform
2. Configure user name and email
3. Set up SSH keys for GitHub
4. Test GitHub connection
5. Configure useful aliases

### Step 2: Create GitHub Account
1. Sign up for free GitHub account
2. Complete profile
3. Add SSH keys
4. Enable two-factor authentication
5. Explore GitHub interface

### Step 3: Begin with Lecture 1
- Read introduction to version control
- Understand Git architecture
- Complete setup lab
- Create your first repository

### Step 4: Practice Regularly
- Work through exercises sequentially
- Experiment with commands
- Make mistakes safely
- Build muscle memory
- Use Git for personal projects

### Step 5: Collaborate
- Find open-source projects
- Contribute small fixes
- Practice pull request workflow
- Engage in code review
- Build collaboration skills

## Tips for Success

1. **Practice Daily:** Use Git for all your code, even personal projects
2. **Visualize:** Use graphical tools to understand commit graphs
3. **Experiment Safely:** Create practice repositories to try new commands
4. **Read Commit Messages:** Study good commit messages in popular projects
5. **Use Aliases:** Create shortcuts for frequently used commands
6. **Learn from Mistakes:** Git makes it hard to lose data permanently
7. **Follow Conventions:** Adopt standard commit message formats early
8. **Collaborate:** Working with others accelerates learning
9. **Read Documentation:** Git documentation is comprehensive and well-written
10. **Build a Workflow:** Develop consistent personal workflows

## Common Pitfalls and Solutions

### Pitfall 1: Committing Too Much/Too Little
**Solution:** Practice atomic commits; each commit should represent one logical change

### Pitfall 2: Vague Commit Messages
**Solution:** Use Conventional Commits format; explain "why" not just "what"

### Pitfall 3: Working on Wrong Branch
**Solution:** Check branch before starting work; use `git status` frequently

### Pitfall 4: Fear of Merge Conflicts
**Solution:** Conflicts are normal; practice resolving them in safe environment

### Pitfall 5: Force Pushing to Shared Branches
**Solution:** Never force push to main/master; understand rebase implications

### Pitfall 6: Committing Secrets
**Solution:** Use .gitignore properly; scan before committing; use pre-commit hooks

### Pitfall 7: Large Binary Files
**Solution:** Use Git LFS; keep binaries out when possible; use .gitignore

### Pitfall 8: Detached HEAD State
**Solution:** Understand what HEAD means; create branch if making changes

## Troubleshooting Guide

### Problem: Merge Conflict
```bash
# Steps to resolve
git status  # Identify conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git commit  # Complete the merge
```

### Problem: Committed to Wrong Branch
```bash
# Solution using cherry-pick
git checkout correct-branch
git cherry-pick <commit-hash>
git checkout wrong-branch
git reset --hard HEAD~1  # Remove from wrong branch
```

### Problem: Need to Undo Last Commit
```bash
# Keep changes
git reset --soft HEAD~1

# Discard changes
git reset --hard HEAD~1
```

### Problem: Lost Commits
```bash
# Find lost commits
git reflog

# Recover specific commit
git checkout <commit-hash>
git checkout -b recovery-branch
```

## Next Steps

After completing this module, you'll be ready to:
- **Module 004:** Python for Infrastructure (use Git for all code)
- **Module 005:** Docker and Containers (version control for Dockerfiles)
- **All Future Modules:** Git is used throughout the curriculum

You'll also be prepared to:
- Contribute to open-source projects
- Collaborate professionally on team projects
- Manage infrastructure as code effectively
- Build a portfolio of public repositories

## Development Status

**Current Status:** Template phase - comprehensive structure in place

**Available Now:**
- Complete module structure
- Detailed topic breakdown
- Lecture outline
- Exercise framework
- Assessment criteria

**In Development:**
- Full lecture notes with diagrams
- Step-by-step exercise instructions
- Interactive tutorials
- Video demonstrations
- Practice repositories
- Solution guides

**Planned Updates:**
- GitHub Actions integration
- Advanced workflow patterns
- Team collaboration scenarios
- Git at scale techniques
- Troubleshooting cookbook

## Feedback and Contributions

This module is continuously being improved. Contributions welcome:
- Report issues or suggest improvements
- Share your learning experience
- Contribute example repositories
- Suggest additional resources
- Help improve documentation

---

**Module Maintainer:** AI Infrastructure Curriculum Team
**Contact:** ai-infra-curriculum@joshua-ferguson.com
**Last Updated:** 2025-10-18
**Version:** 1.0.0-template
