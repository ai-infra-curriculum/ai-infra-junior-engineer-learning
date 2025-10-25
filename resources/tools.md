# Development Tools Guide

Essential tools and setup recommendations for Junior AI Infrastructure Engineers.

---

## Table of Contents

- [Development Environment](#development-environment)
- [Text Editors and IDEs](#text-editors-and-ides)
- [Terminal and Shell](#terminal-and-shell)
- [Container Tools](#container-tools)
- [Kubernetes Tools](#kubernetes-tools)
- [Version Control](#version-control)
- [Python Development](#python-development)
- [Monitoring and Debugging](#monitoring-and-debugging)
- [API Development and Testing](#api-development-and-testing)
- [Database Tools](#database-tools)
- [Cloud Platforms](#cloud-platforms)
- [Productivity Tools](#productivity-tools)

---

## Development Environment

### Operating System

**Recommended**: Linux (Ubuntu 22.04 LTS) or macOS

**Option 1: Linux Native**
- Best for development
- Native Docker support
- Most servers run Linux
- Recommended distributions:
  - Ubuntu 22.04 LTS
  - Fedora
  - Pop!_OS

**Option 2: macOS**
- Good for development
- Unix-based
- Install Homebrew package manager

**Option 3: Windows + WSL2**
- Windows Subsystem for Linux 2
- Near-native Linux performance
- Install Ubuntu 22.04 from Microsoft Store
- Configure VSCode for WSL

**Option 4: Virtual Machine**
- VirtualBox or VMware
- Install Ubuntu Desktop
- Minimum 4GB RAM, 25GB storage

---

## Text Editors and IDEs

### Visual Studio Code (Recommended)
**Free | Cross-platform**

**Installation**:
```bash
# Ubuntu/Debian
sudo snap install code --classic

# macOS
brew install --cask visual-studio-code

# Windows
# Download from https://code.visualstudio.com/
```

**Essential Extensions**:
- Python (Microsoft)
- Docker (Microsoft)
- Kubernetes (Microsoft)
- GitLens (Enhanced Git)
- Remote - SSH
- Remote - Containers
- YAML (Red Hat)
- Pylance (Python language server)
- autoDocstring
- Better Comments
- Error Lens
- indent-rainbow

**Recommended Settings**:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "files.trimTrailingWhitespace": true
}
```

### PyCharm Community Edition
**Free | Python-focused**
- Powerful Python IDE
- Excellent debugging
- Built-in database tools
- Download: https://www.jetbrains.com/pycharm/

### Vim/Neovim (Advanced)
**Free | Terminal-based**
- Ubiquitous on servers
- Steep learning curve
- Highly customizable
- Worth learning basics

---

## Terminal and Shell

### Terminal Emulators

**Linux**:
- Default GNOME Terminal (good)
- Terminator (split panes)
- Alacritty (GPU-accelerated)

**macOS**:
- iTerm2 (highly recommended)
- Default Terminal (adequate)

**Windows**:
- Windows Terminal (recommended)
- ConEmu
- Hyper

### Shell Configuration

**Zsh with Oh My Zsh (Recommended)**:
```bash
# Install Zsh
sudo apt install zsh  # Ubuntu
brew install zsh      # macOS

# Install Oh My Zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# Recommended plugins in ~/.zshrc:
plugins=(git docker docker-compose kubectl python pip)

# Recommended theme:
ZSH_THEME="robbyrussell"  # or "agnoster"
```

**Useful Zsh Plugins**:
- zsh-autosuggestions
- zsh-syntax-highlighting
- zsh-completions

### Terminal Multiplexer

**tmux**:
```bash
# Install
sudo apt install tmux  # Ubuntu
brew install tmux      # macOS

# Basic commands
tmux                    # start session
tmux ls                # list sessions
tmux attach            # reattach
Ctrl+b d               # detach
Ctrl+b %               # split vertical
Ctrl+b "               # split horizontal
```

---

## Container Tools

### Docker Desktop
**Free for personal use | Cross-platform**
- Download: https://www.docker.com/products/docker-desktop
- Includes Docker Engine, Docker Compose, Kubernetes
- GUI for managing containers

**Installation (Ubuntu)**:
```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### Docker Compose
**Free**
- Comes with Docker Desktop
- Standalone installation:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Dive - Docker Image Analysis
**Free**
```bash
# Install
brew install dive  # macOS
# Ubuntu: download from GitHub releases

# Analyze image layers
dive myimage:latest
```

### Portainer (Docker Management UI)
**Free**
```bash
docker volume create portainer_data
docker run -d -p 9000:9000 --name=portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce
```

---

## Kubernetes Tools

### kubectl
**Free | Official CLI**
```bash
# Install (Linux)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install (macOS)
brew install kubectl

# Verify
kubectl version --client
```

### Local Kubernetes Clusters

**kind (Kubernetes in Docker)**:
```bash
# Install
brew install kind  # macOS
# Linux: download from GitHub

# Create cluster
kind create cluster --name dev
kind get clusters
kind delete cluster --name dev
```

**minikube**:
```bash
# Install
brew install minikube  # macOS
# Ubuntu: download from GitHub

# Start
minikube start
minikube status
minikube dashboard  # Web UI
minikube stop
```

**Docker Desktop Kubernetes**:
- Enable in Docker Desktop settings
- Single-node cluster
- Easy to use

### kubectx and kubens
**Free | Context and namespace switching**
```bash
# Install
brew install kubectx  # macOS

# Usage
kubectx                # list contexts
kubectx dev            # switch to dev context
kubens                 # list namespaces
kubens production      # switch namespace
```

### k9s - Kubernetes CLI UI
**Free**
```bash
# Install
brew install derailed/k9s/k9s  # macOS

# Run
k9s
```

### Lens - Kubernetes IDE
**Free**
- Download: https://k8slens.dev/
- Visual Kubernetes management
- Cluster metrics and logs
- Multi-cluster support

### Helm
**Free | Package manager for Kubernetes**
```bash
# Install
brew install helm  # macOS
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash  # Linux

# Usage
helm repo add stable https://charts.helm.sh/stable
helm search repo <chart>
helm install myrelease stable/<chart>
```

---

## Version Control

### Git
**Free | Included in most OS**
```bash
# Install
sudo apt install git  # Ubuntu
brew install git      # macOS

# Configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

### GitHub CLI (gh)
**Free**
```bash
# Install
brew install gh       # macOS
sudo apt install gh   # Ubuntu

# Authenticate
gh auth login

# Usage
gh repo create
gh pr create
gh pr list
gh issue create
```

### GitKraken (Git GUI)
**Free for public repos | Paid for private**
- Download: https://www.gitkraken.com/
- Visual Git interface
- Merge conflict resolution

### SourceTree (Git GUI)
**Free**
- Download: https://www.sourcetreeapp.com/
- Alternative to GitKraken

---

## Python Development

### Python Version Management

**pyenv**:
```bash
# Install
curl https://pyenv.run | bash

# Add to shell configuration
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python versions
pyenv install 3.9.16
pyenv install 3.11.2
pyenv global 3.11.2
```

### Virtual Environments

**venv (built-in)**:
```bash
# Create
python -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

**virtualenvwrapper** (recommended):
```bash
# Install
pip install virtualenvwrapper

# Add to ~/.bashrc or ~/.zshrc
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# Usage
mkvirtualenv myproject
workon myproject
deactivate
rmvirtualenv myproject
```

### Python Tools

**Poetry** (dependency management):
```bash
# Install
curl -sSL https://install.python-poetry.org | python3 -

# Usage
poetry new myproject
poetry add requests
poetry install
poetry run python app.py
```

**Black** (code formatter):
```bash
pip install black
black myfile.py
black .
```

**Flake8** (linter):
```bash
pip install flake8
flake8 myfile.py
```

**Pylint** (linter):
```bash
pip install pylint
pylint myfile.py
```

**pytest** (testing):
```bash
pip install pytest pytest-cov
pytest
pytest --cov=src tests/
```

**ipython** (enhanced Python shell):
```bash
pip install ipython
ipython
```

---

## Monitoring and Debugging

### Prometheus
**Free | Monitoring system**
```bash
# Docker
docker run -d -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Grafana
**Free | Visualization platform**
```bash
# Docker
docker run -d -p 3000:3000 grafana/grafana
```

### htop
**Free | Process viewer**
```bash
sudo apt install htop
htop
```

### ctop
**Free | Container monitoring**
```bash
sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 \
  -O /usr/local/bin/ctop
sudo chmod +x /usr/local/bin/ctop
ctop
```

### Sentry (Error Tracking)
**Free tier available**
- Sign up: https://sentry.io/
- Python integration:
```bash
pip install sentry-sdk
```

---

## API Development and Testing

### Postman
**Free tier**
- Download: https://www.postman.com/
- API testing and development
- Collection sharing
- Environment variables

### Insomnia
**Free | Open source**
- Download: https://insomnia.rest/
- Alternative to Postman
- GraphQL support

### HTTPie
**Free | CLI HTTP client**
```bash
# Install
pip install httpie

# Usage
http GET https://api.github.com
http POST https://httpbin.org/post name=John
```

### curl
**Free | Built-in**
```bash
curl https://api.github.com
curl -X POST -H "Content-Type: application/json" \
  -d '{"key":"value"}' https://httpbin.org/post
```

---

## Database Tools

### pgAdmin (PostgreSQL)
**Free**
- Download: https://www.pgadmin.org/
- GUI for PostgreSQL

### DBeaver
**Free | Universal database tool**
- Download: https://dbeaver.io/
- Supports multiple databases
- SQL editor and visualizer

### Redis Desktop Manager
**Free/Paid**
- Redis GUI client
- Alternatives: RedisInsight (free)

### MongoDB Compass
**Free**
- Official MongoDB GUI
- Download: https://www.mongodb.com/products/compass

---

## Cloud Platforms

### AWS CLI
**Free**
```bash
# Install
pip install awscli

# Configure
aws configure
```

### Google Cloud SDK
**Free**
```bash
# Install
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init
```

### Azure CLI
**Free**
```bash
# Install
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login
```

---

## Productivity Tools

### Notion
**Free for personal**
- Note-taking and documentation
- Project management
- Knowledge base

### Obsidian
**Free**
- Markdown-based notes
- Local-first
- Graph view for connections

### Draw.io (diagrams.net)
**Free**
- Architecture diagrams
- Flowcharts
- Online or desktop

### Excalidraw
**Free**
- Sketch-style diagrams
- Online: https://excalidraw.com/

---

## Recommended Setup for Beginners

### Minimal Setup
1. **OS**: Ubuntu 22.04 or macOS
2. **IDE**: VSCode with Python and Docker extensions
3. **Terminal**: Default with Git
4. **Docker**: Docker Desktop
5. **K8s**: kind or minikube
6. **Python**: pyenv + venv

### Full Setup
All of the above plus:
- Zsh with Oh My Zsh
- kubectx/kubens
- k9s
- Postman
- DBeaver
- Prometheus + Grafana (Docker)

---

## Installation Scripts

### Quick Setup Script (Ubuntu)
```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install basics
sudo apt install -y git curl wget build-essential

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install VSCode
sudo snap install code --classic

echo "Setup complete! Please log out and back in for Docker group changes."
```

---

## Browser Extensions

### Chrome/Edge Extensions
- **JSON Formatter** - Pretty print JSON
- **Wappalyzer** - Identify technologies
- **React/Vue DevTools** - For frontend debugging
- **Lighthouse** - Performance auditing

---

## Additional Resources

- [VSCode Tips and Tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks)
- [Oh My Zsh Plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins)
- [awesome-docker](https://github.com/veggiemonk/awesome-docker)
- [awesome-kubernetes](https://github.com/ramitsurana/awesome-kubernetes)

---

**Remember**: Start with the minimal setup and add tools as you need them. Don't get overwhelmed trying to install everything at once!
