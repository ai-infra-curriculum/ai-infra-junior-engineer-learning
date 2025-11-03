# Exercise 09: Linux Networking and Troubleshooting for ML Infrastructure

## Overview
Master essential Linux networking tools and troubleshooting techniques for managing ML infrastructure. Learn to diagnose connectivity issues, secure SSH access, configure firewalls, and analyze network performance problems that commonly affect distributed ML systems.

**Duration:** 3-4 hours
**Difficulty:** Intermediate

## Learning Objectives
By completing this exercise, you will:
- Use modern network tools (ip, ss) to inspect and configure interfaces
- Diagnose network connectivity issues using ping, traceroute, and tcpdump
- Secure SSH access with key-based authentication and hardened configurations
- Configure firewall rules for ML services (APIs, model servers, databases)
- Troubleshoot DNS resolution and latency problems
- Monitor network performance and identify bottlenecks
- Implement network segmentation for security

## Prerequisites
- Linux system (Ubuntu 22.04+ recommended) or VM
- Root/sudo access
- Basic understanding of TCP/IP and networking concepts
- Docker installed (for simulating multi-host scenarios)

## Scenario
You're managing an **ML Platform** with multiple components:
- **Training cluster**: GPU nodes that pull data from storage
- **Model serving API**: REST endpoints accessed by applications
- **Feature store**: Redis cache accessed by serving layer
- **PostgreSQL database**: Stores model metadata
- **Monitoring stack**: Prometheus and Grafana

Users are reporting various issues:
- "Training jobs can't reach the data lake"
- "Model API is slow from certain regions"
- "Database connections timing out"
- "Can't SSH into GPU nodes"

You'll use Linux networking tools to diagnose and fix these problems.

## Tasks

### Task 1: Network Interface Configuration and Inspection

**TODO 1.1:** Inspect current network configuration

```bash
# Modern way to view network interfaces (replaces ifconfig)
ip addr show

# TODO: Identify your primary network interface (usually eth0, ens33, or enp0s3)
PRIMARY_IFACE=$(ip route | grep default | awk '{print $5}')
echo "Primary interface: $PRIMARY_IFACE"

# Show detailed interface info
ip -s link show $PRIMARY_IFACE

# View routing table
ip route show

# TODO: Document output
# - What is your IP address?
# - What is your default gateway?
# - What is your subnet mask (CIDR notation)?
```

**TODO 1.2:** View active network connections

```bash
# Modern replacement for netstat
ss -tulpn

# Break down the flags:
# -t : TCP sockets
# -u : UDP sockets
# -l : Listening sockets
# -p : Show process using the socket
# -n : Show numeric addresses (don't resolve names)

# TODO: Identify what services are listening
# Common ports for ML infrastructure:
# - 5432: PostgreSQL
# - 6379: Redis
# - 8080/8000: HTTP APIs
# - 9090: Prometheus
# - 3000: Grafana

# Filter for specific port
ss -tlnp | grep :8080

# Show established connections
ss -tnp state established
```

**TODO 1.3:** Configure static IP (optional, for VMs)

```bash
# TODO: Check current DHCP configuration
ip addr show $PRIMARY_IFACE

# For Ubuntu with Netplan, edit config
sudo cat > /etc/netplan/01-netcfg.yaml << 'EOF'
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      addresses:
        - 192.168.1.100/24
      gateway4: 192.168.1.1
      nameservers:
        addresses:
          - 8.8.8.8
          - 1.1.1.1
EOF

# TODO: Test configuration without applying
sudo netplan try

# Apply if successful
# sudo netplan apply

# Verify
ip addr show eth0
```

### Task 2: SSH Security Hardening

**TODO 2.1:** Generate and configure SSH key pairs

```bash
# TODO: Generate ED25519 key (more secure than RSA)
ssh-keygen -t ed25519 -C "ml-platform-admin" -f ~/.ssh/ml_platform_key

# Set proper permissions (critical for SSH security)
chmod 700 ~/.ssh
chmod 600 ~/.ssh/ml_platform_key
chmod 644 ~/.ssh/ml_platform_key.pub

# TODO: Add public key to authorized_keys
mkdir -p ~/.ssh
cat ~/.ssh/ml_platform_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Test key-based authentication
ssh -i ~/.ssh/ml_platform_key localhost
```

**TODO 2.2:** Harden SSH daemon configuration

