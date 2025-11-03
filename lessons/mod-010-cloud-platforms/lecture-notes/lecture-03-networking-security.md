# Lecture 03: AWS Networking and Security for AI Infrastructure

## Lecture Overview

Secure, well-architected network infrastructure is fundamental to production ML systems. This lecture covers AWS networking services—VPCs, subnets, routing, security groups, NACLs—and how to design isolated, secure network architectures for AI/ML workloads. You'll learn to build multi-tier networks with public-facing load balancers, private application servers, and isolated data tiers, implementing defense-in-depth security principles.

By the end, you'll understand how to create production-grade VPC architectures, configure security groups following least-privilege principles, implement network segmentation for compliance, and troubleshoot connectivity issues. You'll also learn advanced IAM patterns for cross-account access and service-to-service authentication in microservices architectures.

**Estimated Reading Time:** 75-90 minutes
**Hands-on Companion Lab:** Exercise 03 – Networking & Security Lab
**Prerequisites:** Lecture 02 (AWS Core Services), basic understanding of IP addressing and subnetting, familiarity with TCP/IP protocols

### Learning Objectives

By the end of this lecture, you will:
- Design and create VPC architectures with proper CIDR block planning
- Configure public and private subnets with appropriate routing
- Implement security groups and NACLs following defense-in-depth principles
- Deploy multi-tier network architectures for ML applications
- Configure VPC endpoints for secure AWS service access
- Troubleshoot network connectivity issues using AWS tools
- Apply IAM security patterns for cross-account and service-to-service access

---

## 1. VPC (Virtual Private Cloud) Fundamentals

### 1.1 What is a VPC?

**VPC = Isolated Virtual Network in AWS Cloud**

Think of a VPC as your own private data center in AWS, where you have complete control over:
- **IP address range** (CIDR blocks)
- **Subnets** (network segments)
- **Route tables** (how traffic flows)
- **Network gateways** (internet access, VPN connections)
- **Security policies** (firewalls, access control)

**Default VPC:**
- AWS creates a default VPC in each region when you create an account
- CIDR: 172.31.0.0/16 (65,536 IP addresses)
- Public subnets in each AZ
- Internet Gateway attached
- **Good for getting started, NOT recommended for production**

### 1.2 VPC CIDR Blocks and IP Addressing

**CIDR Notation:** `10.0.0.0/16`
- **Network portion:** First 16 bits (10.0)
- **Host portion:** Last 16 bits (65,536 addresses: 10.0.0.0 - 10.0.255.255)

**Common VPC CIDR Blocks:**

| CIDR | IP Range | Usable IPs | Use Case |
|------|----------|------------|----------|
| 10.0.0.0/16 | 10.0.0.0 - 10.0.255.255 | 65,531 | Large production VPC |
| 10.0.0.0/24 | 10.0.0.0 - 10.0.0.255 | 251 | Small dev/test VPC |
| 172.16.0.0/12 | 172.16.0.0 - 172.31.255.255 | 1,048,571 | Very large VPC |
| 192.168.0.0/16 | 192.168.0.0 - 192.168.255.255 | 65,531 | Common for on-prem integration |

**AWS Reserves 5 IPs per Subnet:**
- **x.x.x.0**: Network address
- **x.x.x.1**: VPC router
- **x.x.x.2**: DNS server (AWS-provided)
- **x.x.x.3**: Reserved for future use
- **x.x.x.255**: Broadcast address (not used in VPC, but reserved)

**Example:** 10.0.0.0/24 subnet
- Total IPs: 256
- Usable IPs: 256 - 5 = **251**
- First usable: 10.0.0.4
- Last usable: 10.0.0.254

### 1.3 Creating a VPC (CLI)

**Create VPC:**

```bash
# Create VPC with 10.0.0.0/16 CIDR block
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=ml-production-vpc}]'

# Output includes VpcId (e.g., vpc-0abcdef1234567890)

# Enable DNS hostnames (required for RDS, ELB)
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-0abcdef1234567890 \
  --enable-dns-hostnames

# Enable DNS support (enabled by default)
aws ec2 modify-vpc-attribute \
  --vpc-id vpc-0abcdef1234567890 \
  --enable-dns-support
```

