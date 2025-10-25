# Lecture 06: Linux Networking and System Services

## Table of Contents
1. [Introduction](#introduction)
2. [System Services and systemd](#system-services-and-systemd)
3. [Linux Networking Fundamentals](#linux-networking-fundamentals)
4. [Network Configuration](#network-configuration)
5. [Firewall Management](#firewall-management)
6. [Monitoring Services and Logs](#monitoring-services-and-logs)
7. [Scheduled Tasks and Automation](#scheduled-tasks-and-automation)
8. [AI Infrastructure Applications](#ai-infrastructure-applications)
9. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

As an AI Infrastructure Engineer, understanding Linux networking and system services is essential for deploying and managing ML applications. You'll need to configure services, manage networking for distributed training, set up monitoring, and automate maintenance tasks.

This lecture covers systemd service management, Linux networking basics, firewall configuration, and task automation - all critical skills for running production ML infrastructure.

### Learning Objectives

By the end of this lecture, you will:
- Understand and manage systemd services for ML applications
- Configure Linux networking for AI infrastructure
- Set up and manage firewalls for ML services
- Monitor system services and analyze logs
- Schedule automated tasks using cron and systemd timers
- Apply these concepts to real-world ML deployment scenarios

### Prerequisites
- Completion of Lectures 01-05 in this module
- Basic understanding of Linux command line
- Access to a Linux system with sudo privileges

**Duration**: 90 minutes
**Difficulty**: Intermediate

---

## 1. System Services and systemd

### What is systemd?

**systemd** is the modern init system and service manager for Linux. It manages system services, handles boot process, and controls system states.

```
Why systemd matters for AI Infrastructure:
├── Start/stop ML inference services
├── Ensure services restart after crashes
├── Manage dependencies (database → API → model server)
├── Control resource limits for GPU processes
└── Monitor service health automatically
```

### Understanding Units

systemd uses **units** to represent resources. The main types:

| Unit Type | Extension | Purpose | AI Infrastructure Example |
|-----------|-----------|---------|---------------------------|
| Service | `.service` | Long-running processes | ML model serving API |
| Timer | `.timer` | Scheduled tasks | Model retraining jobs |
| Socket | `.socket` | Network/IPC sockets | API endpoints |
| Mount | `.mount` | Filesystem mounts | Model storage volumes |
| Target | `.target` | Unit grouping | ML infrastructure stack |

### Essential systemctl Commands

```bash
# View all running services
systemctl list-units --type=service --state=running

# Check status of a service
systemctl status nginx

# Start/stop/restart services
sudo systemctl start ml-api
sudo systemctl stop ml-api
sudo systemctl restart ml-api

# Enable service to start on boot
sudo systemctl enable ml-api

# Disable automatic startup
sudo systemctl disable ml-api

# Reload configuration without restart
sudo systemctl reload nginx

# View service logs
journalctl -u ml-api

# Follow logs in real-time
journalctl -u ml-api -f

# View failed services
systemctl --failed
```

### Creating a systemd Service for ML Applications

**Example: ML Model Serving API**

Create `/etc/systemd/system/ml-inference-api.service`:

```ini
[Unit]
Description=ML Inference API Service
After=network.target
Requires=postgresql.service
# Ensures database starts before API

[Service]
Type=simple
User=mluser
Group=mlgroup
WorkingDirectory=/opt/ml-api

# Environment variables
Environment="MODEL_PATH=/models/production/model.onnx"
Environment="PORT=8000"
EnvironmentFile=/etc/ml-api/config.env

# Start command
ExecStart=/opt/ml-api/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000

# Resource limits (important for GPU workloads)
CPUQuota=200%
MemoryLimit=4G

# Restart policy
Restart=on-failure
RestartSec=10s

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ml-api

[Install]
WantedBy=multi-user.target
```

**Activate the service:**

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Start the service
sudo systemctl start ml-inference-api

# Enable on boot
sudo systemctl enable ml-inference-api

# Check status
systemctl status ml-inference-api
```

### Service Dependencies

Define service order and dependencies:

```ini
[Unit]
Description=ML Training Orchestrator
# Wait for these to start first
After=network.target postgresql.service redis.service
# Fail if these aren't available
Requires=postgresql.service
# Optional dependencies
Wants=prometheus.service
```

**Common dependency directives:**
- `After=` - Start after these units
- `Before=` - Start before these units
- `Requires=` - Hard dependency (fail if not available)
- `Wants=` - Soft dependency (continue if not available)

---

## 2. Linux Networking Fundamentals

### Network Interfaces

View network interfaces:

```bash
# Show all network interfaces (modern)
ip addr show

# Show specific interface
ip addr show eth0

# Legacy command (still widely used)
ifconfig

# Show interface statistics
ip -s link show eth0
```

**Common interface types in ML infrastructure:**
- `eth0`, `ens33` - Physical Ethernet
- `lo` - Loopback (127.0.0.1)
- `docker0` - Docker bridge network
- `br-*` - Custom bridge networks
- `veth*` - Virtual ethernet (container pairs)

### IP Address Management

```bash
# Assign IP address temporarily
sudo ip addr add 192.168.1.100/24 dev eth0

# Remove IP address
sudo ip addr del 192.168.1.100/24 dev eth0

# Bring interface up/down
sudo ip link set eth0 up
sudo ip link set eth0 down
```

### Routing

```bash
# Display routing table
ip route show

# Add static route
sudo ip route add 10.0.0.0/24 via 192.168.1.1

# Delete route
sudo ip route del 10.0.0.0/24

# Show default gateway
ip route | grep default
```

**Example routing scenario - Multi-GPU training cluster:**

```
GPU Cluster Architecture:
┌──────────────────────────┐
│  Master Node             │
│  192.168.10.1            │  ← Coordinates training
│  Default route via       │
│  gateway 10.0.0.1        │
└────────┬─────────────────┘
         │
    ┌────┴────┬────────┬───────┐
    │         │        │       │
┌───▼────┐ ┌─▼─────┐ ┌▼──────┐ │
│Worker 1│ │Worker2│ │Worker3│ ...
│.10.11  │ │.10.12 │ │.10.13 │
└────────┘ └───────┘ └───────┘
```

### DNS Configuration

```bash
# View DNS servers
cat /etc/resolv.conf

# Test DNS resolution
nslookup api.openai.com
dig @8.8.8.8 huggingface.co

# Flush DNS cache (systemd-resolved)
sudo systemd-resolve --flush-caches
```

### Network Testing and Troubleshooting

```bash
# Test connectivity
ping -c 4 google.com

# Test specific port
telnet api.example.com 443
nc -zv api.example.com 443

# Trace network path
traceroute google.com
mtr google.com  # Better interactive version

# Show listening ports
sudo netstat -tulpn
sudo ss -tulpn  # Modern alternative

# Show active connections
ss -tan

# Check which process uses a port
sudo lsof -i :8080
```

**ML Infrastructure Example - Check model serving API:**

```bash
# Is the API port open?
sudo ss -tulpn | grep 8000

# Can we connect?
curl http://localhost:8000/health

# Check response time
time curl http://localhost:8000/predict -X POST \
  -d '{"input": [1, 2, 3, 4, 5]}'

# View API connections
ss -tan | grep :8000
```

---

## 3. Network Configuration

### Persistent Configuration (Ubuntu/Debian with Netplan)

Modern Ubuntu uses **Netplan** for network configuration.

Edit `/etc/netplan/01-netcfg.yaml`:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

Apply configuration:

```bash
# Test configuration (doesn't apply)
sudo netplan try

# Apply configuration
sudo netplan apply
```

### Persistent Configuration (RHEL/CentOS)

Edit `/etc/sysconfig/network-scripts/ifcfg-eth0`:

```ini
DEVICE=eth0
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.1.100
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
DNS2=8.8.4.4
```

Restart networking:

```bash
sudo systemctl restart NetworkManager
```

### Hostname Configuration

```bash
# View current hostname
hostname
hostnamectl

# Set hostname
sudo hostnamectl set-hostname ml-gpu-node-01

# Edit /etc/hosts for local resolution
sudo nano /etc/hosts
# Add: 192.168.1.100 ml-gpu-node-01
```

---

## 4. Firewall Management

### firewalld (RHEL/CentOS/Fedora)

```bash
# Check firewall status
sudo firewall-cmd --state

# List all zones
sudo firewall-cmd --get-zones

# View active zones
sudo firewall-cmd --get-active-zones

# List rules in a zone
sudo firewall-cmd --zone=public --list-all

# Allow HTTP traffic
sudo firewall-cmd --zone=public --add-service=http --permanent

# Allow custom port (ML API on 8000)
sudo firewall-cmd --zone=public --add-port=8000/tcp --permanent

# Allow port range (distributed training)
sudo firewall-cmd --zone=public --add-port=6000-6100/tcp --permanent

# Remove a rule
sudo firewall-cmd --zone=public --remove-port=8000/tcp --permanent

# Reload firewall
sudo firewall-cmd --reload
```

### ufw (Ubuntu/Debian)

UFW (Uncomplicated Firewall) is simpler:

```bash
# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose

# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow ML API port
sudo ufw allow 8000/tcp

# Allow from specific IP
sudo ufw allow from 192.168.1.50 to any port 5432

# Allow port range
sudo ufw allow 6000:6100/tcp

# Deny a port
sudo ufw deny 3306/tcp

# Delete a rule
sudo ufw delete allow 8000/tcp

# Reset all rules
sudo ufw reset
```

### iptables (Low-level firewall)

```bash
# View current rules
sudo iptables -L -v -n

# Allow incoming HTTP
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Block specific IP
sudo iptables -A INPUT -s 192.168.1.100 -j DROP

# Save rules (Ubuntu)
sudo iptables-save > /etc/iptables/rules.v4
```

**ML Infrastructure Firewall Example:**

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow ML API
sudo ufw allow 8000/tcp

# Allow Prometheus metrics
sudo ufw allow from 192.168.1.0/24 to any port 9090

# Allow distributed training communication
sudo ufw allow from 192.168.10.0/24 to any port 6000:6100/tcp

# Allow Kubernetes API (if applicable)
sudo ufw allow 6443/tcp

# Enable firewall
sudo ufw enable
```

---

## 5. Monitoring Services and Logs

### systemd Journal (journalctl)

The journal stores logs from all systemd services:

```bash
# View all logs
journalctl

# View logs for specific service
journalctl -u ml-api

# Follow logs in real-time
journalctl -u ml-api -f

# View logs since boot
journalctl -b

# View logs from specific time
journalctl --since "2024-01-01"
journalctl --since "1 hour ago"
journalctl --since "2024-01-15 14:00" --until "2024-01-15 15:00"

# Filter by priority
journalctl -p err  # Errors only
journalctl -p warning  # Warnings and above

# Show only kernel messages
journalctl -k

# Disk usage
journalctl --disk-usage

# Vacuum old logs
sudo journalctl --vacuum-time=2weeks
sudo journalctl --vacuum-size=500M
```

### Traditional Log Files

```bash
# System logs location
/var/log/syslog       # General system logs (Debian/Ubuntu)
/var/log/messages     # General system logs (RHEL/CentOS)
/var/log/auth.log     # Authentication logs
/var/log/kern.log     # Kernel logs
/var/log/nginx/       # Nginx logs
/var/log/apache2/     # Apache logs

# View logs
tail -f /var/log/syslog
less /var/log/auth.log

# Search logs
grep "ERROR" /var/log/syslog
grep -i "failed" /var/log/auth.log
```

### Monitoring Service Health

```bash
# Check if service is running
systemctl is-active ml-api

# Check if service is enabled
systemctl is-enabled ml-api

# View service start time
systemctl show ml-api -p ActiveEnterTimestamp

# View resource usage
systemctl status ml-api | grep -E "Memory|CPU"

# All failed services
systemctl list-units --state=failed
```

---

## 6. Scheduled Tasks and Automation

### cron - Traditional Task Scheduler

#### Cron Syntax

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

#### Common Patterns

```bash
# Every minute
* * * * * /path/to/script.sh

# Every hour at minute 0
0 * * * * /path/to/script.sh

# Every day at 2:30 AM
30 2 * * * /path/to/backup.sh

# Every Monday at 9:00 AM
0 9 * * 1 /path/to/weekly-report.sh

# First day of every month
0 0 1 * * /path/to/monthly-task.sh

# Every 15 minutes
*/15 * * * * /path/to/check-health.sh

# Multiple times per day (6 AM, 12 PM, 6 PM)
0 6,12,18 * * * /path/to/sync-models.sh
```

#### Managing Cron Jobs

```bash
# Edit user crontab
crontab -e

# List user cron jobs
crontab -l

# Remove all cron jobs
crontab -r

# Edit system-wide crontab
sudo nano /etc/crontab

# User-specific cron files
/var/spool/cron/crontabs/username

# System cron directories
/etc/cron.daily/      # Daily scripts
/etc/cron.hourly/     # Hourly scripts
/etc/cron.weekly/     # Weekly scripts
/etc/cron.monthly/    # Monthly scripts
```

#### ML Infrastructure Cron Examples

```bash
# Retrain model nightly at 2 AM
0 2 * * * /opt/ml/scripts/retrain-model.sh >> /var/log/ml-training.log 2>&1

# Check GPU health every 5 minutes
*/5 * * * * /usr/local/bin/check-gpu-health.sh

# Backup models daily
0 1 * * * /opt/ml/scripts/backup-models.sh

# Clear old prediction logs weekly
0 3 * * 0 find /var/log/predictions -mtime +7 -delete

# Update model metrics hourly
0 * * * * /opt/ml/scripts/update-metrics.sh
```

### systemd Timers - Modern Alternative

Systemd timers are more powerful and flexible than cron.

#### Create a Timer Unit

**Example: Model Retraining**

Create `/etc/systemd/system/model-retrain.service`:

```ini
[Unit]
Description=Retrain ML Model

[Service]
Type=oneshot
ExecStart=/opt/ml/scripts/retrain.sh
User=mluser
StandardOutput=journal
```

Create `/etc/systemd/system/model-retrain.timer`:

```ini
[Unit]
Description=Run model retraining daily
Requires=model-retrain.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true
# Run immediately if system was off during scheduled time

[Install]
WantedBy=timers.target
```

**Activate the timer:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer (NOT the service)
sudo systemctl enable model-retrain.timer
sudo systemctl start model-retrain.timer

# Check timer status
systemctl status model-retrain.timer

# List all timers
systemctl list-timers

# View when timer will next run
systemctl list-timers model-retrain.timer
```

#### Timer Calendar Syntax

```ini
# Daily at 2:30 AM
OnCalendar=*-*-* 02:30:00

# Every 15 minutes
OnCalendar=*:0/15

# Mondays at 9 AM
OnCalendar=Mon 09:00

# First day of month
OnCalendar=*-*-01 00:00:00

# Weekdays at 8 AM
OnCalendar=Mon..Fri 08:00
```

---

## 7. AI Infrastructure Applications

### Use Case 1: ML Model Serving with Auto-Restart

**Service file:** `/etc/systemd/system/model-server.service`

```ini
[Unit]
Description=TensorFlow Serving for Production Models
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=mluser
ExecStartPre=/usr/bin/docker pull tensorflow/serving:latest
ExecStart=/usr/bin/docker run --rm \
  --name tf-serving \
  -p 8501:8501 \
  -v /models:/models \
  tensorflow/serving --model_config_file=/models/models.config

ExecStop=/usr/bin/docker stop tf-serving

Restart=always
RestartSec=10s

# Resource limits
CPUQuota=400%
MemoryLimit=8G

[Install]
WantedBy=multi-user.target
```

### Use Case 2: Automated Model Retraining Pipeline

**Timer:** Daily retraining at 2 AM with metrics upload

```bash
# Create /opt/ml/scripts/retrain-pipeline.sh
#!/bin/bash
set -e

echo "[$(date)] Starting model retraining..."

# Pull latest data
python /opt/ml/pull_data.py

# Train model
python /opt/ml/train.py --config /opt/ml/config/prod.yaml

# Validate model
python /opt/ml/validate.py

# Deploy if validation passes
if [ $? -eq 0 ]; then
    echo "Validation passed, deploying model..."
    python /opt/ml/deploy.py
    systemctl restart model-server
else
    echo "Validation failed, keeping previous model"
    exit 1
fi

echo "[$(date)] Retraining complete"
```

**Schedule with cron:**

```bash
# Retrain daily at 2 AM
0 2 * * * /opt/ml/scripts/retrain-pipeline.sh >> /var/log/ml-retrain.log 2>&1
```

### Use Case 3: GPU Health Monitoring

**Script:** `/usr/local/bin/monitor-gpus.sh`

```bash
#!/bin/bash

# Check GPU health
nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,utilization.memory \
  --format=csv,noheader | while read temp util_gpu util_mem; do

  # Alert if temperature > 85°C
  if [ "$temp" -gt 85 ]; then
    echo "WARNING: GPU temperature $temp°C" | systemd-cat -t gpu-monitor -p warning
    # Send alert (email, Slack, etc.)
  fi

  # Log metrics to monitoring system
  curl -X POST http://prometheus-pushgateway:9091/metrics/job/gpu-health \
    -d "gpu_temperature $temp"
done
```

**Cron job:** Run every 2 minutes

```bash
*/2 * * * * /usr/local/bin/monitor-gpus.sh
```

### Use Case 4: Firewall for Multi-Tenant ML Platform

```bash
#!/bin/bash
# setup-ml-firewall.sh

# Allow SSH
ufw allow 22/tcp

# Allow public API
ufw allow 443/tcp

# Allow internal ML services from private network
ufw allow from 10.0.0.0/8 to any port 8000:9000 proto tcp

# Allow Prometheus scraping from monitoring subnet
ufw allow from 172.16.0.0/12 to any port 9090:9100 proto tcp

# Allow distributed training within cluster
ufw allow from 192.168.100.0/24 to any port 6000:6100 proto tcp

# Rate limiting for API (prevent DDoS)
ufw limit 443/tcp

# Enable firewall
ufw --force enable

echo "ML platform firewall configured"
```

---

## 8. Best Practices

### Service Management

1. **Use systemd for production services**
   - Better logging and monitoring
   - Automatic restarts
   - Resource limiting
   - Dependency management

2. **Set appropriate restart policies**
   ```ini
   Restart=on-failure  # Restart only on crashes
   Restart=always      # Always restart
   RestartSec=10s      # Wait 10s before restart
   ```

3. **Limit resources to prevent resource exhaustion**
   ```ini
   CPUQuota=200%     # Maximum 2 CPU cores
   MemoryLimit=4G    # Maximum 4GB RAM
   TasksMax=100      # Limit number of processes
   ```

4. **Enable services at boot for critical infrastructure**
   ```bash
   sudo systemctl enable ml-api
   ```

### Networking

1. **Use static IPs for servers, DHCP for clients**
2. **Document network topology and IP assignments**
3. **Monitor network bandwidth for training/inference**
4. **Use private networks for internal ML communication**
5. **Implement proper DNS for service discovery**

### Firewall

1. **Default deny, explicit allow**
   ```bash
   ufw default deny incoming
   ufw default allow outgoing
   ```

2. **Restrict by IP when possible**
   ```bash
   ufw allow from 192.168.1.0/24 to any port 5432
   ```

3. **Use different zones/rules for different trust levels**
   - Public zone: HTTPS only
   - Internal zone: ML APIs, databases
   - Admin zone: SSH, monitoring

4. **Regularly review and audit rules**
   ```bash
   ufw status numbered
   firewall-cmd --list-all
   ```

### Logging and Monitoring

1. **Centralize logs for correlation**
   - Use syslog forwarding
   - Aggregate with ELK stack or Loki

2. **Set up log rotation**
   ```bash
   # /etc/logrotate.d/ml-api
   /var/log/ml-api/*.log {
       daily
       rotate 7
       compress
       delaycompress
       missingok
       notifempty
   }
   ```

3. **Monitor service health proactively**
   ```bash
   # Check services every 5 minutes
   */5 * * * * systemctl is-active ml-api || systemctl restart ml-api
   ```

### Automation

1. **Use timers instead of cron when possible**
   - Better integration with systemd
   - More flexible scheduling
   - Automatic logging

2. **Make scripts idempotent**
   - Safe to run multiple times
   - Check state before acting

3. **Add error handling**
   ```bash
   set -euo pipefail  # Exit on error, undefined vars, pipe failures
   ```

4. **Log all automated tasks**
   ```bash
   exec > >(tee -a /var/log/automation.log)
   exec 2>&1
   ```

---

## 9. Summary and Key Takeaways

### Core Concepts

1. **systemd** is the modern service manager
   - Manages services, timers, sockets, and more
   - Use `systemctl` for service control
   - Create `.service` files for ML applications

2. **Linux networking** enables distributed ML
   - Configure interfaces with `ip` or Netplan
   - Understand routing for multi-node training
   - Use DNS for service discovery

3. **Firewalls** protect ML infrastructure
   - Use `ufw` (Ubuntu) or `firewalld` (RHEL)
   - Default deny, explicit allow
   - Restrict by IP and port

4. **Logging** provides visibility
   - Use `journalctl` for systemd services
   - Forward logs to centralized systems
   - Rotate logs to manage disk space

5. **Automation** reduces toil
   - Use cron or systemd timers
   - Automate model retraining, backups, monitoring
   - Make scripts idempotent and logged

### Practical Skills Gained

✅ Create and manage systemd services for ML applications
✅ Configure networking for distributed training
✅ Set up firewalls for secure ML infrastructure
✅ Monitor service health and analyze logs
✅ Automate repetitive tasks with cron/timers
✅ Apply these skills to real-world ML deployments

### Next Steps

- **Practice**: Set up a simple ML API as a systemd service
- **Exercise**: Configure networking for a multi-node training cluster
- **Challenge**: Automate model retraining with a systemd timer
- **Explore**: Review the exercises in this module for hands-on practice

### Additional Resources

- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/)
- [Red Hat Enterprise Linux Networking Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/)
- [Ubuntu Server Guide - Networking](https://ubuntu.com/server/docs/network-introduction)
- [systemd for Administrators](https://www.freedesktop.org/wiki/Software/systemd/)
- [Linux Firewall Tutorial - iptables, firewalld, ufw](https://wiki.archlinux.org/title/Firewall)

---

**Congratulations!** You now have a solid foundation in Linux networking and system services for AI infrastructure. These skills are essential for deploying, managing, and automating production ML systems.

**Next Lecture**: Module 003 - Git Version Control
