# Module 003: Git & Version Control - Comprehensive Quiz

## Instructions

This quiz covers all topics from Module 003: Git & Version Control. It includes 30 questions covering:
- Git fundamentals and basics
- Branching and merging
- Collaboration workflows
- Advanced Git techniques
- ML-specific workflows with DVC and Git LFS

**Scoring:**
- Each question is worth 1 point
- Total: 30 points
- Passing score: 24/30 (80%)

**Time Estimate:** 45-60 minutes

Answer all questions, then check your answers at the end.

---

## Section 1: Git Fundamentals (Questions 1-8)

### Question 1: Git Basics
What is the purpose of the staging area in Git?

A) To store committed changes
B) To temporarily hold changes before committing
C) To store remote repository information
D) To cache file contents for faster access

**Answer:** B

**Explanation:** The staging area (also called "index") is an intermediate area where you prepare changes before committing them. It allows you to selectively choose which changes to include in the next commit using `git add`.

---

### Question 2: Commit Identification
What uniquely identifies each Git commit?

A) Commit message
B) Timestamp
C) SHA-1 hash
D) Author name

**Answer:** C

**Explanation:** Each Git commit is uniquely identified by a SHA-1 hash (40-character hexadecimal string). This hash is calculated from the commit content, parent commits, author, timestamp, and message, ensuring uniqueness.

---

### Question 3: Git Workflow
In the three-state Git workflow, what are the three areas?

A) Remote, Local, Cache
B) Working Directory, Staging Area, Repository
C) Edit, Add, Commit
D) Create, Modify, Delete

**Answer:** B

**Explanation:** Git has three main areas: Working Directory (where you edit files), Staging Area/Index (where you prepare commits), and Repository (where commits are stored). Files move through these areas as you work with Git.

---

### Question 4: .gitignore
You accidentally committed a 5GB model file to Git. What should you have done to prevent this?

A) Use a smaller model
B) Compress the file first
C) Add the file pattern to .gitignore before committing
D) Commit it to a separate branch

**Answer:** C

**Explanation:** Files matching patterns in `.gitignore` are never tracked by Git. For ML projects, you should add patterns like `*.h5`, `*.pth`, `models/`, and `data/` to `.gitignore`, then use Git LFS or DVC for large files instead.

---

### Question 5: Viewing Changes
What's the difference between `git diff` and `git diff --staged`?

A) No difference, they're the same
B) `git diff` shows unstaged changes, `git diff --staged` shows staged changes
C) `git diff` shows local changes, `git diff --staged` shows remote changes
D) `git diff --staged` is faster

**Answer:** B

**Explanation:** `git diff` shows changes in the working directory that haven't been staged yet. `git diff --staged` (or `--cached`) shows changes that have been staged and will be included in the next commit.

---

### Question 6: Commit Messages
Which commit message follows conventional commit best practices?

A) "fixed bug"
B) "Updated files"
C) "fix(preprocessing): handle grayscale images correctly"
D) "Changes to preprocessing module"

**Answer:** C

**Explanation:** Conventional commits use the format `type(scope): subject`. The type (feat, fix, docs, etc.) categorizes the change, scope specifies what area, and subject describes the change. This enables automation and clear history.

---

### Question 7: Git Log
Which command shows the last 5 commits in compact one-line format?

A) `git log -5`
B) `git log --oneline -5`
C) `git show -5`
D) `git log --short -5`

**Answer:** B

**Explanation:** `git log --oneline` shows commits in compact format (first 7 characters of hash + message). Adding `-5` limits output to the last 5 commits. This is useful for quickly scanning recent history.

---

### Question 8: Undoing Changes
You staged a file by mistake. How do you unstage it without losing the changes?

A) `git reset --hard <file>`
B) `git checkout <file>`
C) `git restore --staged <file>`
D) `git rm --cached <file>`

**Answer:** C

**Explanation:** `git restore --staged <file>` (or the older `git reset HEAD <file>`) unstages a file while keeping changes in the working directory. `--hard` would discard changes, `checkout` might discard changes, and `rm --cached` is for removing from tracking.

---

## Section 2: Branching and Merging (Questions 9-16)

### Question 9: Branch Creation
What's the shortcut to create AND switch to a new branch in one command?

A) `git branch -b feature/new`
B) `git switch -c feature/new`
C) `git checkout --new feature/new`
D) `git create feature/new`