**View VPCs:**

```bash
# List all VPCs
aws ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock,Tags[?Key==`Name`].Value|[0]]' --output table

# Output:
-----------------------------------------------------
|                  DescribeVpcs                     |
+----------------------+----------------+-----------+
|  vpc-0abc123       |  10.0.0.0/16   |  ml-production-vpc |
|  vpc-default456    |  172.31.0.0/16 |  default-vpc       |
+----------------------+----------------+-----------+
```

---

## 2. Subnets: Network Segmentation

### 2.1 Public vs Private Subnets

**Public Subnet:**
- **Route to Internet Gateway** (0.0.0.0/0 → igw-xxxxx)
- Instances have **public IP addresses**
- **Use case**: Load balancers, bastion hosts, NAT gateways

**Private Subnet:**
- **No direct route to Internet Gateway**
- Instances have **private IP addresses only**
- Outbound internet via **NAT Gateway** in public subnet
- **Use case**: Application servers, databases (security best practice)

### 2.2 Multi-Tier Network Architecture

**Typical Production ML Architecture:**

```
VPC: 10.0.0.0/16

├─ Public Subnet 1 (10.0.1.0/24) [us-east-1a]
│  └─ Application Load Balancer (ALB)
│  └─ NAT Gateway
├─ Public Subnet 2 (10.0.2.0/24) [us-east-1b]
│  └─ ALB (for HA)
│  └─ NAT Gateway (for HA)
│
├─ Private Subnet 1 (10.0.11.0/24) [us-east-1a]
│  └─ EC2 Inference Servers
│  └─ ECS/EKS worker nodes
├─ Private Subnet 2 (10.0.12.0/24) [us-east-1b]
│  └─ EC2 Inference Servers (HA)
│
├─ Data Subnet 1 (10.0.21.0/24) [us-east-1a]
│  └─ RDS Primary
│  └─ ElastiCache Redis
├─ Data Subnet 2 (10.0.22.0/24) [us-east-1b]
│  └─ RDS Standby (Multi-AZ)
```

**Why Multi-Tier?**
- **Security**: Internet cannot directly reach application servers or databases
- **Compliance**: Meet requirements for network isolation (PCI-DSS, HIPAA)
- **Defense in Depth**: Multiple layers of security

### 2.3 Creating Subnets (CLI)

**Create Public Subnet:**

```bash
# Public Subnet in us-east-1a
aws ec2 create-subnet \
  --vpc-id vpc-0abcdef1234567890 \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1a},{Key=Tier,Value=public}]'

# Enable auto-assign public IP (makes it "public")
aws ec2 modify-subnet-attribute \
  --subnet-id subnet-0abc111 \
  --map-public-ip-on-launch
```

**Create Private Subnet:**

```bash
# Private Subnet in us-east-1a
aws ec2 create-subnet \
  --vpc-id vpc-0abcdef1234567890 \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1a},{Key=Tier,Value=private}]'

# No auto-assign public IP (makes it "private")
```

**Create Subnets in Multiple AZs (High Availability):**

```bash
# Public Subnet in us-east-1b
aws ec2 create-subnet \
  --vpc-id vpc-0abcdef1234567890 \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public-subnet-1b}]'

aws ec2 modify-subnet-attribute --subnet-id subnet-0abc222 --map-public-ip-on-launch

# Private Subnet in us-east-1b
aws ec2 create-subnet \
  --vpc-id vpc-0abcdef1234567890 \
  --cidr-block 10.0.12.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private-subnet-1b}]'
```

### 2.4 Subnet IP Planning Best Practices

**Reserve CIDR Space for Growth:**