```bash
# TODO: Backup original config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Create hardened SSH config
sudo tee /etc/ssh/sshd_config.d/99-hardening.conf << 'EOF'
# Disable password authentication (key-only)
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Disable root login
PermitRootLogin no

# Use protocol 2 only
Protocol 2

# Limit authentication attempts
MaxAuthTries 3
MaxSessions 5

# Disable X11 forwarding (unless needed)
X11Forwarding no

# Set login grace time
LoginGraceTime 30

# Enable strict mode
StrictModes yes

# Allow only specific users (uncomment and customize)
# AllowUsers mluser dataengineer

# Disable unnecessary features
PermitUserEnvironment no
Compression no

# Set idle timeout (15 minutes)
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

# TODO: Test configuration syntax
sudo sshd -t

# If valid, reload SSH
sudo systemctl reload sshd

# Verify SSH is still running
sudo systemctl status sshd
```

**TODO 2.3:** Configure SSH client for ML infrastructure

```bash
# TODO: Create SSH config for easy access to ML nodes
cat > ~/.ssh/config << 'EOF'
# Default settings
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600

# GPU training nodes
Host gpu-node-*
    User mluser
    IdentityFile ~/.ssh/ml_platform_key
    StrictHostKeyChecking ask
    Port 22

# Specific nodes
Host gpu-node-1
    HostName 192.168.1.101

Host gpu-node-2
    HostName 192.168.1.102

# Jump host / bastion
Host bastion
    HostName bastion.ml-platform.com
    User admin
    IdentityFile ~/.ssh/ml_platform_key

# Access internal nodes via bastion
Host internal-*
    ProxyJump bastion
    User mluser
EOF

# Create socket directory
mkdir -p ~/.ssh/sockets

# TODO: Test connection reuse
# ssh gpu-node-1  # First connection
# ssh gpu-node-1  # Reuses connection (faster)
```

### Task 3: Firewall Configuration with UFW and iptables

**TODO 3.1:** Set up UFW (Uncomplicated Firewall)

```bash
# TODO: Check UFW status
sudo ufw status verbose

# Enable UFW (be careful on remote systems!)
# sudo ufw enable

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# TODO: Allow SSH (critical before enabling firewall remotely!)
sudo ufw allow 22/tcp comment 'SSH access'

# Allow ML platform services
sudo ufw allow 8080/tcp comment 'ML Model API'
sudo ufw allow 9090/tcp comment 'Prometheus'
sudo ufw allow 3000/tcp comment 'Grafana'

# Allow from specific subnet only
sudo ufw allow from 192.168.1.0/24 to any port 5432 comment 'PostgreSQL internal only'
sudo ufw allow from 192.168.1.0/24 to any port 6379 comment 'Redis internal only'

# TODO: Rate limit SSH to prevent brute force
sudo ufw limit 22/tcp

# Show rules with numbers
sudo ufw status numbered

# Delete a rule by number if needed
# sudo ufw delete 5
```

**TODO 3.2:** Advanced iptables rules for ML infrastructure

```bash
# TODO: View current iptables rules
sudo iptables -L -v -n

# Save current rules
sudo iptables-save > ~/iptables_backup.txt

# Allow loopback (localhost communication)
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# TODO: Allow SSH from specific IP ranges (company VPN)
sudo iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT

# Allow model API from application servers
sudo iptables -A INPUT -p tcp --dport 8080 -s 192.168.100.0/24 -j ACCEPT

# Rate limit to prevent DDoS on API
sudo iptables -A INPUT -p tcp --dport 8080 -m limit --limit 100/second --limit-burst 200 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8080 -j DROP

# TODO: Log dropped packets for debugging
sudo iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables-dropped: " --log-level 4

# Default policy: drop all other incoming
sudo iptables -P INPUT DROP

# Save rules (Ubuntu/Debian)
sudo netfilter-persistent save

# View logs
sudo tail -f /var/log/syslog | grep iptables-dropped
```

**TODO 3.3:** Test firewall rules

```bash
# TODO: Test from another machine or container
# From testing machine:
# telnet <target-ip> 8080    # Should succeed
# telnet <target-ip> 5432    # Should fail (if not in allowed subnet)

# Simulate testing with Docker containers
docker run -d --name api-server -p 8080:8080 hashicorp/http-echo -text="ML API"

# Test locally
curl http://localhost:8080

# Test with nmap
sudo nmap -sS localhost

# TODO: Document which ports are open and why
```

