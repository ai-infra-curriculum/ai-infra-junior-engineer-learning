# Prerequisites Quiz

## Overview

**Purpose**: Assess foundational knowledge required for the Junior AI Infrastructure Engineer curriculum

**Duration**: 30 minutes

**Total Questions**: 20

**Passing Score**: 70% (14/20 correct)

**Topics Covered**:
- Python Fundamentals (5 questions)
- Linux/Command Line (5 questions)
- Version Control with Git (4 questions)
- Basic Networking (3 questions)
- Database Fundamentals (3 questions)

**Instructions**:
1. Answer all questions to the best of your ability
2. Some questions have multiple correct answers (marked as "Select all that apply")
3. Do not use external resources during the quiz
4. Record your answers and check against the answer key at the end
5. If you score < 70%, review the recommended resources before starting the curriculum

---

## Python Fundamentals (Questions 1-5)

### Question 1: Data Types
**Difficulty**: Easy

Which of the following Python data types is **immutable**?

A) List
B) Dictionary
C) Tuple
D) Set

**Your Answer**: ____

---

### Question 2: List Comprehension
**Difficulty**: Medium

What is the output of the following code?

```python
numbers = [1, 2, 3, 4, 5]
result = [x * 2 for x in numbers if x % 2 == 0]
print(result)
```

A) `[2, 4, 6, 8, 10]`
B) `[4, 8]`
C) `[2, 4]`
D) `[1, 3, 5]`

**Your Answer**: ____

---

### Question 3: Function Arguments
**Difficulty**: Medium

What will this function return when called with `calculate(10, 5)`?

```python
def calculate(a, b=2, *args, **kwargs):
    return a + b
```

A) `10`
B) `15`
C) `12`
D) Error

**Your Answer**: ____

---

### Question 4: Exception Handling
**Difficulty**: Easy

Which statement is true about exception handling in Python?

A) `finally` block always executes, even if an exception is raised
B) `else` block executes only when an exception is raised
C) You must have a `finally` block if you have a `try` block
D) `except` can only catch one type of exception at a time

**Your Answer**: ____

---

### Question 5: Virtual Environments
**Difficulty**: Easy

What is the primary purpose of Python virtual environments?

A) To run Python code faster
B) To isolate project dependencies and avoid conflicts
C) To enable concurrent execution of Python scripts
D) To automatically format Python code

**Your Answer**: ____

---

## Linux/Command Line (Questions 6-10)

### Question 6: File Permissions
**Difficulty**: Medium

What does the command `chmod 755 script.sh` do?

A) Owner: read/write/execute, Group: read/execute, Others: read/execute
B) Owner: read/write, Group: read/write, Others: read/write
C) Everyone gets full permissions
D) Owner: execute only, Group: read only, Others: write only

**Your Answer**: ____

---

### Question 7: Process Management
**Difficulty**: Medium

Which command would you use to find all running Python processes?

A) `find python`
B) `ps aux | grep python`
C) `ls -la python`
D) `top python`

**Your Answer**: ____

---

### Question 8: Redirection and Pipes
**Difficulty**: Easy

What does the following command do?

```bash
cat logfile.txt | grep ERROR > errors.txt
```

A) Searches for "ERROR" in logfile.txt and displays results
B) Searches for "ERROR" in logfile.txt and appends results to errors.txt
C) Searches for "ERROR" in logfile.txt and overwrites errors.txt with results
D) Creates a new file called errors.txt with all contents of logfile.txt

**Your Answer**: ____

---

### Question 9: Environment Variables
**Difficulty**: Easy

How do you set an environment variable in Linux (bash)?

A) `SET VAR=value`
B) `export VAR=value`
C) `VAR := value`
D) `env VAR=value`

**Your Answer**: ____

---

### Question 10: Disk Usage
**Difficulty**: Easy

Which command shows disk space usage of the current directory?

A) `df -h`
B) `du -sh`
C) `ls -lh`
D) `free -h`

**Your Answer**: ____

---

## Version Control with Git (Questions 11-14)

### Question 11: Git Basics
**Difficulty**: Easy

What is the correct sequence of commands to commit changes to a Git repository?

A) `git commit -m "message"` → `git add .` → `git push`
B) `git add .` → `git commit -m "message"` → `git push`
C) `git push` → `git add .` → `git commit -m "message"`
D) `git commit -m "message"` → `git push` → `git add .`

**Your Answer**: ____

---

### Question 12: Branching
**Difficulty**: Medium

What does `git checkout -b feature-branch` do?

A) Switches to an existing branch called feature-branch
B) Creates a new branch called feature-branch and switches to it
C) Deletes the branch called feature-branch
D) Merges feature-branch into the current branch

**Your Answer**: ____

---

### Question 13: Undoing Changes
**Difficulty**: Medium