```
VPC: 10.0.0.0/16 (65,536 IPs)

├─ Public Subnets: 10.0.0.0/20 (4,096 IPs)
│  ├─ us-east-1a: 10.0.1.0/24 (256 IPs)
│  ├─ us-east-1b: 10.0.2.0/24 (256 IPs)
│  ├─ us-east-1c: 10.0.3.0/24 (256 IPs)
│  └─ Reserved: 10.0.4.0/22 (1,024 IPs for future AZs)
│
├─ Private Subnets: 10.0.16.0/20 (4,096 IPs)
│  ├─ us-east-1a: 10.0.16.0/24 (256 IPs)
│  ├─ us-east-1b: 10.0.17.0/24 (256 IPs)
│  ├─ us-east-1c: 10.0.18.0/24 (256 IPs)
│  └─ Reserved: 10.0.20.0/22 (1,024 IPs)
│
├─ Data Subnets: 10.0.32.0/20 (4,096 IPs)
│  ├─ us-east-1a: 10.0.32.0/24 (256 IPs)
│  ├─ us-east-1b: 10.0.33.0/24 (256 IPs)
│  └─ Reserved: 10.0.34.0/23 (512 IPs)
│
└─ Reserved for future tiers: 10.0.48.0/20 - 10.0.255.0/20
```

**Tips:**
- Use /24 subnets (256 IPs) for most use cases
- Use /20 or /22 for EKS node pools (many pods = many IPs)
- Leave gaps for future growth
- Document your IP allocation scheme

---

## 3. Internet Gateway and NAT Gateway

### 3.1 Internet Gateway (IGW)

**Internet Gateway = Door to the Internet for VPC**

**Characteristics:**
- Horizontally scaled, redundant, highly available (AWS-managed)
- No bandwidth constraints
- Free (no hourly charge, only data transfer out)

**Create and Attach IGW:**

```bash
# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=ml-vpc-igw}]'

# Output: igw-0xyz789

# Attach to VPC
aws ec2 attach-internet-gateway \
  --internet-gateway-id igw-0xyz789 \
  --vpc-id vpc-0abcdef1234567890
```

**Create Route Table for Public Subnets:**

```bash
# Create route table
aws ec2 create-route-table \
  --vpc-id vpc-0abcdef1234567890 \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-route-table}]'

# Output: rtb-0public123

# Add route to Internet Gateway (0.0.0.0/0 → IGW)
aws ec2 create-route \
  --route-table-id rtb-0public123 \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id igw-0xyz789

# Associate route table with public subnets
aws ec2 associate-route-table \
  --route-table-id rtb-0public123 \
  --subnet-id subnet-0abc111  # public-subnet-1a

aws ec2 associate-route-table \
  --route-table-id rtb-0public123 \
  --subnet-id subnet-0abc222  # public-subnet-1b
```

### 3.2 NAT Gateway

**NAT Gateway = Allows Private Subnet Instances to Access Internet (Outbound Only)**

**Why NAT Gateway?**
- Private subnet instances need to download packages (apt update, pip install)
- Need to call external APIs (S3, DynamoDB, external services)
- But should NOT be reachable from the internet (security)

**NAT Gateway vs NAT Instance:**

| Feature | NAT Gateway (Managed) | NAT Instance (EC2) |
|---------|----------------------|--------------------|
| **Availability** | AWS-managed HA | Manual (single instance) |
| **Bandwidth** | Up to 45 Gbps | Depends on instance type |
| **Maintenance** | AWS handles | You patch/maintain |
| **Cost** | $0.045/hour + $0.045/GB | EC2 instance cost |
| **Recommended** | ✅ Yes | ❌ No (legacy) |

**Create NAT Gateway:**

```bash
# Step 1: Allocate Elastic IP (static public IP for NAT Gateway)
aws ec2 allocate-address --domain vpc
# Output: AllocationId: eipalloc-0natip123

# Step 2: Create NAT Gateway in public subnet
aws ec2 create-nat-gateway \
  --subnet-id subnet-0abc111 \
  --allocation-id eipalloc-0natip123 \
  --tag-specifications 'ResourceType=nat-gateway,Tags=[{Key=Name,Value=nat-gateway-1a}]'

# Output: NatGatewayId: nat-0natgw123

# Wait for NAT Gateway to become available (takes 2-3 minutes)
aws ec2 wait nat-gateway-available --nat-gateway-ids nat-0natgw123
```

**Create Route Table for Private Subnets:**