**Answer:** B

**Explanation:** `git switch -c <branch-name>` creates a new branch and switches to it immediately. The older syntax `git checkout -b <branch-name>` also works. The `-c` flag means "create."

---

### Question 10: Branch Naming
Which branch name follows common conventions for a bug fix?

A) `mybugfix`
B) `fix-the-bug-in-api`
C) `fix/memory-leak-preprocessing`
D) `bugfix_20240115`

**Answer:** C

**Explanation:** Branch naming conventions use prefixes like `feature/`, `fix/`, `hotfix/`, `experiment/` followed by a descriptive name with hyphens. This makes branch purpose immediately clear and helps with automation.

---

### Question 11: Fast-Forward Merge
When does a fast-forward merge occur?

A) When branches have conflicting changes
B) When the target branch hasn't diverged from the feature branch
C) When you use the `--ff` flag
D) When merging more than two branches

**Answer:** B

**Explanation:** Fast-forward occurs when the target branch has no new commits since the feature branch was created. Git simply moves the branch pointer forward instead of creating a merge commit. Use `--no-ff` to force a merge commit.

---

### Question 12: Merge Conflicts
You're merging a branch and see conflict markers in a file. What do they mean?

```
<<<<<<< HEAD
code A
=======
code B
>>>>>>> feature-branch
```

A) HEAD is correct, feature-branch is wrong
B) Code A is from current branch, code B is from feature-branch
C) Git automatically chose the better option
D) Both versions will be kept automatically

**Answer:** B

**Explanation:** Conflict markers show conflicting changes: `<<<<<<< HEAD` marks the start of your current branch's version, `=======` separates the two versions, and `>>>>>>> branch-name` marks the end of the incoming branch's version. You must manually resolve by editing.

---

### Question 13: Squash Merge
When would you use `git merge --squash`?

A) To speed up the merge process
B) To combine all commits from a feature branch into one commit
C) To compress file sizes
D) To merge multiple branches at once

**Answer:** B

**Explanation:** `--squash` combines all commits from the feature branch into a single commit on the target branch. This is useful when feature branches have many small WIP commits that you don't want in main branch's history.

---

### Question 14: Merge Strategies
Which command resolves conflicts by always preferring the current branch's version?

A) `git merge -X ours feature-branch`
B) `git merge --prefer-current feature-branch`
C) `git merge --keep-mine feature-branch`
D) `git merge -X theirs feature-branch`

**Answer:** A

**Explanation:** `git merge -X ours` uses the "ours" strategy, automatically resolving conflicts in favor of the current branch. `-X theirs` does the opposite. Useful for generated files where one version is definitely correct.

---

### Question 15: Viewing Branches
Which command shows all branches including remote tracking branches?

A) `git branch`
B) `git branch -r`
C) `git branch -a`
D) `git branch --all-remote`

**Answer:** C

**Explanation:** `git branch` shows local branches only. `git branch -r` shows remote-tracking branches. `git branch -a` (--all) shows both local and remote-tracking branches, giving complete view of all branches.

---

### Question 16: Deleting Branches
What happens if you try to delete an unmerged branch with `git branch -d`?

A) Git deletes it immediately
B) Git shows a warning but deletes it
C) Git refuses and suggests using `-D` instead
D) Git automatically merges it first

**Answer:** C

**Explanation:** `git branch -d` (lowercase) only deletes merged branches to protect you from data loss. For unmerged branches, Git refuses and suggests `-D` (uppercase) to force deletion. Always double-check before using `-D`.

---

## Section 3: Collaboration (Questions 17-22)

### Question 17: Remote Repositories
What does `git remote add upstream <url>` do?

A) Creates a new remote repository
B) Adds a reference to another remote repository named "upstream"
C) Uploads local changes to remote
D) Downloads remote changes

**Answer:** B

**Explanation:** `git remote add <name> <url>` creates a named reference to a remote repository. "upstream" conventionally refers to the original repository when you've forked a project, while "origin" refers to your fork.

---

### Question 18: Fetching vs Pulling
What's the difference between `git fetch` and `git pull`?

A) No difference, they're aliases
B) `fetch` downloads changes but doesn't merge; `pull` downloads and merges
C) `fetch` is faster than `pull`
D) `pull` only works with the main branch

**Answer:** B