You've made changes to a file but haven't staged them yet. Which command discards those changes?

A) `git reset --hard`
B) `git checkout -- filename`
C) `git revert filename`
D) `git rm filename`

**Your Answer**: ____

---

### Question 14: Remote Repositories
**Difficulty**: Easy

What does `git clone` do?

A) Creates a copy of your local repository on a remote server
B) Downloads a copy of a remote repository to your local machine
C) Syncs changes between local and remote repositories
D) Creates a new branch in the remote repository

**Your Answer**: ____

---

## Basic Networking (Questions 15-17)

### Question 15: HTTP Methods
**Difficulty**: Easy

Which HTTP method is typically used to retrieve data from a server?

A) POST
B) PUT
C) GET
D) DELETE

**Your Answer**: ____

---

### Question 16: IP Addresses
**Difficulty**: Medium

Which of the following is a valid private IP address?

A) `8.8.8.8`
B) `192.168.1.100`
C) `256.100.50.25`
D) `173.194.45.67`

**Your Answer**: ____

---

### Question 17: Ports
**Difficulty**: Easy

What is the default port for HTTP traffic?

A) 22
B) 443
C) 80
D) 3306

**Your Answer**: ____

---

## Database Fundamentals (Questions 18-20)

### Question 18: SQL Basics
**Difficulty**: Easy

Which SQL command is used to retrieve data from a database?

A) GET
B) SELECT
C) FETCH
D) RETRIEVE

**Your Answer**: ____

---

### Question 19: Database Relationships
**Difficulty**: Medium

What is a foreign key?

A) The primary identifier for a table
B) A unique key that's encrypted
C) A field that references the primary key of another table
D) A key that grants access to the database

**Your Answer**: ____

---

### Question 20: SQL vs NoSQL
**Difficulty**: Medium

**Select all that apply**: Which statements are true about NoSQL databases?

A) They always use a fixed schema like relational databases
B) They can be horizontally scaled more easily than SQL databases
C) MongoDB and Redis are examples of NoSQL databases
D) They cannot handle structured data

**Your Answers** (list all that apply): ____

---

## Answer Key

**Do not look at the answers until you've completed the quiz!**

<details>
<summary>Click to reveal answers</summary>

### Answers and Explanations

**1. C - Tuple**
- Tuples are immutable; once created, they cannot be modified
- Lists, dictionaries, and sets are mutable

**2. B - [4, 8]**
- The comprehension filters even numbers (2, 4) then multiplies by 2
- Result: [2*2, 4*2] = [4, 8]

**3. B - 15**
- Function is called with a=10, b=5
- Returns 10 + 5 = 15
- Default b=2 is overridden by the provided argument

**4. A - `finally` block always executes, even if an exception is raised**
- The finally block runs regardless of exceptions
- else executes only when NO exception is raised
- finally is optional
- except can catch multiple exception types

**5. B - To isolate project dependencies and avoid conflicts**
- Virtual environments create isolated Python environments
- Prevents dependency conflicts between projects
- Doesn't affect execution speed

**6. A - Owner: read/write/execute, Group: read/execute, Others: read/execute**
- 7 = read(4) + write(2) + execute(1)
- 5 = read(4) + execute(1)
- 755 is common for executable scripts

**7. B - `ps aux | grep python`**
- ps aux lists all processes
- grep filters for lines containing "python"
- This is the standard way to find specific processes

**8. C - Searches for "ERROR" in logfile.txt and overwrites errors.txt with results**
- cat reads the file
- grep filters for "ERROR"
- > redirects output and overwrites (>> would append)

**9. B - `export VAR=value`**
- export makes the variable available to child processes
- This is the bash/sh syntax
- SET is Windows syntax

**10. B - `du -sh`**
- du = disk usage
- -s = summary (total)
- -h = human-readable format
- df shows filesystem space, not directory usage

**11. B - `git add .` → `git commit -m "message"` → `git push`**
- First stage changes (add)
- Then commit staged changes
- Finally push to remote repository

**12. B - Creates a new branch called feature-branch and switches to it**
- -b flag creates a new branch
- Equivalent to: git branch feature-branch; git checkout feature-branch
- git switch -c is the newer syntax

**13. B - `git checkout -- filename`**
- Discards unstaged changes to a file
- Restores the file to the last committed state
- git restore filename is the newer syntax

**14. B - Downloads a copy of a remote repository to your local machine**
- Clones the entire repository including history
- Creates a new directory with the repository name
- Automatically sets up remote tracking

**15. C - GET**
- GET retrieves data
- POST sends data to create/update
- PUT updates existing data
- DELETE removes data

**16. B - `192.168.1.100`**
- 192.168.x.x is a private IP range
- Also: 10.x.x.x and 172.16.x.x - 172.31.x.x
- 8.8.8.8 is Google's public DNS
- 256 exceeds the valid range (0-255)