```bash
# Create private route table
aws ec2 create-route-table \
  --vpc-id vpc-0abcdef1234567890 \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-route-table-1a}]'

# Output: rtb-0private123

# Add route to NAT Gateway (0.0.0.0/0 → NAT Gateway)
aws ec2 create-route \
  --route-table-id rtb-0private123 \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-0natgw123

# Associate with private subnet
aws ec2 associate-route-table \
  --route-table-id rtb-0private123 \
  --subnet-id subnet-0private111  # private-subnet-1a
```

**High Availability: NAT Gateway in Each AZ:**

```bash
# Create NAT Gateway in us-east-1b (for HA)
aws ec2 allocate-address --domain vpc
# Output: eipalloc-0natip456

aws ec2 create-nat-gateway \
  --subnet-id subnet-0abc222 \
  --allocation-id eipalloc-0natip456 \
  --tag-specifications 'ResourceType=nat-gateway,Tags=[{Key=Name,Value=nat-gateway-1b}]'

# Create separate route table for private subnet in us-east-1b
aws ec2 create-route-table \
  --vpc-id vpc-0abcdef1234567890 \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-route-table-1b}]'

aws ec2 create-route \
  --route-table-id rtb-0private456 \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id nat-0natgw456

aws ec2 associate-route-table \
  --route-table-id rtb-0private456 \
  --subnet-id subnet-0private222
```

**Cost Consideration:**
- **NAT Gateway**: $0.045/hour × 2 AZs × 730 hours = $65.70/month
- **Data processing**: $0.045/GB transferred
- **Alternative for dev**: Single NAT Gateway in one AZ (not HA, saves $32.85/month)

---

## 4. Security Groups: Instance-Level Firewalls

### 4.1 Security Group Fundamentals

**Security Group = Stateful Firewall for EC2 Instances**

**Key Characteristics:**
- **Stateful**: If you allow inbound request, outbound response is automatically allowed
- **Default Deny**: Everything blocked unless explicitly allowed
- **Allow Rules Only**: Cannot create deny rules (use NACLs for that)
- **Instance-Level**: Applied to network interfaces (ENIs)

**Example: Web Server Security Group**

```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Allow HTTP/HTTPS from internet" \
  --vpc-id vpc-0abcdef1234567890

# Output: GroupId: sg-0websg123

# Allow HTTP (port 80) from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-0websg123 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS (port 443) from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id sg-0websg123 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow SSH (port 22) from your IP only (security best practice)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0websg123 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.25/32  # Your IP address
```

**View Security Group Rules:**

```bash
aws ec2 describe-security-groups --group-ids sg-0websg123

# Output shows inbound/outbound rules
```

### 4.2 Multi-Tier Security Group Architecture

**Best Practice: Reference Other Security Groups (Not CIDR Blocks)**

```bash
# Create ALB security group (public-facing)
aws ec2 create-security-group \
  --group-name alb-sg \
  --description "Load balancer security group" \
  --vpc-id vpc-0abcdef1234567890

# Allow HTTP/HTTPS from internet
aws ec2 authorize-security-group-ingress \
  --group-id sg-0albsg123 \
  --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-0albsg123 \
  --protocol tcp --port 443 --cidr 0.0.0.0/0

# Create application server security group
aws ec2 create-security-group \
  --group-name app-server-sg \
  --description "Application servers" \
  --vpc-id vpc-0abcdef1234567890

# Allow traffic ONLY from ALB security group (not from internet!)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0appsg123 \
  --protocol tcp --port 5000 \
  --source-group sg-0albsg123  # Reference ALB SG, not CIDR

# Create database security group
aws ec2 create-security-group \
  --group-name database-sg \
  --description "RDS databases" \
  --vpc-id vpc-0abcdef1234567890

# Allow PostgreSQL (port 5432) ONLY from app servers
aws ec2 authorize-security-group-ingress \
  --group-id sg-0dbsg123 \
  --protocol tcp --port 5432 \
  --source-group sg-0appsg123  # Only from app servers

# Create bastion security group
aws ec2 create-security-group \
  --group-name bastion-sg \
  --description "Bastion host for SSH access" \
  --vpc-id vpc-0abcdef1234567890

# Allow SSH only from corporate VPN
aws ec2 authorize-security-group-ingress \
  --group-id sg-0bastionsg123 \
  --protocol tcp --port 22 \
  --cidr 198.51.100.0/24  # Corporate VPN CIDR

# Allow SSH from bastion to app servers
aws ec2 authorize-security-group-ingress \
  --group-id sg-0appsg123 \
  --protocol tcp --port 22 \
  --source-group sg-0bastionsg123
```