### Task 4: Network Connectivity Troubleshooting

**TODO 4.1:** Diagnose connectivity issues with ping and traceroute

```bash
# Scenario: Training job can't reach data lake at 10.50.20.100

# TODO: Test basic connectivity
ping -c 4 10.50.20.100

# If ping fails, check if host is up
ping -c 4 8.8.8.8  # Test internet connectivity first

# TODO: Trace the route to destination
traceroute 10.50.20.100
# Or use modern mtr (combines ping + traceroute)
mtr --report --report-cycles 10 10.50.20.100

# Check specific port connectivity
nc -zv 10.50.20.100 443  # Test if port 443 is open

# Alternative: use telnet
telnet 10.50.20.100 443

# TODO: Test with timeout
timeout 5 bash -c 'cat < /dev/null > /dev/tcp/10.50.20.100/443'
if [ $? -eq 0 ]; then
    echo "Port 443 is open"
else
    echo "Port 443 is closed or filtered"
fi
```

**TODO 4.2:** Analyze network traffic with tcpdump

```bash
# TODO: Capture packets on primary interface
sudo tcpdump -i $PRIMARY_IFACE -c 100 -w /tmp/capture.pcap

# Capture only HTTP traffic to model API
sudo tcpdump -i any 'tcp port 8080' -A -c 20

# Capture traffic to/from specific host
sudo tcpdump -i any host 192.168.1.100

# Capture and show in real-time with details
sudo tcpdump -i any -nn -A 'tcp port 8080 and host 192.168.1.100'

# TODO: Debug PostgreSQL connection issues
# Terminal 1: Start capture
sudo tcpdump -i any 'tcp port 5432' -w /tmp/postgres.pcap

# Terminal 2: Try to connect
psql -h 192.168.1.50 -U mluser -d ml_platform

# Stop capture (Ctrl+C) and analyze
tcpdump -r /tmp/postgres.pcap -nn

# Look for:
# - SYN packets (connection attempts)
# - RST packets (connection refused)
# - Retransmissions (network issues)
```

**TODO 4.3:** Debug with netcat (network Swiss Army knife)

```bash
# TODO: Test if a port is open (alternative to telnet)
nc -zv 192.168.1.100 6379

# Create a simple TCP server for testing
nc -l 9999
# From another terminal: echo "test message" | nc localhost 9999

# Test UDP connectivity (often needed for DNS)
nc -u -zv 8.8.8.8 53

# Transfer file over network (for testing bandwidth)
# Receiver:
nc -l 9999 > received_file.dat
# Sender:
nc 192.168.1.100 9999 < /dev/zero | pv -r  # Use pv to show rate
```

### Task 5: DNS Resolution Troubleshooting

**TODO 5.1:** Diagnose DNS issues

```bash
# TODO: Check current DNS configuration
cat /etc/resolv.conf

# Test DNS resolution
nslookup google.com

# More detailed DNS query
dig google.com

# Query specific DNS server
dig @8.8.8.8 google.com

# TODO: Test internal DNS (common issue in ML clusters)
dig ml-api.internal.com

# If fails, check if DNS server is reachable
ping <dns-server-ip>

# Trace DNS resolution path
dig +trace google.com

# Check reverse DNS
dig -x 8.8.8.8
```

**TODO 5.2:** Configure custom DNS resolution

```bash
# TODO: Add custom DNS entries to /etc/hosts (local testing)
sudo tee -a /etc/hosts << EOF
192.168.1.100 gpu-node-1.internal
192.168.1.101 gpu-node-2.internal
192.168.1.200 ml-api.internal
192.168.1.201 feature-store.internal
192.168.1.202 model-registry.internal
EOF

# Verify resolution
ping -c 2 ml-api.internal

# TODO: Configure systemd-resolved (Ubuntu 18.04+)
sudo tee /etc/systemd/resolved.conf << EOF
[Resolve]
DNS=8.8.8.8 1.1.1.1
FallbackDNS=8.8.4.4
Domains=internal.com ml-platform.local
DNSSEC=no
EOF

# Restart resolver
sudo systemctl restart systemd-resolved

# Verify configuration
resolvectl status
```

**TODO 5.3:** Test DNS caching behavior