**Explanation:** `git fetch` downloads commits, files, and refs from remote but doesn't merge them into your work. `git pull` does `fetch` followed by `merge` (or `rebase`), updating your current branch. Use `fetch` when you want to see changes before integrating.

---

### Question 19: Pull Requests
What's the purpose of a pull request (PR)?

A) To pull changes from remote to local
B) To request write access to a repository
C) To propose changes and enable code review before merging
D) To request help with Git problems

**Answer:** C

**Explanation:** Pull requests are GitHub/GitLab's mechanism for proposing changes. They enable code review, discussion, automated testing, and approval workflows before merging changes into the main branch. Essential for team collaboration.

---

### Question 20: Code Review Comments
Which type of code review comment indicates a blocking issue that must be fixed?

A) 💅 Nitpick
B) ❓ Question
C) 👍 Nice
D) 🚨 BLOCKER

**Answer:** D

**Explanation:** Code review comments should be categorized: BLOCKER (must fix before merge), Important suggestions (should fix), Nitpicks (optional), Questions (clarification needed), and Praise (good work). This helps authors prioritize feedback.

---

### Question 21: Fork Workflow
In a fork-based workflow, how do you keep your fork updated with the original repository?

A) Delete your fork and re-fork
B) `git fetch upstream` and merge upstream/main
C) Pull requests automatically sync forks
D) Forks stay in sync automatically

**Answer:** B

**Explanation:** Add the original repository as "upstream" remote, fetch changes with `git fetch upstream`, then merge with `git merge upstream/main`. This keeps your fork's main branch synchronized with the original project.

---

### Question 22: Rebasing for PRs
You have a PR open, but main has moved forward. What should you do?

A) Close PR and create a new one
B) Rebase your branch on latest main and force push
C) Do nothing, GitHub will handle it
D) Delete your branch and start over

**Answer:** B

**Explanation:** `git fetch upstream && git rebase upstream/main` updates your branch with latest main, replaying your commits on top. Then `git push --force-with-lease` updates the PR. This keeps PR history clean and resolves conflicts.

---

## Section 4: Advanced Git (Questions 23-26)

### Question 23: Interactive Rebase
In interactive rebase, what does the "squash" command do?

A) Deletes the commit
B) Combines commit with previous one, keeping both messages
C) Edits the commit message
D) Reorders commits

**Answer:** B

**Explanation:** In `git rebase -i`, "squash" merges the commit with the previous one and combines both commit messages. "fixup" is similar but discards the message. This cleans up history by combining related commits.

---

### Question 24: Cherry-Picking
When would you use `git cherry-pick`?

A) To delete specific commits
B) To apply a specific commit from another branch
C) To choose which files to commit
D) To select the best merge strategy

**Answer:** B

**Explanation:** `git cherry-pick <commit-hash>` applies the changes from a specific commit to your current branch. Useful for applying a bug fix from one branch to another without merging all changes.

---

### Question 25: Git Bisect
What problem does `git bisect` solve?

A) Merging branches with many conflicts
B) Finding which commit introduced a bug using binary search
C) Splitting large commits into smaller ones
D) Resolving merge conflicts automatically

**Answer:** B

**Explanation:** `git bisect` uses binary search to find the commit that introduced a bug. Mark a good (working) and bad (broken) commit, and Git checks out middle commits for testing until it finds the problematic commit. Can be automated with test scripts.

---

### Question 26: Reflog
You accidentally reset to an old commit and lost your work. How can you recover?

A) Work is permanently lost
B) Use `git reflog` to find the lost commit and recover it
C) Restore from backup only
D) Use `git recover`

**Answer:** B

**Explanation:** `git reflog` shows a log of all HEAD movements, including "lost" commits from resets, rebases, etc. Find the commit hash in reflog and `git checkout <hash>` or create a branch at that point to recover your work.

---

## Section 5: ML-Specific Git (Questions 27-30)

### Question 27: DVC Purpose
Why use DVC (Data Version Control) instead of Git for ML datasets?

A) DVC is faster than Git
B) Git isn't designed for large binary files; DVC handles them efficiently
C) DVC has better merge conflict resolution
D) DVC is required by ML frameworks

**Answer:** B

**Explanation:** Git stores complete file history, making it inefficient for large datasets and models. DVC stores metadata in Git and actual data in separate storage (S3, GCS, etc.), providing version control for data without bloating the Git repository.

---