**Security Group Chain:**

```
Internet
  ↓ (HTTP/HTTPS allowed)
[ALB - sg-0albsg123]
  ↓ (Port 5000 allowed from ALB SG only)
[App Servers - sg-0appsg123]
  ↓ (Port 5432 allowed from App SG only)
[Database - sg-0dbsg123]

[Bastion - sg-0bastionsg123]
  ↓ (SSH allowed to App Servers)
[App Servers - sg-0appsg123]
```

**Benefits:**
- If you scale app servers (add instances), they automatically get access to DB
- No need to update DB security group with new IP addresses
- Clear security boundaries

### 4.3 Common Security Group Patterns for ML Infrastructure

**1. ML Training Instance Security Group:**

```bash
aws ec2 create-security-group \
  --group-name ml-training-sg \
  --description "GPU instances for model training" \
  --vpc-id vpc-0abcdef1234567890

# Allow SSH from bastion only
aws ec2 authorize-security-group-ingress \
  --group-id sg-0trainsg123 \
  --protocol tcp --port 22 \
  --source-group sg-0bastionsg123

# Allow Jupyter notebook access (port 8888) from VPN only
aws ec2 authorize-security-group-ingress \
  --group-id sg-0trainsg123 \
  --protocol tcp --port 8888 \
  --cidr 198.51.100.0/24  # Corporate VPN

# Allow S3 access (outbound) - default allows all outbound, no rule needed
```

**2. ML Inference Service Security Group:**

```bash
aws ec2 create-security-group \
  --group-name ml-inference-sg \
  --description "Inference API servers" \
  --vpc-id vpc-0abcdef1234567890

# Allow API traffic (port 5000) from ALB only
aws ec2 authorize-security-group-ingress \
  --group-id sg-0infersg123 \
  --protocol tcp --port 5000 \
  --source-group sg-0albsg123

# Allow health checks from ALB
# (Covered by above rule if health check uses same port)
```

**3. EKS Cluster Security Groups:**

```bash
# EKS Control Plane Security Group (AWS-managed, but you can add rules)
# EKS Worker Node Security Group

aws ec2 create-security-group \
  --group-name eks-worker-sg \
  --description "EKS worker nodes" \
  --vpc-id vpc-0abcdef1234567890

# Allow kubelet API (port 10250) from control plane
aws ec2 authorize-security-group-ingress \
  --group-id sg-0eksworkersg123 \
  --protocol tcp --port 10250 \
  --source-group sg-0ekscontrolsg123

# Allow all traffic between worker nodes (pod-to-pod communication)
aws ec2 authorize-security-group-ingress \
  --group-id sg-0eksworkersg123 \
  --protocol -1 \
  --source-group sg-0eksworkersg123  # Self-referencing
```

### 4.4 Security Group Best Practices

**1. Least Privilege:**
- Only open ports that are absolutely necessary
- Restrict source to specific IPs/security groups, not 0.0.0.0/0

**2. Use Descriptive Names and Tags:**
```bash
--tag-specifications 'ResourceType=security-group,Tags=[{Key=Name,Value=ml-inference-prod},{Key=Environment,Value=production},{Key=Team,Value=ml-platform}]'
```

**3. Regular Audits:**
```bash
# List security groups with overly permissive rules (open to 0.0.0.0/0)
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]].{Name:GroupName,ID:GroupId}' \
  --output table
```

**4. Document Your Security Groups:**
```bash
# Add descriptions to rules (requires JSON input)
cat > sg-rule.json <<'EOF'
{
  "IpPermissions": [{
    "IpProtocol": "tcp",
    "FromPort": 5000,
    "ToPort": 5000,
    "UserIdGroupPairs": [{
      "GroupId": "sg-0albsg123",
      "Description": "Allow inference API traffic from ALB"
    }]
  }]
}
EOF

aws ec2 authorize-security-group-ingress \
  --group-id sg-0infersg123 \
  --cli-input-json file://sg-rule.json
```