```bash
# TODO: Flush DNS cache
sudo systemd-resolve --flush-caches
# Or on older systems:
# sudo /etc/init.d/nscd restart

# Time DNS resolution
time nslookup google.com  # First query (uncached)
time nslookup google.com  # Second query (cached)

# Monitor DNS queries
sudo tcpdump -i any port 53 -v
```

### Task 6: Network Performance and Latency Analysis

**TODO 6.1:** Measure network latency and packet loss

```bash
# TODO: Continuous latency monitoring
ping -i 0.2 192.168.1.100 | while read line; do
    echo "$(date): $line";
done | tee ping_monitor.log

# Better tool: use mtr for detailed analysis
mtr --report --report-cycles 100 192.168.1.100

# Calculate statistics
ping -c 100 192.168.1.100 | tail -n 4

# TODO: Test bandwidth with iperf3
# On server (model server):
iperf3 -s

# On client (training node):
iperf3 -c 192.168.1.100 -t 30 -i 5

# Test UDP bandwidth and packet loss
iperf3 -c 192.168.1.100 -u -b 100M
```

**TODO 6.2:** Analyze network interface statistics

```bash
# TODO: Check for errors and dropped packets
ip -s link show $PRIMARY_IFACE

# Monitor interface statistics in real-time
watch -n 1 'ip -s link show eth0'

# Detailed statistics
ethtool -S $PRIMARY_IFACE

# Check for errors
netstat -i

# TODO: Look for:
# - RX errors: Problems receiving data
# - TX errors: Problems sending data
# - Dropped: Packets dropped (buffer overflow)
# - Overruns: Interface buffer overflow
```

**TODO 6.3:** Create network performance monitoring script

```bash
# TODO: Create monitoring script
cat > ~/network_monitor.sh << 'EOF'
#!/bin/bash
# Network performance monitoring for ML infrastructure

IFACE="${1:-eth0}"
LOG_FILE="/var/log/network_monitor.log"

echo "=== Network Monitoring Started: $(date) ===" | tee -a $LOG_FILE

while true; do
    # Timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

    # Get interface statistics
    STATS=$(ip -s link show $IFACE | grep -A 2 "RX:\|TX:")

    # Get connection counts
    ESTABLISHED=$(ss -tan | grep ESTAB | wc -l)
    TIME_WAIT=$(ss -tan | grep TIME-WAIT | wc -l)

    # Log
    echo "[$TIMESTAMP] Established: $ESTABLISHED, TIME_WAIT: $TIME_WAIT" | tee -a $LOG_FILE

    # Test connectivity to critical services
    SERVICES=("ml-api.internal:8080" "feature-store.internal:6379" "model-registry.internal:5432")

    for service in "${SERVICES[@]}"; do
        HOST=${service%%:*}
        PORT=${service##*:}

        if timeout 1 bash -c "cat < /dev/null > /dev/tcp/$HOST/$PORT" 2>/dev/null; then
            echo "[$TIMESTAMP] ✓ $service reachable" | tee -a $LOG_FILE
        else
            echo "[$TIMESTAMP] ✗ $service UNREACHABLE" | tee -a $LOG_FILE
        fi
    done

    sleep 60
done
EOF

chmod +x ~/network_monitor.sh

# TODO: Run in background
# nohup ./network_monitor.sh eth0 &
```

### Task 7: Network Segmentation and Security

**TODO 7.1:** Create network namespaces for isolation

```bash
# TODO: Create isolated network namespace
sudo ip netns add ml-training
sudo ip netns add ml-serving

# List namespaces
ip netns list

# Execute command in namespace
sudo ip netns exec ml-training ip addr

# TODO: Create virtual ethernet pair
sudo ip link add veth-train type veth peer name veth-train-br
sudo ip link add veth-serve type veth peer name veth-serve-br

# Move one end to namespace
sudo ip link set veth-train netns ml-training
sudo ip link set veth-serve netns ml-serving

# Configure interfaces
sudo ip netns exec ml-training ip addr add 10.100.1.2/24 dev veth-train
sudo ip netns exec ml-training ip link set veth-train up
sudo ip netns exec ml-training ip link set lo up

# Test isolation
sudo ip netns exec ml-training ping -c 2 10.100.1.2
```

**TODO 7.2:** Simulate multi-network ML infrastructure with Docker