### Question 28: Git LFS
What types of files should be tracked with Git LFS in an ML project?

A) Python code files
B) Configuration files
C) Model weights (.pth, .h5, .pkl)
D) Documentation

**Answer:** C

**Explanation:** Git LFS (Large File Storage) is designed for large binary files like model weights (.pth, .h5), pickled models (.pkl), ONNX files, etc. LFS stores pointers in Git and actual files in LFS storage, preventing repository bloat.

---

### Question 29: Experiment Tracking
You're running multiple ML experiments. What's the best Git practice?

A) Commit all experiments to main branch
B) Create experiment branches and track configurations as YAML files
C) Don't use Git for experiments
D) Create a new repository for each experiment

**Answer:** B

**Explanation:** Create experiment branches (experiment/name) and version control experiment configurations as YAML files. This maintains reproducibility, allows comparing experiments, and keeps history clean. Tag successful experiments for easy reference.

---

### Question 30: Model Versioning
How should you version a trained model for production deployment?

A) Just copy the file to production
B) Use Git tags on the commit that trained the model
C) Create a git tag with metadata, track model in LFS, and document in JSON
D) Email the model file

**Answer:** C

**Explanation:** Best practice: Tag the training commit (git tag model-v1.0.0), track weights with Git LFS, include metadata JSON with training config/metrics/data version, and document in model registry. This ensures full traceability from data to deployed model.

---

## Answer Key Summary

1. B - Staging area holds changes before committing
2. C - SHA-1 hash uniquely identifies commits
3. B - Working Directory, Staging Area, Repository
4. C - Add patterns to .gitignore before committing
5. B - diff shows unstaged, diff --staged shows staged
6. C - Conventional commit format with type, scope, subject
7. B - git log --oneline -5
8. C - git restore --staged unstages without losing changes
9. B - git switch -c creates and switches
10. C - fix/ prefix with descriptive name
11. B - When target branch hasn't diverged
12. B - HEAD is current, feature-branch is incoming
13. B - Combines all commits into one
14. A - git merge -X ours prefers current branch
15. C - git branch -a shows all branches
16. C - Git refuses and suggests -D
17. B - Adds named reference to remote repository
18. B - fetch downloads, pull downloads and merges
19. C - Proposes changes for code review
20. D - BLOCKER indicates must-fix issue
21. B - Fetch upstream and merge
22. B - Rebase on main and force push
23. B - Combines with previous, keeps both messages
24. B - Apply specific commit from another branch
25. B - Find bug-introducing commit with binary search
26. B - Use reflog to find and recover
27. B - Git isn't efficient for large binary files
28. C - Model weights and large binary files
29. B - Experiment branches with config versioning
30. C - Tag + LFS + metadata JSON for traceability

---

## Scoring Guide

**28-30 correct (93-100%)**: Excellent! You've mastered Git for ML infrastructure.

**24-27 correct (80-90%)**: Good! You understand Git well. Review missed topics.

**20-23 correct (67-79%)**: Passing, but review key concepts, especially:
- Branching workflows
- Collaboration practices
- ML-specific tooling

**Below 20 (< 67%)**: Review course materials and practice more:
- Repeat exercises 01-07
- Re-read lecture notes
- Practice with real repositories

---

## Key Concepts Review

If you missed questions in certain areas, review these topics:

### Git Fundamentals (Q1-8)
- Three-state workflow (working/staging/repository)
- .gitignore for ML projects
- Commit message best practices
- Viewing and searching history

### Branching & Merging (Q9-16)
- Branch naming conventions
- Fast-forward vs three-way merges
- Conflict resolution
- Merge strategies

### Collaboration (Q17-22)
- Fork and upstream workflows
- Pull request best practices
- Code review guidelines
- Keeping forks synchronized

### Advanced Techniques (Q23-26)
- Interactive rebase for clean history
- Cherry-picking specific commits
- Bisect for debugging
- Reflog for recovery

### ML Workflows (Q27-30)
- DVC for data versioning
- Git LFS for large files
- Experiment tracking
- Model versioning and deployment

---

## Next Steps

1. **Review** any topics where you missed questions
2. **Practice** with the exercises for those topics
3. **Apply** Git in your actual ML projects
4. **Move on** to Module 004 if you scored 80% or higher

Remember: Git proficiency comes with practice. The more you use these workflows in real projects, the more natural they'll become!