---

## 5. Network ACLs (NACLs)

### 5.1 NACLs vs Security Groups

| Feature | Security Groups | NACLs |
|---------|----------------|-------|
| **Level** | Instance (ENI) | Subnet |
| **State** | Stateful (return traffic auto-allowed) | Stateless (must explicitly allow return) |
| **Rules** | Allow only | Allow and Deny |
| **Rule Evaluation** | All rules evaluated | Rules evaluated in number order |
| **Default** | Deny all inbound, allow all outbound | Allow all inbound/outbound |
| **Use Case** | Primary defense | Additional layer of defense |

**When to Use NACLs:**
- Block specific IP addresses (DDoS mitigation)
- Compliance requirements for network-level controls
- Defense in depth (additional layer beyond security groups)

### 5.2 Creating Custom NACLs

**Create NACL:**

```bash
# Create network ACL
aws ec2 create-network-acl \
  --vpc-id vpc-0abcdef1234567890 \
  --tag-specifications 'ResourceType=network-acl,Tags=[{Key=Name,Value=private-subnet-nacl}]'

# Output: NetworkAclId: acl-0nacl123
```

**Add Rules:**

```bash
# Allow inbound HTTP (port 80) from anywhere
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

# Allow inbound HTTPS (port 443)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

# Allow inbound ephemeral ports (return traffic for outbound connections)
# Linux clients use ports 32768-60999, Windows uses 49152-65535
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

# DENY traffic from specific malicious IP
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --rule-number 50 \
  --protocol -1 \
  --cidr-block 203.0.113.50/32 \
  --rule-action deny

# Allow outbound HTTP/HTTPS
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --egress \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --egress \
  --rule-number 110 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

# Allow outbound ephemeral ports (return traffic)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --egress \
  --rule-number 120 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow

# Associate NACL with subnet
aws ec2 replace-network-acl-association \
  --association-id aclassoc-0abc123 \
  --network-acl-id acl-0nacl123
```

**Rule Number Best Practices:**
- Use increments of 10 (100, 110, 120...) to allow inserting rules later
- Lower numbers evaluated first
- Use numbers < 100 for deny rules (evaluated before allow rules)

### 5.3 Example: Block Specific IP Range

```bash
# Scenario: Block traffic from known malicious IP range 198.51.100.0/24

# Inbound deny rule
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --rule-number 10 \
  --protocol -1 \
  --cidr-block 198.51.100.0/24 \
  --rule-action deny

# Outbound deny rule (stateless, need both directions)
aws ec2 create-network-acl-entry \
  --network-acl-id acl-0nacl123 \
  --egress \
  --rule-number 10 \
  --protocol -1 \
  --cidr-block 198.51.100.0/24 \
  --rule-action deny
```

---

## 6. Advanced IAM for Network Security

### 6.1 VPC Endpoints: Secure S3/DynamoDB Access

**Problem:** Traffic to S3/DynamoDB from private subnet goes through NAT Gateway → internet → AWS (expensive, less secure)

**Solution:** VPC Endpoints (private connection to AWS services)

**Types:**
- **Gateway Endpoint**: S3, DynamoDB (free)
- **Interface Endpoint**: Most other services (charged per hour + data)

**Create S3 VPC Endpoint:**

```bash
# Create S3 gateway endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-0abcdef1234567890 \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids rtb-0private123 rtb-0private456

# Now S3 traffic stays within AWS network, doesn't use NAT Gateway
# Traffic from private subnets: EC2 → S3 endpoint → S3 (never touches internet)
```

**S3 Bucket Policy for VPC Endpoint:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAccessFromVPCEndpointOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-ml-training-data-123456789",
        "arn:aws:s3:::my-ml-training-data-123456789/*"
      ],
      "Condition": {
        "StringNotEquals": {
          "aws:sourceVpce": "vpce-0s3endpoint123"
        }
      }
    }
  ]
}
```

**Benefits:**
- **Cost Savings**: No NAT Gateway data charges for S3/DynamoDB traffic
- **Security**: Traffic never leaves AWS network
- **Performance**: Lower latency

### 6.2 IAM Policies with Network Conditions

**Restrict EC2 Launch to Specific VPC:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:RunInstances",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringEquals": {
          "ec2:Vpc": "arn:aws:ec2:us-east-1:123456789012:vpc/vpc-0abcdef1234567890"
        }
      }
    }
  ]
}
```

