# Module 003 — Git & Version Control Resources

## Official documentation

- **Pro Git book** — [git-scm.com/book](https://git-scm.com/book/en/v2). Free, comprehensive, regularly updated. The canonical reference.
- **Git reference** — [git-scm.com/docs](https://git-scm.com/docs). Command-by-command documentation.
- **GitHub docs** — [docs.github.com](https://docs.github.com/). Specifically the "Get started" and "Using Git" sections.

## Books

- **Pro Git** by Scott Chacon and Ben Straub. Already mentioned above; worth a second mention because it's free *and* the best Git book in existence.
- **Git for Teams** by Emma Jane Hogbin Westby. Strong on collaboration workflows.
- **Version Control with Git (3rd ed.)** by Prem Kumar Ponuthorai. Modern coverage including GitHub Actions integration.

## Interactive learning

- **Learn Git Branching** — [learngitbranching.js.org](https://learngitbranching.js.org/). Visual, hands-on. Especially good for branching, rebasing, merging.
- **GitHub Skills** — [skills.github.com](https://skills.github.com/). Interactive courses inside GitHub.
- **Oh My Git!** — [ohmygit.org](https://ohmygit.org/). Open-source game that teaches Git.

## Cheat sheets

- **GitHub's Git Cheat Sheet** — [training.github.com/downloads/github-git-cheat-sheet.pdf](https://training.github.com/downloads/github-git-cheat-sheet.pdf).
- **Atlassian Git tutorial** — [atlassian.com/git](https://www.atlassian.com/git/tutorials). Particularly strong on merge vs. rebase.

## ML-specific version control

- **DVC documentation** — [dvc.org/doc](https://dvc.org/doc). Data + model versioning that complements Git.
- **MLflow documentation** — [mlflow.org/docs/latest](https://mlflow.org/docs/latest/index.html). Experiment tracking + model registry.
- **nbstripout** — [github.com/kynan/nbstripout](https://github.com/kynan/nbstripout). Strip Jupyter notebook outputs before commit.
- **jupytext** — [jupytext.readthedocs.io](https://jupytext.readthedocs.io/). Keep `.py` alongside `.ipynb` for diff-friendly notebooks.

## Tools

- **lazygit** — [github.com/jesseduffield/lazygit](https://github.com/jesseduffield/lazygit). Terminal UI for Git. Fast.
- **gh CLI** — [cli.github.com](https://cli.github.com/). Official GitHub CLI for PRs, issues, releases.
- **GitHub Desktop / Sublime Merge / GitKraken** — GUI clients. Pick one if you prefer visual workflows; otherwise the CLI is fine.
- **pre-commit** — [pre-commit.com](https://pre-commit.com/). Framework for managing pre-commit hooks.

## Workflow references

- **Conventional Commits** — [conventionalcommits.org](https://www.conventionalcommits.org/). Standard for commit messages.
- **GitFlow** — [nvie.com/posts/a-successful-git-branching-model](https://nvie.com/posts/a-successful-git-branching-model/). The classic branching model. Heavyweight; rarely the right choice for modern teams but worth understanding.
- **GitHub Flow** — [docs.github.com/en/get-started/quickstart/github-flow](https://docs.github.com/en/get-started/using-github/github-flow). Lightweight branch-+-PR model. Much more common today.
- **Trunk-based development** — [trunkbaseddevelopment.com](https://trunkbaseddevelopment.com/). Single main branch, feature flags. Used at high-velocity teams.

## Cross-references in this curriculum

- Engineer track's `mod-109-infrastructure-as-code` for GitOps with ArgoCD / FluxCD.
- Module 005 (Docker) — version-control your Dockerfiles + .dockerignore.
- Module 006 (Kubernetes) — version-control your manifests.