```bash
# TODO: Create Docker networks for different tiers
docker network create --subnet=172.20.0.0/16 ml-frontend
docker network create --subnet=172.21.0.0/16 ml-backend
docker network create --subnet=172.22.0.0/16 ml-data

# Deploy services in segmented networks
# Frontend: Model API
docker run -d --name ml-api \
    --network ml-frontend \
    --ip 172.20.0.10 \
    -p 8080:8080 \
    hashicorp/http-echo -text="ML API"

# Backend: Feature store (Redis)
docker run -d --name feature-store \
    --network ml-backend \
    --ip 172.21.0.10 \
    redis:7-alpine

# Data layer: PostgreSQL
docker run -d --name model-db \
    --network ml-data \
    --ip 172.22.0.10 \
    -e POSTGRES_PASSWORD=secret \
    postgres:15

# TODO: Connect API to backend and data networks
docker network connect ml-backend ml-api
docker network connect ml-data ml-api

# Verify connectivity
docker exec ml-api ping -c 2 172.21.0.10  # Should reach feature-store
docker exec ml-api ping -c 2 172.22.0.10  # Should reach model-db

# TODO: Verify isolation - feature-store cannot reach model-db
docker exec feature-store ping -c 2 172.22.0.10  # Should fail

# Inspect network
docker network inspect ml-backend
```

### Task 8: Troubleshooting Common ML Infrastructure Network Issues

**TODO 8.1:** Debug "Connection Timeout" issues

```bash
# TODO: Create debugging checklist script
cat > ~/debug_connection.sh << 'EOF'
#!/bin/bash
# Debug network connection issues

TARGET_HOST="$1"
TARGET_PORT="$2"

if [ -z "$TARGET_HOST" ] || [ -z "$TARGET_PORT" ]; then
    echo "Usage: $0 <host> <port>"
    exit 1
fi

echo "=== Debugging connection to $TARGET_HOST:$TARGET_PORT ==="

# 1. Check DNS resolution
echo -e "\n[1] DNS Resolution:"
if host $TARGET_HOST > /dev/null 2>&1; then
    IP=$(host $TARGET_HOST | awk '/has address/ {print $4}' | head -n1)
    echo "✓ Resolved: $TARGET_HOST -> $IP"
else
    echo "✗ DNS resolution failed for $TARGET_HOST"
    exit 1
fi

# 2. Check ping connectivity
echo -e "\n[2] Ping Test:"
if ping -c 3 -W 2 $IP > /dev/null 2>&1; then
    echo "✓ Host is reachable via ICMP"
else
    echo "✗ Host not reachable (might be ICMP blocked)"
fi

# 3. Check port connectivity
echo -e "\n[3] Port $TARGET_PORT Test:"
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$IP/$TARGET_PORT" 2>/dev/null; then
    echo "✓ Port $TARGET_PORT is open"
else
    echo "✗ Port $TARGET_PORT is closed or filtered"
fi

# 4. Check route
echo -e "\n[4] Route to host:"
traceroute -m 10 -w 2 $IP 2>&1 | head -n 10

# 5. Check local firewall
echo -e "\n[5] Local Firewall:"
if sudo iptables -L OUTPUT -n | grep -q "REJECT\|DROP"; then
    echo "⚠ Outbound firewall rules detected"
else
    echo "✓ No restrictive outbound rules"
fi

# 6. Check if service is listening (if local)
if [ "$IP" == "127.0.0.1" ] || [ "$TARGET_HOST" == "localhost" ]; then
    echo -e "\n[6] Local Service Check:"
    if ss -tlnp | grep -q ":$TARGET_PORT "; then
        echo "✓ Service is listening on port $TARGET_PORT"
        ss -tlnp | grep ":$TARGET_PORT "
    else
        echo "✗ No service listening on port $TARGET_PORT"
    fi
fi

echo -e "\n=== Debug Complete ==="
EOF

chmod +x ~/debug_connection.sh

# TODO: Test the script
./debug_connection.sh ml-api.internal 8080
```

**TODO 8.2:** Debug high latency issues