**Require MFA for Security Group Modifications:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:AuthorizeSecurityGroupIngress",
        "ec2:RevokeSecurityGroupIngress"
      ],
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        }
      }
    }
  ]
}
```

### 6.3 Cross-Account VPC Peering and IAM

**VPC Peering:** Connect two VPCs (same account or different accounts) for private communication.

**Create VPC Peering Connection:**

```bash
# In Account A (Requester)
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-0accountA123 \
  --peer-vpc-id vpc-0accountB456 \
  --peer-owner-id 987654321098 \
  --peer-region us-east-1

# In Account B (Accepter)
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-0peering123

# Update route tables in both VPCs
# Account A: Add route 10.1.0.0/16 → pcx-0peering123
aws ec2 create-route \
  --route-table-id rtb-0accountA123 \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-0peering123

# Account B: Add route 10.0.0.0/16 → pcx-0peering123
aws ec2 create-route \
  --route-table-id rtb-0accountB456 \
  --destination-cidr-block 10.0.0.0/16 \
  --vpc-peering-connection-id pcx-0peering123

# Update security groups to allow traffic from peered VPC CIDR
```

**Use Case: ML Training in Account A, Inference in Account B**
- Training VPC (Account A): 10.0.0.0/16
- Inference VPC (Account B): 10.1.0.0/16
- Peering allows models trained in Account A to be tested in Account B's inference environment

---

## 7. Network Troubleshooting

### 7.1 VPC Flow Logs

**Enable Flow Logs to CloudWatch:**

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /aws/vpc/flowlogs

# Create IAM role for Flow Logs
cat > flow-logs-trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "vpc-flow-logs.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name VPCFlowLogsRole \
  --assume-role-policy-document file://flow-logs-trust-policy.json

# Attach policy to write to CloudWatch
aws iam attach-role-policy \
  --role-name VPCFlowLogsRole \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess

# Create flow log
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-0abcdef1234567890 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs \
  --deliver-logs-permission-arn arn:aws:iam::123456789012:role/VPCFlowLogsRole
```

**Flow Log Format:**

```
version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status

Example:
2 123456789012 eni-0abc123 10.0.1.5 198.51.100.5 45678 443 6 10 5200 1634567890 1634567920 ACCEPT OK
```

**Query Flow Logs (CloudWatch Logs Insights):**

```sql
# Find rejected connections
fields @timestamp, srcAddr, dstAddr, dstPort, action
| filter action = "REJECT"
| sort @timestamp desc
| limit 100

# Top talkers (source IPs with most traffic)
stats sum(bytes) as totalBytes by srcAddr
| sort totalBytes desc
| limit 10
```

### 7.2 Reachability Analyzer

**Test Connectivity Between Resources:**

```bash
# Analyze path from EC2 instance to RDS
aws ec2 create-network-insights-path \
  --source eni-0source123 \
  --destination eni-0destination456 \
  --protocol tcp \
  --destination-port 5432

# Run analysis
aws ec2 start-network-insights-analysis \
  --network-insights-path-id nip-0path123

# Check results
aws ec2 describe-network-insights-analyses \
  --network-insights-analysis-ids nia-0analysis123

# Output shows:
# - Reachable: Yes/No
# - Path: Source → SG → Route Table → NAT/IGW → Destination SG
# - Blocking Rule: If unreachable, shows which SG/NACL/route is blocking
```

### 7.3 Common Connectivity Issues

**1. Cannot SSH to EC2 in Public Subnet:**

Checklist:
- [ ] Instance has public IP?
- [ ] Internet Gateway attached to VPC?
- [ ] Route table has 0.0.0.0/0 → IGW?
- [ ] Security group allows SSH (port 22) from your IP?
- [ ] NACL allows inbound SSH and outbound ephemeral ports?
- [ ] Using correct SSH key?

