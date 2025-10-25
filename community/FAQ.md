# Frequently Asked Questions (FAQ)

Common questions and answers for learners in the Junior AI Infrastructure Engineer curriculum.

---

## Table of Contents

- [General Questions](#general-questions)
- [Prerequisites](#prerequisites)
- [Time Commitment](#time-commitment)
- [Technical Setup](#technical-setup)
- [Learning Difficulties](#learning-difficulties)
- [Projects](#projects)
- [Assessments](#assessments)
- [Job Search](#job-search)
- [Tools & Environment](#tools--environment)
- [Community & Support](#community--support)

---

## General Questions

### Q1: Who is this curriculum for?
**A**: This curriculum is designed for:
- Career changers wanting to enter AI infrastructure
- Recent graduates interested in ML engineering infrastructure
- Software engineers pivoting to ML infrastructure roles
- DevOps engineers expanding into AI/ML space
- Anyone wanting structured learning in AI infrastructure

Prerequisites: Basic programming knowledge and familiarity with command line recommended but not required.

---

### Q2: Do I need a computer science degree?
**A**: No! While a CS degree can be helpful, it's not required. This curriculum assumes:
- Basic programming experience (Python preferred)
- Willingness to learn
- Strong problem-solving skills
- Self-discipline for self-paced learning

Many successful AI infrastructure engineers are self-taught or come from non-CS backgrounds.

---

### Q3: Is this curriculum enough to get a job?
**A**: This curriculum provides foundational knowledge for junior roles. To maximize job prospects:
- Complete all projects with high quality
- Build additional portfolio projects
- Contribute to open source
- Network with professionals
- Practice interview questions
- Gain internship or freelance experience (if possible)

Think of this as your foundation—continuous learning is part of the career.

---

### Q4: What's the difference between learning and solutions repositories?
**A**:
- **Learning Repository**: Contains lessons, exercises with stubs, and templates. You work through these.
- **Solutions Repository**: Contains complete implementations for reference. Use these AFTER attempting projects yourself.

Always try to solve problems independently before checking solutions.

---

### Q5: Can I use AI assistants (ChatGPT, GitHub Copilot, etc.)?
**A**:
- **While learning**: Use sparingly. Understanding > completion.
- **For debugging**: Yes, but understand the solutions.
- **For generating entire projects**: No. You won't learn.
- **Best practice**: Try independently first, then use AI for specific stuck points.

The goal is genuine competency, not just completed assignments.

---

## Prerequisites

### Q6: I don't know Python. Should I learn it first?
**A**: Yes, basic Python is essential. Before starting this curriculum:
- Complete a Python fundamentals course (2-4 weeks)
- Be comfortable with: variables, functions, loops, classes
- Recommended: "Python Crash Course" or Codecademy Python
- Take the Prerequisites Quiz—if you score <70%, do more Python prep

---

### Q7: Do I need to know machine learning before starting?
**A**: No deep ML knowledge required! You need:
- **Awareness** of what ML is (models, training, inference)
- **Basic concepts** like features, predictions, accuracy
- **Ability to use** pre-trained models

The curriculum includes ML fundamentals (Module 1). You'll learn enough to deploy and manage ML systems.

---

### Q8: Do I need a Mac or Linux computer?
**A**: Strongly recommended. While Windows works (especially with WSL2):
- Most servers run Linux
- Docker works better on Linux/Mac
- Industry primarily uses Linux/Mac
- Easier for development

If using Windows, set up WSL2 (Windows Subsystem for Linux) with Ubuntu.

---

### Q9: How much math do I need to know?
**A**: For this curriculum, minimal math needed:
- Basic algebra
- Understanding of percentages and statistics (helpful)
- No calculus or advanced math required

This curriculum focuses on infrastructure, not ML research. Implementation skills matter more than mathematical proof.

---

## Time Commitment

### Q10: How long does it take to complete the curriculum?
**A**: Depends on your schedule:
- **Full-time** (40 hrs/week): 8-12 weeks
- **Part-time** (20 hrs/week): 4-6 months
- **Casual** (10 hrs/week): 6-12 months

Time varies based on:
- Prior experience
- Learning speed
- Depth of exploration
- Time on projects

---

### Q11: Can I work through this while employed full-time?
**A**: Absolutely! Many learners do. Tips:
- Set aside 1-2 hours daily
- Use weekends for projects (4-6 hours)
- Consistency > intensity
- Aim for 10-15 hours/week
- Expect 6-9 months completion

---

### Q12: What if I need to take a break?
**A**: Life happens! To resume effectively:
- Use the progress tracking templates
- Review your last completed module before continuing
- Don't restart from scratch
- Ease back in with easier exercises
- Join a study group for accountability

Knowledge retention decreases over time, but you don't lose everything. A quick review gets you back on track.

---

## Technical Setup

### Q13: My Docker installation isn't working. Help!
**A**: Common issues and fixes:

**Linux**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker
```

**Mac/Windows**:
- Ensure Docker Desktop is running
- Check resource allocation (increase if needed)
- Restart Docker Desktop

**General**:
- Run `docker --version` to verify installation
- Try `docker run hello-world`
- Check Docker Desktop logs
- See `resources/tools.md` for detailed setup

---

### Q14: I'm getting "permission denied" errors. What do I do?
**A**: Usually a Docker permissions issue:

```bash
# Linux: Add to docker group
sudo usermod -aG docker $USER
# Log out and log back in

# Verify
docker ps
```

For file permission issues:
```bash
# Check ownership
ls -la

# Fix ownership
sudo chown -R $USER:$USER /path/to/directory
```

---

### Q15: My computer is slow. What are minimum requirements?
**A**: Minimum specs:
- **CPU**: Dual-core (Quad-core recommended)
- **RAM**: 8GB (16GB recommended)
- **Storage**: 50GB free space (SSD preferred)
- **OS**: Ubuntu 20.04+, macOS 10.15+, or Windows 10 with WSL2

If your computer struggles:
- Close other applications while learning
- Use lightweight alternatives (Minikube single-node)
- Consider cloud development environments (AWS Cloud9, GitHub Codespaces)

---

### Q16: Can I use a cloud VM instead of my local machine?
**A**: Yes! Options:
- **AWS EC2**: Free tier available
- **Google Cloud**: $300 credit for new users
- **DigitalOcean**: Affordable droplets
- **GitHub Codespaces**: Cloud-based VS Code

Benefits:
- Better resources
- Matches production environment
- Access from anywhere

Drawbacks:
- Internet dependency
- Potential costs after free tier
- Slightly more complex setup

---

## Learning Difficulties

### Q17: I'm stuck on a concept. What should I do?
**A**: Follow this process:
1. **Reread** the material carefully
2. **Try examples** in the lessons
3. **Search** online (official docs, Stack Overflow)
4. **Watch videos** on the topic (YouTube)
5. **Ask** in study groups or community forums
6. **Take a break** and return with fresh perspective
7. **Try different resource** (alternative explanations help)

Don't spend more than 1-2 hours stuck before seeking help.

---

### Q18: The pace feels too fast/slow. What should I do?
**A**:
**Too Fast**:
- Slow down, depth > speed
- Supplement with additional resources
- Practice more exercises
- Don't move forward until comfortable

**Too Slow**:
- Skip ahead to challenging sections
- Try building projects early
- Explore advanced variations
- Contribute to open source for real complexity

This is self-paced—adjust to your needs!

---

### Q19: I keep forgetting what I learned. How do I retain information?
**A**: Use these techniques:
1. **Active recall**: Test yourself regularly
2. **Spaced repetition**: Review after 1 day, 1 week, 1 month
3. **Practice projects**: Apply concepts immediately
4. **Teach others**: Explain concepts to solidify understanding
5. **Take notes**: Write summaries in your own words
6. **Use flashcards**: For commands and terminology
7. **Build projects**: Hands-on practice is key

Remember: Some forgetting is normal. Reference materials exist for a reason!

---

### Q20: I failed the midterm exam. What now?
**A**: Don't panic! This is a learning opportunity:
1. **Review feedback** to identify weak areas
2. **Revisit modules** where you struggled
3. **Practice more** exercises in those areas
4. **Try alternative resources** for difficult concepts
5. **Ask for help** in community channels
6. **Retake** after meaningful review (wait 1 week)

Many successful learners fail on first attempts. Growth happens through struggle.

---

## Projects

### Q21: My project isn't working. When should I check the solutions?
**A**: Check solutions only after:
1. **Spending significant time** trying (minimum 2-3 hours)
2. **Debugging systematically** (logs, error messages, Google)
3. **Asking for help** in community
4. **Breaking problem into parts** and testing each

When you do check solutions:
- Don't copy-paste
- Understand the approach
- Implement in your own way
- Document what you learned

---

### Q22: Can I use libraries not mentioned in requirements?
**A**: Yes, but:
- Core requirements must still be met
- Document why you chose additional libraries
- Ensure they're appropriate for the task
- Don't over-engineer—simpler is often better

The goal is learning fundamentals, not building the fanciest system.

---

### Q23: Should I make my projects public on GitHub?
**A**: Yes! Benefits:
- **Portfolio**: Show skills to employers
- **Feedback**: Community can review and suggest
- **Practice**: Good Git/GitHub hygiene
- **Networking**: People discover your work

Just ensure:
- No sensitive data (credentials, API keys)
- Professional README
- Clean commit history
- Regular updates

---

### Q24: How "perfect" should my projects be?
**A**: Aim for:
- **Functional**: Works as specified
- **Clean**: Well-organized code
- **Documented**: Clear README
- **Tested**: Basic testing present

Don't aim for:
- Production-ready perfection
- Every possible feature
- Zero bugs
- Cutting-edge optimization

"Good enough to pass and learn from" is the goal. You can always improve later.

---

## Assessments

### Q25: What's a passing score?
**A**:
- **Quizzes**: 75%
- **Midterm Practical**: 75%
- **Final Practical**: 80%
- **Projects**: 75%

These are guidelines for self-assessment. The goal is genuine competency, not just passing scores.

---

### Q26: Can I retake assessments?
**A**: Yes! Unlimited retakes for:
- Quizzes (wait 24 hours between attempts)
- Practical exams (wait 1 week, maximum 3 attempts recommended)
- Projects (resubmit until passing)

Use failed attempts as learning opportunities. Review, improve, and try again.

---

### Q27: How strictly should I time myself on exams?
**A**: Be honest but flexible:
- **For learning**: Focus on understanding over time
- **For job prep**: Practice under time constraints
- **Time overages**: Note how much extra time you needed

In real work, quality often matters more than speed, but efficiency is valued.

---

## Job Search

### Q28: When should I start applying for jobs?
**A**: Start applying when you:
- ☑ Completed all modules
- ☑ Completed at least 3-4 projects
- ☑ Passed the final practical exam
- ☑ Have a portfolio on GitHub
- ☑ Feel comfortable discussing your projects

You don't need to feel "fully ready"—some learning happens on the job. Apply when you meet 70-80% of job requirements.

---

### Q29: What job titles should I look for?
**A**: Entry-level titles:
- Junior ML Engineer
- ML Infrastructure Engineer
- Junior MLOps Engineer
- DevOps Engineer (ML focus)
- AI Platform Engineer (Junior)
- Data Infrastructure Engineer

Also consider:
- Internships
- Contract positions
- Smaller companies (more learning opportunities)

---

### Q30: How do I explain self-taught experience on my resume?
**A**:
- List skills and technologies prominently
- Highlight projects with metrics and impact
- Include this curriculum as "Professional Development"
- Emphasize problem-solving and self-learning ability
- Show GitHub profile with active projects

Example:
```
Professional Development
Junior AI Infrastructure Engineer Curriculum | 2024
- Completed 150+ hours of hands-on training in Docker, Kubernetes, and CI/CD
- Built 5 production-ready ML infrastructure projects
- Deployed containerized ML models with monitoring and scaling
```

---

### Q31: Should I get certified (CKA, Docker DCA, etc.)?
**A**: Certifications can help but aren't required for entry-level. Consider:

**Pros**:
- Validates knowledge
- Stands out on resume
- Structured learning path
- Some employers value them

**Cons**:
- Costs money ($300-400)
- Takes time to prepare
- Experience often valued more

**Recommendation**: Focus on projects and practical skills first. Get certified after landing a role or if you have time/budget.

---

## Tools & Environment

### Q32: Which IDE should I use?
**A**: For this curriculum:
- **VSCode** (recommended): Free, lightweight, great extensions
- **PyCharm**: Excellent for Python, but heavier
- **Vim/Neovim**: If you're already proficient

Most important: Choose one and master it. VSCode is most common in industry.

---

### Q33: Do I need to memorize all these commands?
**A**: No! You'll memorize commonly used commands through practice. For others:
- Use cheat sheets (provided in `resources/cheat-sheets/`)
- Reference official documentation
- Use command history (up arrow, `history` command)
- Create aliases for frequent commands

Understanding > memorization. Know what's possible and where to find details.

---

### Q34: Should I use Docker Desktop or Docker Engine?
**A**:
- **Docker Desktop** (Mac/Windows): Easier setup, includes GUI
- **Docker Engine** (Linux): Lightweight, command-line only

For learning: Docker Desktop is fine.
For production mindset: Learn Docker Engine commands.

---

## Community & Support

### Q35: How do I get help when I'm stuck?
**A**: Multiple options:
1. **Search first**: Google error messages
2. **Study groups**: See `community/study-groups.md`
3. **Office hours**: See `community/office-hours.md`
4. **Stack Overflow**: Search and ask questions
5. **Reddit**: r/devops, r/docker, r/kubernetes
6. **Discord/Slack**: Join relevant communities

When asking for help:
- Describe what you tried
- Include error messages
- Provide relevant code
- Explain expected vs. actual behavior

---

### Q36: Are there study groups I can join?
**A**: Yes! See `community/study-groups.md` for:
- How to find existing groups
- How to start your own
- Best practices for study groups
- Communication channels

Learning with others improves retention and motivation!

---

### Q37: Can I get one-on-one mentorship?
**A**: Options:
- **Peer mentorship**: Connect with learners ahead of you
- **Community mentors**: Active in forums/Discord
- **Paid mentoring**: Platforms like MentorCruise, Codementor
- **Company mentors**: After getting a job

See `community/office-hours.md` for virtual support sessions.

---

### Q38: How do I stay motivated for months of self-study?
**A**: Tips that work:
1. **Set small milestones**: Weekly goals, not just end goal
2. **Track progress visually**: Use progress templates
3. **Join community**: Accountability and support
4. **Celebrate wins**: Completed a module? Celebrate!
5. **Connect to purpose**: Remember your "why"
6. **Take breaks**: Avoid burnout
7. **Vary activities**: Mix reading, coding, watching videos
8. **Share journey**: Blog, tweet, LinkedIn updates

Motivation fluctuates—build habits that carry you through low periods.

---

### Q39: Is there a certificate upon completion?
**A**: This is an open-source curriculum, so there's no official certificate. However:
- Your GitHub portfolio IS your certificate
- Completed projects demonstrate competency
- Passing assessments shows you met standards
- List curriculum on resume under Professional Development

Employers care more about skills and projects than certificates for these roles.

---

### Q40: How can I contribute back to this curriculum?
**A**: Ways to contribute:
- Report issues or errors
- Suggest improvements
- Share your project solutions (after completing)
- Help other learners in community
- Write blog posts about your experience
- Create supplementary resources
- Submit pull requests for fixes

See repository CONTRIBUTING.md for details.

---

## Still Have Questions?

- **Check documentation**: Start with README.md
- **Search this FAQ**: Use Ctrl+F
- **Ask in community**: See `community/study-groups.md`
- **Open an issue**: GitHub repository issues
- **Office hours**: See `community/office-hours.md`

---

**Remember**: No question is too basic! Everyone starts as a beginner. The community is here to help you succeed.

Good luck on your learning journey!
