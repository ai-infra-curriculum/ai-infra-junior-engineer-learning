# Lecture 08: Networking Fundamentals

## Table of Contents
1. [Introduction](#introduction)
2. [TCP/IP Networking Basics](#tcpip-networking-basics)
3. [Network Configuration](#network-configuration)
4. [SSH and Remote Access](#ssh-and-remote-access)
5. [Network Diagnostics and Troubleshooting](#network-diagnostics-and-troubleshooting)
6. [Firewall Basics](#firewall-basics)
7. [AI Infrastructure Networking](#ai-infrastructure-networking)
8. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Networking is fundamental for AI infrastructure. You'll configure networks for distributed training, set up remote access to GPU servers, troubleshoot connectivity issues, and secure ML services. Understanding Linux networking empowers you to build, maintain, and troubleshoot production AI systems.

This lecture covers essential networking concepts and practical skills for AI infrastructure engineering.

### Learning Objectives

By the end of this lecture, you will:
- Understand TCP/IP fundamentals and network addressing
- Configure network interfaces and routing
- Use SSH for secure remote access
- Diagnose network issues with command-line tools
- Configure firewalls for ML services
- Apply networking concepts to distributed AI infrastructure
- Troubleshoot common network problems

### Prerequisites
- Lectures 01-07 (Linux fundamentals through text processing)
- Basic understanding of IP addresses and networks
- Access to a Linux system with network connectivity

### Why Networking for AI Infrastructure?

**Distributed Training**: Multi-node training requires reliable, high-bandwidth networking

**Remote Access**: Manage GPU servers and training jobs from anywhere

**Model Serving**: Deploy inference APIs accessible over the network

**Data Transfer**: Move large datasets between storage and compute

**Security**: Protect ML services from unauthorized access

**Troubleshooting**: Debug connectivity issues in complex infrastructure

**Duration**: 120 minutes
**Difficulty**: Intermediate

---

## TCP/IP Networking Basics

### The OSI and TCP/IP Models

**OSI Model** (7 layers):
```
7. Application  - HTTP, SSH, FTP
6. Presentation - Encryption, compression
5. Session      - Connection management
4. Transport    - TCP, UDP
3. Network      - IP, routing
2. Data Link    - Ethernet, MAC addresses
1. Physical     - Cables, signals
```

**TCP/IP Model** (4 layers - practical focus):
```
4. Application  - HTTP, SSH, DNS
3. Transport    - TCP, UDP
2. Internet     - IP, ICMP
1. Link         - Ethernet, WiFi
```

### IP Addresses

**IPv4 Address**: 32-bit address (e.g., 192.168.1.100)
- 4 octets, each 0-255
- ~4.3 billion unique addresses

**IPv6 Address**: 128-bit address (e.g., 2001:0db8:85a3::8a2e:0370:7334)
- Much larger address space
- Increasingly important

**IP Address Classes** (historical but still referenced):

| Class | Range | Default Mask | Use |
|-------|-------|--------------|-----|
| A | 1.0.0.0 - 126.255.255.255 | /8 (255.0.0.0) | Large networks |
| B | 128.0.0.0 - 191.255.255.255 | /16 (255.255.0.0) | Medium networks |
| C | 192.0.0.0 - 223.255.255.255 | /24 (255.255.255.0) | Small networks |

**Private IP Ranges** (not routed on internet):
- 10.0.0.0/8 (10.0.0.0 - 10.255.255.255)
- 172.16.0.0/12 (172.16.0.0 - 172.31.255.255)
- 192.168.0.0/16 (192.168.0.0 - 192.168.255.255)

**Special Addresses**:
- 127.0.0.1 - Loopback (localhost)
- 0.0.0.0 - All interfaces / default route
- 255.255.255.255 - Broadcast

### Subnetting Basics

**CIDR Notation**: IP/prefix (e.g., 192.168.1.0/24)

**Common Subnet Masks**:
- /8 = 255.0.0.0 (16,777,214 hosts)
- /16 = 255.255.0.0 (65,534 hosts)
- /24 = 255.255.255.0 (254 hosts)
- /25 = 255.255.255.128 (126 hosts)
- /26 = 255.255.255.192 (62 hosts)
- /27 = 255.255.255.224 (30 hosts)
- /28 = 255.255.255.240 (14 hosts)

**Example**: 192.168.1.0/24
- Network: 192.168.1.0
- First host: 192.168.1.1
- Last host: 192.168.1.254
- Broadcast: 192.168.1.255
- Total usable: 254 hosts

### Ports and Protocols

**Well-Known Ports** (0-1023):
- 22: SSH
- 80: HTTP
- 443: HTTPS
- 25: SMTP (email)
- 53: DNS
- 21: FTP

**Common Service Ports**:
- 3306: MySQL
- 5432: PostgreSQL
- 6379: Redis
- 27017: MongoDB
- 8080: Alternative HTTP
- 8000: Development servers

**AI/ML Service Ports** (examples):
- 6006: TensorBoard
- 8888: Jupyter Notebook
- 8501: TensorFlow Serving REST
- 8500: TensorFlow Serving gRPC
- 5000: Flask default
- 8000: FastAPI default

**TCP vs UDP**:
- **TCP**: Connection-oriented, reliable, ordered (web, SSH, databases)
- **UDP**: Connectionless, fast, no guarantees (DNS, streaming, gaming)

### DNS (Domain Name System)

**DNS Resolution**:
```
User enters: api.example.com
    ↓
DNS query → DNS server
    ↓
DNS server returns: 203.0.113.42
    ↓
Connection to: 203.0.113.42
```

**DNS Configuration**: `/etc/resolv.conf`
```bash
nameserver 8.8.8.8          # Google DNS
nameserver 8.8.4.4          # Google DNS (secondary)
nameserver 1.1.1.1          # Cloudflare DNS
```

**Testing DNS**:
```bash
# Test DNS resolution
nslookup google.com

# More detailed information
dig google.com

# Query specific DNS server
dig @8.8.8.8 google.com
```

---

## Network Configuration

### Viewing Network Interfaces

**ip command** (modern):
```bash
# Show all interfaces
ip addr show
ip a                            # Short form

# Show specific interface
ip addr show eth0

# Show interface statistics
ip -s link show eth0

# Show brief summary
ip -br addr
```

**ifconfig** (legacy but still common):
```bash
# Show all interfaces
ifconfig

# Show specific interface
ifconfig eth0

# Show interface statistics
ifconfig -a
```

**Example output interpretation**:
```
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
    link/ether 00:1a:2b:3c:4d:5e brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0
    inet6 fe80::21a:2bff:fe3c:4d5e/64 scope link
```

**Key information**:
- `eth0`: Interface name
- `UP`: Interface is active
- `00:1a:2b:3c:4d:5e`: MAC address
- `192.168.1.100/24`: IP address and subnet
- `mtu 1500`: Maximum transmission unit

**Common interface names**:
- `eth0`, `eth1`: Ethernet (old naming)
- `ens33`, `enp0s3`: Ethernet (new predictable naming)
- `wlan0`, `wlp2s0`: Wireless
- `lo`: Loopback (127.0.0.1)
- `docker0`: Docker bridge
- `br-*`: Custom bridges
- `veth*`: Virtual ethernet pairs

### Configuring IP Addresses

**Temporary configuration** (lost after reboot):
```bash
# Assign IP address
sudo ip addr add 192.168.1.100/24 dev eth0

# Remove IP address
sudo ip addr del 192.168.1.100/24 dev eth0

# Bring interface up
sudo ip link set eth0 up

# Bring interface down
sudo ip link set eth0 down

# Alternative with ifconfig
sudo ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up
```

### Persistent Configuration - Netplan (Ubuntu 18.04+)

Configuration files: `/etc/netplan/*.yaml`

**Static IP configuration**:
```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 8.8.4.4
```

**DHCP configuration**:
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: true
```

**Apply configuration**:
```bash
# Test configuration (prompts to confirm)
sudo netplan try

# Apply configuration
sudo netplan apply

# Debug configuration issues
sudo netplan --debug apply
```

### Persistent Configuration - NetworkManager (Most Linux)

**Using nmcli**:
```bash
# Show connections
nmcli connection show

# Show device status
nmcli device status

# Create static IP connection
sudo nmcli connection add type ethernet \
    con-name ml-network \
    ifname eth0 \
    ip4 192.168.1.100/24 \
    gw4 192.168.1.1

# Set DNS servers
sudo nmcli connection modify ml-network \
    ipv4.dns "8.8.8.8 8.8.4.4"

# Activate connection
sudo nmcli connection up ml-network

# Create DHCP connection
sudo nmcli connection add type ethernet \
    con-name dhcp-network \
    ifname eth0
```

### Routing

**View routing table**:
```bash
# Show routes
ip route show
ip r                            # Short form

# Show specific route
ip route get 8.8.8.8

# Alternative
route -n
netstat -rn
```

**Example routing table**:
```
default via 192.168.1.1 dev eth0
192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100
```

**Add/remove routes**:
```bash
# Add static route
sudo ip route add 10.0.0.0/24 via 192.168.1.254

# Delete route
sudo ip route del 10.0.0.0/24

# Add default gateway
sudo ip route add default via 192.168.1.1

# Delete default gateway
sudo ip route del default
```

### Hostname Configuration

```bash
# View current hostname
hostname
hostnamectl

# Set hostname (permanent)
sudo hostnamectl set-hostname ml-gpu-node-01

# Verify
hostnamectl

# Edit hosts file for local resolution
sudo nano /etc/hosts
# Add: 192.168.1.100 ml-gpu-node-01
```

### AI Infrastructure Network Example

**Configure ML training cluster**:

**Master Node** (192.168.10.1):
```yaml
# /etc/netplan/01-netcfg.yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    # Management network
    eth0:
      dhcp4: false
      addresses:
        - 10.0.0.10/24
      routes:
        - to: default
          via: 10.0.0.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]

    # Training network (high-speed)
    eth1:
      dhcp4: false
      addresses:
        - 192.168.10.1/24
```

**Worker Nodes** (192.168.10.11, .12, .13, ...):
```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    # Management network
    eth0:
      dhcp4: true

    # Training network
    eth1:
      dhcp4: false
      addresses:
        - 192.168.10.11/24  # .12, .13, etc. for other workers
      routes:
        - to: 192.168.10.0/24
          via: 192.168.10.1
```

---

## SSH and Remote Access

SSH (Secure Shell) is essential for managing remote systems.

### Basic SSH Usage

**Connect to remote server**:
```bash
# Basic connection
ssh username@hostname
ssh user@192.168.1.100

# Specify port
ssh -p 2222 user@hostname

# Execute single command
ssh user@hostname "ls -la"
ssh user@hostname "nvidia-smi"
```

### SSH Key-Based Authentication

**Generate SSH key pair**:
```bash
# Generate RSA key (4096 bits)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Generate ED25519 key (modern, more secure)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Keys saved to:
# ~/.ssh/id_rsa or ~/.ssh/id_ed25519 (private key)
# ~/.ssh/id_rsa.pub or ~/.ssh/id_ed25519.pub (public key)
```

**Copy public key to server**:
```bash
# Method 1: ssh-copy-id (easiest)
ssh-copy-id user@hostname

# Method 2: Manual copy
cat ~/.ssh/id_rsa.pub | ssh user@hostname "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Method 3: Direct copy
scp ~/.ssh/id_rsa.pub user@hostname:~/.ssh/authorized_keys
```

**Set correct permissions**:
```bash
# On server
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# On client
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

**Test key-based login**:
```bash
# Should login without password
ssh user@hostname
```

### SSH Configuration File

**Client config**: `~/.ssh/config`

```bash
# Default settings for all hosts
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3

# ML GPU Server
Host ml-gpu-1
    HostName 192.168.1.100
    User mluser
    Port 22
    IdentityFile ~/.ssh/ml_gpu_key
    ForwardAgent yes

# Training Cluster Master
Host ml-master
    HostName ml-master.example.com
    User admin
    Port 2222
    IdentityFile ~/.ssh/cluster_key

# All worker nodes
Host ml-worker-*
    User mluser
    Port 22
    IdentityFile ~/.ssh/cluster_key
    StrictHostKeyChecking no
```

**Usage with config**:
```bash
# Simple connection
ssh ml-gpu-1

# Instead of:
ssh -i ~/.ssh/ml_gpu_key -p 22 mluser@192.168.1.100
```

### Secure File Transfer

**scp - Secure Copy**:
```bash
# Copy file to remote
scp local_file.txt user@hostname:/remote/path/

# Copy file from remote
scp user@hostname:/remote/file.txt /local/path/

# Copy directory recursively
scp -r local_directory user@hostname:/remote/path/

# Copy between two remote hosts
scp user1@host1:/path/file.txt user2@host2:/path/

# Copy with specific port
scp -P 2222 file.txt user@hostname:/path/

# Show progress
scp -v file.txt user@hostname:/path/
```

**rsync - Efficient Synchronization**:
```bash
# Basic sync
rsync -avz source/ user@hostname:/destination/

# -a: archive mode (preserve permissions, times, etc.)
# -v: verbose
# -z: compress during transfer

# Sync with progress
rsync -avzP source/ user@hostname:/destination/

# Dry run (test without changes)
rsync -avzn source/ user@hostname:/destination/

# Delete files in destination not in source
rsync -avz --delete source/ user@hostname:/destination/

# Exclude files
rsync -avz --exclude '*.log' --exclude 'tmp/' source/ user@hostname:/dest/

# Resume interrupted transfer
rsync -avz --partial source/ user@hostname:/destination/
```

**ML Data Transfer Examples**:
```bash
# Sync training dataset to GPU server
rsync -avzP /local/datasets/imagenet/ ml-gpu-1:/data/imagenet/

# Sync models to production
rsync -avz --delete /local/models/ production:/models/

# Backup training checkpoints
rsync -avz ml-gpu-1:/experiments/checkpoints/ /backup/checkpoints/

# Sync with bandwidth limit (10MB/s)
rsync -avz --bwlimit=10000 large_dataset/ remote:/data/
```

### SSH Tunneling

**Local port forwarding** (access remote service locally):
```bash
# Forward local port 8888 to remote port 8888
ssh -L 8888:localhost:8888 user@remote-server

# Now access remote Jupyter at: http://localhost:8888

# Forward to different remote host
ssh -L 5432:database-server:5432 user@jump-server
# Access database through jump server
```

**Remote port forwarding** (expose local service remotely):
```bash
# Make local port 8000 accessible on remote port 9000
ssh -R 9000:localhost:8000 user@remote-server

# Useful for demos or temporary access
```

**Dynamic port forwarding** (SOCKS proxy):
```bash
# Create SOCKS proxy on port 9090
ssh -D 9090 user@remote-server

# Configure browser to use localhost:9090 as SOCKS proxy
# All traffic goes through remote server
```

**Persistent SSH tunnels**:
```bash
# Keep tunnel alive
ssh -L 8888:localhost:8888 -N -f user@remote

# -N: Don't execute remote command
# -f: Background process

# Kill tunnel
pkill -f "ssh.*8888:localhost:8888"
```

### SSH Best Practices

**Security**:
```bash
# Use key-based authentication (no passwords)
# Use strong passphrases on private keys
# Use ed25519 keys (modern, secure)
# Disable root login: PermitRootLogin no
# Disable password authentication: PasswordAuthentication no
# Use non-standard SSH port
# Use fail2ban to prevent brute force
```

**Performance**:
```bash
# Enable compression for slow connections
ssh -C user@hostname

# Connection multiplexing (reuse connections)
# In ~/.ssh/config:
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

---

## Network Diagnostics and Troubleshooting

### Connectivity Testing

**ping - Test reachability**:
```bash
# Basic ping
ping google.com

# Limit to 4 packets
ping -c 4 google.com

# Set interval (1 second)
ping -i 1 google.com

# Large packet size
ping -s 1000 google.com

# Flood ping (requires root, use carefully!)
sudo ping -f target

# Ping specific interface
ping -I eth0 192.168.1.1
```

**traceroute - Trace network path**:
```bash
# Trace route to destination
traceroute google.com

# Show IP addresses only
traceroute -n google.com

# Use ICMP instead of UDP
traceroute -I google.com

# Set max hops
traceroute -m 15 google.com
```

**mtr - Continuous traceroute**:
```bash
# Interactive network diagnostic
mtr google.com

# Report mode (10 packets)
mtr -r -c 10 google.com

# No DNS resolution
mtr -n google.com
```

### Port and Service Testing

**telnet - Test port connectivity**:
```bash
# Test if port is open
telnet hostname 80
telnet 192.168.1.100 8080

# If connection succeeds, port is open
# Press Ctrl+] then 'quit' to exit
```

**nc (netcat) - Network swiss army knife**:
```bash
# Test TCP port
nc -zv hostname 80

# Test multiple ports
nc -zv hostname 80 443 8080

# Test UDP port
nc -zvu hostname 53

# Test port range
nc -zv hostname 1-1000

# Listen on port (server mode)
nc -l 8080

# Connect and send data
echo "GET / HTTP/1.0" | nc google.com 80
```

**nmap - Network scanner**:
```bash
# Scan common ports
nmap hostname

# Scan specific ports
nmap -p 22,80,443 hostname

# Scan port range
nmap -p 1-1000 hostname

# Scan all ports
nmap -p- hostname

# Service version detection
nmap -sV hostname

# OS detection
sudo nmap -O hostname

# Scan network range
nmap 192.168.1.0/24
```

### Viewing Active Connections

**netstat - Network statistics** (older):
```bash
# Show all listening ports
netstat -tuln

# Show all connections
netstat -tun

# Show listening TCP ports with programs
sudo netstat -tulpn

# Show routing table
netstat -rn

# Show network statistics
netstat -s
```

**ss - Socket statistics** (modern replacement):
```bash
# Show all TCP connections
ss -ta

# Show all listening sockets
ss -tln

# Show processes
sudo ss -tlnp

# Show specific port
ss -tuln | grep :8080

# Show summary
ss -s

# Show UDP connections
ss -ua

# Filter by state
ss -t state established
ss -t state time-wait
```

**lsof - List open files** (includes network):
```bash
# Show all network connections
sudo lsof -i

# Show specific port
sudo lsof -i :8080

# Show specific protocol
sudo lsof -i tcp
sudo lsof -i udp

# Show specific host
sudo lsof -i @192.168.1.100

# Which process is using port?
sudo lsof -i :22

# All network activity by user
sudo lsof -i -u username
```

### DNS Troubleshooting

```bash
# Test DNS resolution
nslookup google.com

# Detailed DNS query
dig google.com

# Query specific record type
dig google.com A           # IPv4 address
dig google.com AAAA        # IPv6 address
dig google.com MX          # Mail servers
dig google.com NS          # Name servers

# Query specific DNS server
dig @8.8.8.8 google.com

# Reverse DNS lookup
dig -x 8.8.8.8

# Trace DNS resolution
dig +trace google.com

# Short answer only
dig google.com +short
```

### Network Interface Statistics

```bash
# Interface statistics
ip -s link show eth0

# Detailed stats
netstat -i

# Real-time stats
watch -n 1 'ip -s link show eth0'

# Bandwidth monitoring
ifstat
iftop
nload
```

### Troubleshooting Methodology

**1. Check physical/link layer**:
```bash
# Is interface up?
ip link show eth0

# Cable connected?
ethtool eth0 | grep "Link detected"

# Check errors
ip -s link show eth0
```

**2. Check network layer (IP)**:
```bash
# IP configured?
ip addr show eth0

# Can ping gateway?
ping -c 4 192.168.1.1

# Can ping external IP?
ping -c 4 8.8.8.8
```

**3. Check DNS**:
```bash
# Can resolve names?
nslookup google.com

# DNS servers configured?
cat /etc/resolv.conf
```

**4. Check application layer**:
```bash
# Is service listening?
sudo ss -tlnp | grep :80

# Can connect to port?
nc -zv hostname 80

# Check service logs
journalctl -u service-name -n 50
```

### AI Infrastructure Troubleshooting Examples

**Distributed training not connecting**:
```bash
# 1. Check network connectivity between nodes
ping ml-worker-1
ping ml-worker-2

# 2. Check if training port is open
nc -zv ml-worker-1 6000

# 3. Check firewall
sudo ufw status
sudo iptables -L

# 4. Check what's listening
sudo ss -tlnp | grep 6000

# 5. Check logs
journalctl -u training-service -n 100
```

**Cannot access Jupyter notebook**:
```bash
# 1. Is Jupyter running?
ps aux | grep jupyter

# 2. What port is it on?
sudo lsof -i | grep jupyter

# 3. Can you access locally?
curl http://localhost:8888

# 4. Is port open externally?
sudo ufw status

# 5. Test from remote
nc -zv gpu-server 8888

# 6. Use SSH tunnel
ssh -L 8888:localhost:8888 user@gpu-server
```

**Slow data transfer**:
```bash
# 1. Check bandwidth
iperf3 -s                    # On server
iperf3 -c server-ip          # On client

# 2. Check interface speed
ethtool eth0 | grep Speed

# 3. Check for errors
ip -s link show eth0

# 4. Check MTU
ip link show eth0 | grep mtu

# 5. Use rsync with compression
rsync -avz --progress source/ dest/
```

---

## Firewall Basics

Firewalls control network traffic based on rules.

### ufw - Uncomplicated Firewall (Ubuntu/Debian)

**Basic operations**:
```bash
# Enable firewall
sudo ufw enable

# Disable firewall
sudo ufw disable

# Check status
sudo ufw status
sudo ufw status verbose
sudo ufw status numbered       # Show rule numbers
```

**Allow rules**:
```bash
# Allow SSH (important - don't lock yourself out!)
sudo ufw allow 22/tcp
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow http
sudo ufw allow https

# Allow from specific IP
sudo ufw allow from 192.168.1.50

# Allow from specific IP to specific port
sudo ufw allow from 192.168.1.50 to any port 22

# Allow from subnet
sudo ufw allow from 192.168.1.0/24

# Allow port range
sudo ufw allow 6000:6100/tcp
```

**Deny rules**:
```bash
# Deny specific port
sudo ufw deny 3306/tcp

# Deny from IP
sudo ufw deny from 192.168.1.100
```

**Delete rules**:
```bash
# Delete by rule number
sudo ufw status numbered
sudo ufw delete 2

# Delete by specification
sudo ufw delete allow 80/tcp
```

**Default policies**:
```bash
# Deny incoming, allow outgoing (recommended)
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Deny all
sudo ufw default deny incoming
sudo ufw default deny outgoing
```

### Firewall for ML Services

**Basic ML infrastructure**:
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow Jupyter Notebook (restrict to local network)
sudo ufw allow from 192.168.1.0/24 to any port 8888

# Allow TensorBoard (restrict to local network)
sudo ufw allow from 192.168.1.0/24 to any port 6006

# Allow ML API
sudo ufw allow 8000/tcp

# Allow distributed training ports
sudo ufw allow from 192.168.10.0/24 to any port 6000:6100/tcp

# Allow monitoring (Prometheus)
sudo ufw allow from 10.0.0.0/24 to any port 9090/tcp

# Enable firewall
sudo ufw enable
```

**Production API server**:
```bash
# Default deny
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (change port for security)
sudo ufw allow 2222/tcp

# HTTPS only (no HTTP)
sudo ufw allow 443/tcp

# Rate limit SSH (prevent brute force)
sudo ufw limit 2222/tcp

# Enable
sudo ufw enable
```

### firewalld (RHEL/CentOS)

**Basic operations**:
```bash
# Check status
sudo firewall-cmd --state

# Get active zones
sudo firewall-cmd --get-active-zones

# List all rules
sudo firewall-cmd --zone=public --list-all
```

**Add rules**:
```bash
# Allow HTTP
sudo firewall-cmd --zone=public --add-service=http --permanent

# Allow custom port
sudo firewall-cmd --zone=public --add-port=8000/tcp --permanent

# Allow port range
sudo firewall-cmd --zone=public --add-port=6000-6100/tcp --permanent

# Allow from specific IP
sudo firewall-cmd --zone=public --add-rich-rule='rule family="ipv4" source address="192.168.1.50" accept' --permanent

# Reload to apply
sudo firewall-cmd --reload
```

---

## AI Infrastructure Networking

### Distributed Training Network Architecture

**Example: 4-node GPU cluster**

```
                    Internet
                        |
                   [Gateway]
                        |
           ┌────────────┴────────────┐
           |   Management Network    |
           |     (10.0.0.0/24)      |
           └────────────┬────────────┘
                        |
        ┌───────────────┼───────────────┐
        |               |               |
    [Master]        [Worker1]      [Worker2]
    10.0.0.10       10.0.0.11      10.0.0.12
        |               |               |
        └───────────────┼───────────────┘
                        |
           ┌────────────┴────────────┐
           |   Training Network      |
           |   (192.168.10.0/24)     |
           |   (High-speed/InfiniBand)|
           └────────────┬────────────┘
                        |
        ┌───────────────┼───────────────┐
        |               |               |
    192.168.10.1  192.168.10.11   192.168.10.12
```

**Network requirements**:
- **Management**: SSH, monitoring, logging (1 Gbps)
- **Training**: Model updates, gradients (10+ Gbps, InfiniBand ideal)
- **Storage**: Dataset access (10+ Gbps)

### Model Serving Network

**Load-balanced API architecture**:

```
            Internet
                |
           [Load Balancer]
                |
        ┌───────┴───────┐
        |               |
    [API-1]         [API-2]
    (Inference)     (Inference)
        |               |
        └───────┬───────┘
                |
          [Model Store]
          [Monitoring]
```

**Network considerations**:
- **Latency**: Critical for real-time inference
- **Bandwidth**: Large models, high request volume
- **Reliability**: Load balancing, failover
- **Security**: TLS, authentication, rate limiting

### Performance Optimization

**TCP tuning for large transfers**:
```bash
# Increase TCP buffer sizes (add to /etc/sysctl.conf)
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# Apply changes
sudo sysctl -p
```

**MTU optimization**:
```bash
# Check current MTU
ip link show eth0 | grep mtu

# Set jumbo frames (9000 bytes) for high-speed networks
sudo ip link set eth0 mtu 9000

# Test MTU path
ping -M do -s 8972 remote-host
```

### Network Monitoring

```bash
# Monitor bandwidth
iftop -i eth0

# Monitor connections
watch -n 1 'ss -tun | wc -l'

# Log network stats
while true; do
    echo "$(date): $(ip -s link show eth0 | grep 'RX:' -A1)"
    sleep 60
done >> network_stats.log
```

---

## Summary and Key Takeaways

### Concepts Mastered

**TCP/IP Basics**:
- IP addressing and subnetting
- Ports and protocols
- DNS resolution
- TCP vs UDP

**Configuration**:
- View interfaces (ip, ifconfig)
- Configure IPs (Netplan, NetworkManager)
- Routing tables
- Hostname management

**SSH**:
- Remote access
- Key-based authentication
- File transfer (scp, rsync)
- SSH tunneling

**Diagnostics**:
- Connectivity testing (ping, traceroute)
- Port testing (nc, telnet, nmap)
- Connection viewing (ss, netstat, lsof)
- DNS troubleshooting (dig, nslookup)

**Firewall**:
- ufw (Ubuntu/Debian)
- firewalld (RHEL/CentOS)
- Rule management
- Security best practices

### Key Commands

```bash
# View network config
ip addr show
ip route show
cat /etc/resolv.conf

# Test connectivity
ping host
traceroute host
nc -zv host port

# View connections
ss -tuln
sudo lsof -i :port

# SSH
ssh user@host
scp file user@host:/path/
rsync -avz source/ user@host:/dest/

# Firewall
sudo ufw allow port/tcp
sudo ufw status
```

### AI Infrastructure Best Practices

✅ **Use static IPs for servers**: Predictable addressing
✅ **Separate networks**: Management, training, storage
✅ **High-bandwidth for training**: 10+ Gbps for distributed training
✅ **Low latency for inference**: Optimize for real-time response
✅ **Secure SSH access**: Keys only, no passwords
✅ **Firewall by default**: Explicit allow, default deny
✅ **Monitor network health**: Bandwidth, latency, errors
✅ **Document topology**: Network diagrams, IP assignments
✅ **Use SSH tunnels**: Secure access to internal services
✅ **Test thoroughly**: Verify connectivity before production

### Troubleshooting Checklist

1. **Physical/Link**: Interface up? Cable connected?
2. **Network**: IP configured? Can ping gateway?
3. **Routing**: Can reach external IPs?
4. **DNS**: Can resolve names?
5. **Firewall**: Port allowed?
6. **Service**: Is it listening?
7. **Application**: Check logs

### Next Steps

**Congratulations!** You've completed Module 002: Linux Essentials.

**What you've learned**:
- Linux fundamentals and command line
- File system navigation and permissions
- System administration and package management
- Process management and monitoring
- Shell scripting (basic and advanced)
- Text processing with grep, sed, awk
- Networking fundamentals

**Continue learning**:
- Practice these skills daily
- Complete module exercises
- Build automation scripts
- Set up a lab environment
- Move to Module 003: Version Control with Git

### Quick Reference Card

```bash
# Network Info
ip addr show                    # Show IPs
ip route show                   # Show routes
hostname                        # Show hostname

# Testing
ping host                       # Test connectivity
nc -zv host port               # Test port
dig domain                      # DNS lookup

# Connections
ss -tuln                       # Listening ports
sudo lsof -i :port             # Port usage
netstat -rn                    # Routing table

# SSH
ssh user@host                  # Connect
ssh-keygen -t ed25519          # Generate key
ssh-copy-id user@host          # Copy key
scp file user@host:/path/      # Copy file
rsync -avz src/ user@host:dst/ # Sync

# Firewall
sudo ufw allow port/tcp        # Allow port
sudo ufw status                # Check status
sudo ufw enable                # Enable firewall
```

---

**End of Lecture 08: Networking Fundamentals**

**Congratulations on completing Module 002: Linux Essentials!**

You now have a solid foundation in Linux systems, shell scripting, text processing, and networking—all essential skills for AI Infrastructure Engineering.

**Next Module**: Module 003 - Version Control with Git