```bash
# Verify public IP
aws ec2 describe-instances --instance-ids i-0abc123 \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# Verify route table
aws ec2 describe-route-tables --route-table-ids rtb-0public123

# Check security group
aws ec2 describe-security-groups --group-ids sg-0websg123
```

**2. EC2 in Private Subnet Cannot Reach Internet:**

Checklist:
- [ ] NAT Gateway exists in public subnet?
- [ ] Route table has 0.0.0.0/0 → NAT Gateway?
- [ ] NAT Gateway has Elastic IP?
- [ ] Security group allows outbound traffic (default yes)?
- [ ] NACL allows outbound HTTP/HTTPS and inbound ephemeral ports?

**3. RDS Not Accessible from EC2:**

Checklist:
- [ ] RDS security group allows traffic from EC2 security group?
- [ ] RDS in same VPC as EC2?
- [ ] Using correct endpoint hostname (not IP)?
- [ ] Port 5432 (PostgreSQL) or 3306 (MySQL) allowed?

```bash
# Test connection from EC2
telnet ml-metadata-db.abc123.us-east-1.rds.amazonaws.com 5432

# If connection times out, check security groups
```

---

## 8. Production VPC Architecture Example

**Complete Terraform Template (Reference):**

```hcl
# VPC
resource "aws_vpc" "ml_production" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ml-production-vpc"
    Environment = "production"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.ml_production.id
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.ml_production.id
  cidr_block        = cidrsubnet(aws_vpc.ml_production.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-${count.index + 1}"
    Tier = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.ml_production.id
  cidr_block        = cidrsubnet(aws_vpc.ml_production.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "private-subnet-${count.index + 1}"
    Tier = "private"
  }
}

# NAT Gateways (one per AZ for HA)
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"
}

resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.ml_production.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-route-table"
  }
}

resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.ml_production.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "private-route-table-${count.index + 1}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "Allow HTTP/HTTPS from internet"
  vpc_id      = aws_vpc.ml_production.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "app" {
  name        = "app-sg"
  description = "Allow traffic from ALB only"
  vpc_id      = aws_vpc.ml_production.id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "db" {
  name        = "db-sg"
  description = "Allow PostgreSQL from app servers only"
  vpc_id      = aws_vpc.ml_production.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# VPC Endpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.ml_production.id
  service_name = "com.amazonaws.${var.region}.s3"
  route_table_ids = concat(
    [aws_route_table.public.id],
    aws_route_table.private[*].id
  )
}
```

---

## 9. Key Takeaways

1. **VPCs** provide isolated networks in AWS; plan CIDR blocks carefully with room for growth.

2. **Multi-tier architecture** (public/private/data subnets) is security best practice for production.

3. **NAT Gateways** allow private instances to reach internet for updates/API calls without being reachable from internet.

4. **Security Groups** are stateful, instance-level firewalls; use group references (not CIDR) for multi-tier architectures.

5. **NACLs** provide stateless, subnet-level defense; use for deny rules and compliance requirements.

6. **VPC Endpoints** save costs and improve security by keeping S3/DynamoDB traffic within AWS network.

7. **Flow Logs** are essential for troubleshooting and security auditing; enable on production VPCs.

8. **Multi-AZ deployments** (NAT Gateways in each AZ, subnets across AZs) provide high availability.

---

## What's Next?

**Lecture 04** covers **Deployment & ML Workloads**—Infrastructure as Code with Terraform, container orchestration with ECS/EKS, serverless ML with Lambda, managed ML platforms (SageMaker), and cost optimization strategies.

**Exercise 03** provides hands-on practice building a production VPC with public/private subnets, configuring security groups for multi-tier architecture, deploying bastion hosts, and implementing VPC endpoints.

---

## Further Reading

- **AWS VPC User Guide**: https://docs.aws.amazon.com/vpc/
- **AWS Well-Architected Framework - Security Pillar**: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/
- **VPC Peering Guide**: https://docs.aws.amazon.com/vpc/latest/peering/
- **VPC Flow Logs**: https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html
- **AWS Security Best Practices**: https://aws.amazon.com/architecture/security-identity-compliance/

---

**End of Lecture 03**