```bash
# TODO: Create latency analysis script
cat > ~/analyze_latency.sh << 'EOF'
#!/bin/bash
# Analyze network latency issues

TARGET="$1"

echo "=== Latency Analysis for $TARGET ==="

# Measure round-trip time
echo -e "\n[1] RTT Measurement (100 pings):"
ping -c 100 -i 0.2 $TARGET 2>&1 | tail -n 2

# Identify if latency is consistent or variable
echo -e "\n[2] Latency Distribution:"
ping -c 50 $TARGET | grep 'time=' | awk -F'time=' '{print $2}' | awk '{print $1}' | sort -n | awk '
    BEGIN { sum=0; count=0; }
    {
        values[count]=$1;
        sum+=$1;
        count++;
    }
    END {
        print "Min:  " values[0] " ms"
        print "P50:  " values[int(count*0.5)] " ms"
        print "P95:  " values[int(count*0.95)] " ms"
        print "P99:  " values[int(count*0.99)] " ms"
        print "Max:  " values[count-1] " ms"
        print "Avg:  " sum/count " ms"
    }
'

# Check for packet loss
echo -e "\n[3] Packet Loss Test:"
ping -c 100 -i 0.1 $TARGET | grep 'packet loss'

# Identify network hops causing delay
echo -e "\n[4] Per-Hop Latency:"
mtr --report --report-cycles 10 $TARGET 2>/dev/null || traceroute $TARGET

echo -e "\n=== Analysis Complete ==="
EOF

chmod +x ~/analyze_latency.sh

# TODO: Run analysis
# ./analyze_latency.sh ml-api.internal
```

## Deliverables

Submit a repository with:

1. **Configuration Files**
   - Hardened `/etc/ssh/sshd_config.d/99-hardening.conf`
   - Custom `~/.ssh/config` for ML infrastructure
   - UFW rules backup (`ufw_rules.txt`)
   - `/etc/hosts` with internal hostnames

2. **Troubleshooting Scripts**
   - `network_monitor.sh` - Continuous monitoring
   - `debug_connection.sh` - Connection debugging
   - `analyze_latency.sh` - Latency analysis

3. **Documentation** (`NETWORK_GUIDE.md`)
   - Network topology diagram for ML platform
   - Troubleshooting decision tree (flowchart)
   - Common issues and solutions table
   - Security hardening checklist

4. **Lab Report** (`LAB_REPORT.md`)
   - Screenshot/output from each task
   - Issues encountered and how you resolved them
   - Network performance benchmarks (iperf3, ping latency)
   - Firewall rules explanation

## Success Criteria

- [ ] Successfully use `ip` and `ss` commands instead of deprecated tools
- [ ] SSH hardened with key-based auth and password login disabled
- [ ] Firewall configured to allow only necessary services
- [ ] Can diagnose connectivity issues using ping, traceroute, tcpdump
- [ ] DNS resolution working for internal hostnames
- [ ] Network monitoring script runs successfully
- [ ] Can measure bandwidth and identify bottlenecks
- [ ] Demonstrated network segmentation with Docker or namespaces
- [ ] All troubleshooting scripts execute without errors
- [ ] Documentation includes clear diagrams and explanations

## Bonus Challenges

1. **VPN Setup**: Configure WireGuard VPN for secure remote access to ML infrastructure
2. **Load Balancer**: Set up HAProxy or Nginx to load balance across multiple model API servers
3. **Network Monitoring Dashboard**: Create Grafana dashboard using network metrics
4. **Automated Remediation**: Extend monitoring script to automatically restart failed services
5. **Network Namespace per Job**: Isolate each training job in its own network namespace
6. **BGP Simulation**: Use FRRouting to simulate BGP for multi-datacenter ML platform

## Resources

- [Linux Networking Commands Cheat Sheet](https://www.redhat.com/sysadmin/linux-networking-commands)
- [tcpdump Tutorial](https://danielmiessler.com/study/tcpdump/)
- [SSH Security Best Practices](https://www.ssh.com/academy/ssh/security)
- [UFW Essentials](https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands)
- [Network Troubleshooting with mtr](https://www.linode.com/docs/guides/diagnosing-network-issues-with-mtr/)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| Network interface inspection and configuration | 10 |
| SSH security hardening | 15 |
| Firewall configuration (UFW/iptables) | 15 |
| Connectivity troubleshooting (ping, traceroute, tcpdump) | 15 |
| DNS resolution and configuration | 10 |
| Network performance analysis | 15 |
| Network segmentation demonstration | 10 |
| Documentation and scripts | 10 |

**Total: 100 points**