**17. C - 80**
- HTTP uses port 80 by default
- HTTPS uses port 443
- SSH uses port 22
- MySQL uses port 3306

**18. B - SELECT**
- SELECT is the SQL command to query data
- Example: SELECT * FROM users;
- GET is an HTTP method, not SQL

**19. C - A field that references the primary key of another table**
- Foreign keys establish relationships between tables
- They enforce referential integrity
- Point to the primary key of a related table

**20. B and C**
- B: NoSQL databases typically scale horizontally more easily
- C: MongoDB (document store) and Redis (key-value store) are NoSQL
- A is FALSE: NoSQL databases are typically schema-flexible
- D is FALSE: NoSQL can handle structured, semi-structured, and unstructured data

</details>

---

## Scoring Guide

### Calculate Your Score

Count the number of correct answers:
- Questions 1-19: 1 point each
- Question 20: 1 point (both B and C must be selected, no others)

**Total Correct**: ___ / 20

**Percentage**: ___ %

### Score Interpretation

| Score | Percentage | Interpretation | Recommendation |
|-------|------------|----------------|----------------|
| 18-20 | 90-100% | Excellent | Proceed with confidence |
| 14-17 | 70-89% | Good | Proceed, review weak areas |
| 10-13 | 50-69% | Fair | Review resources before starting |
| 0-9 | 0-49% | Needs Improvement | Complete prerequisites first |

### Topic Analysis

Record your score per topic:

| Topic | Your Score | Max Score | Percentage |
|-------|------------|-----------|------------|
| Python Fundamentals | ___ | 5 | ___% |
| Linux/Command Line | ___ | 5 | ___% |
| Git Version Control | ___ | 4 | ___% |
| Basic Networking | ___ | 3 | ___% |
| Database Fundamentals | ___ | 3 | ___% |

**Weak Areas** (< 60% in a topic):
- [ ] Python Fundamentals
- [ ] Linux/Command Line
- [ ] Git Version Control
- [ ] Basic Networking
- [ ] Database Fundamentals

---

## Remediation Resources

If you scored below 70% or have weak areas, review these resources:

### Python Fundamentals
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python - Python Basics](https://realpython.com/learning-paths/python3-introduction/)
- [Codecademy Python Course](https://www.codecademy.com/learn/learn-python-3)
- Practice: Complete 50 Python exercises on HackerRank

### Linux/Command Line
- [Linux Journey](https://linuxjourney.com/)
- [The Linux Command Line Book](http://linuxcommand.org/tlcl.php) (free)
- [Bash Scripting Tutorial](https://www.shellscript.sh/)
- Practice: Set up a Linux VM and use only terminal for a week

### Git Version Control
- [Pro Git Book](https://git-scm.com/book/en/v2) (free, chapters 1-3)
- [Learn Git Branching](https://learngitbranching.js.org/) (interactive)
- [GitHub Learning Lab](https://lab.github.com/)
- Practice: Create a repository, make 20 commits with branching

### Basic Networking
- [Computer Networking: A Top-Down Approach](https://www.youtube.com/playlist?list=PLhb9gLxUWF1yCIaGxdvP2xBYdLIJLgxW7) (YouTube lectures)
- [HTTP Basics](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP)
- Practice: Use curl and Postman to make API requests

### Database Fundamentals
- [SQL Tutorial - W3Schools](https://www.w3schools.com/sql/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)
- [MongoDB University](https://university.mongodb.com/) (free courses)
- Practice: Create a database, write 20 different queries

---

## Retake Policy

- You may retake this quiz **unlimited times**
- Wait **24 hours** between attempts
- Use failed attempts to identify gaps
- After 3 attempts with < 70%, complete remediation resources

---

## Next Steps

### If You Passed (70%+)
1. Review any questions you got wrong
2. Proceed to **Module 1: Introduction to AI Infrastructure**
3. Keep this quiz for reference
4. Join the community study group

### If You Need Review (<70%)
1. Focus on topics where you scored < 60%
2. Complete recommended resources for weak areas
3. Practice hands-on exercises
4. Retake the quiz after 24 hours
5. Continue reviewing until you achieve 70%+

---

## Study Tips

Before retaking or moving forward:

1. **Hands-on Practice**: Don't just read; actually code and execute commands
2. **Spaced Repetition**: Review concepts over multiple days
3. **Teach Others**: Explain concepts to solidify understanding
4. **Real Projects**: Build small projects using these foundational skills
5. **Community**: Discuss questions with peers

---

## Question Feedback

Found an error or have suggestions? Please open an issue in the repository with:
- Question number
- Your concern
- Suggested improvement

---

**Good luck!** Remember, this quiz is a learning tool, not a barrier. The goal is to ensure you have the foundation needed to succeed in this curriculum.
