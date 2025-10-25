# Exercise 03: Production VPC with Multi-Tier Security

**Module**: Cloud Platforms
**Difficulty**: Intermediate
**Estimated Time**: 4-5 hours
**Prerequisites**: Exercises 01-02, Lecture 03 (Networking & Security)

---

## Learning Objectives

By completing this exercise, you will:
1. Design and implement a production-ready VPC from scratch
2. Configure multi-tier network architecture (public, private, database subnets)
3. Set up Internet Gateway and NAT Gateway for internet connectivity
4. Implement defense-in-depth security with Security Groups and NACLs
5. Deploy a bastion host for secure SSH access to private instances
6. Configure VPC Flow Logs for network troubleshooting
7. Use Terraform to manage networking infrastructure as code
8. Deploy a complete 3-tier web application architecture

---

## Overview

This exercise builds a production-grade VPC suitable for deploying ML inference services. You'll implement best practices like multi-AZ deployment, bastion hosts, and layered security.

**Real-World Scenario**: Your company is launching a new ML-powered image classification API. You need to build secure, highly available infrastructure with:
- Public-facing load balancer
- Private application servers (ML inference)
- Private database tier (PostgreSQL for predictions storage)
- No direct internet access to application/database servers

---

## Part 1: VPC Design & Planning

### Task 1.1: Design VPC Architecture

**Architecture Diagram**:
```
┌─────────────────────────────────────────────────────────────────┐
│                        VPC: 10.0.0.0/16                         │
│                                                                 │
│  Availability Zone us-east-1a       Availability Zone us-east-1b│
│  ┌──────────────────────┐           ┌──────────────────────┐   │
│  │ Public Subnet 1      │           │ Public Subnet 2      │   │
│  │ 10.0.1.0/24          │           │ 10.0.2.0/24          │   │
│  │ ┌────────────┐       │           │ ┌────────────┐       │   │
│  │ │ NAT GW 1   │       │           │ │ NAT GW 2   │       │   │
│  │ └────────────┘       │           │ └────────────┘       │   │
│  │ ┌────────────┐       │           │ ┌────────────┐       │   │
│  │ │Bastion Host│       │           │ │    ALB     │       │   │
│  │ └────────────┘       │           │ └────────────┘       │   │
│  └──────────┬───────────┘           └──────────┬───────────┘   │
│             │ Internet Gateway        (routes to IGW)          │
│  ┌──────────▼───────────┐           ┌──────────▼───────────┐   │
│  │ Private Subnet 1     │           │ Private Subnet 2     │   │
│  │ 10.0.10.0/24         │           │ 10.0.11.0/24         │   │
│  │ ┌────────────┐       │           │ ┌────────────┐       │   │
│  │ │  App       │       │           │ │  App       │       │   │
│  │ │  Server 1  │       │           │ │  Server 2  │       │   │
│  │ └────────────┘       │           │ └────────────┘       │   │
│  └──────────┬───────────┘           └──────────┬───────────┘   │
│             │ NAT Gateway 1          NAT Gateway 2             │
│  ┌──────────▼───────────┐           ┌──────────▼───────────┐   │
│  │ Database Subnet 1    │           │ Database Subnet 2    │   │
│  │ 10.0.20.0/24         │           │ 10.0.21.0/24         │   │
│  │ ┌────────────┐       │           │ ┌────────────┐       │   │
│  │ │    RDS     │       │           │ │RDS Replica │       │   │
│  │ │  Primary   │       │           │ │ (Standby)  │       │   │
│  │ └────────────┘       │           │ └────────────┘       │   │
│  └──────────────────────┘           └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

**CIDR Block Planning**:
```
VPC CIDR:           10.0.0.0/16   (65,536 IPs)
  ├─ Public Subnets:
  │    └─ us-east-1a:  10.0.1.0/24   (256 IPs)
  │    └─ us-east-1b:  10.0.2.0/24   (256 IPs)
  ├─ Private Subnets (App Tier):
  │    └─ us-east-1a:  10.0.10.0/24  (256 IPs)
  │    └─ us-east-1b:  10.0.11.0/24  (256 IPs)
  └─ Database Subnets:
       └─ us-east-1a:  10.0.20.0/24  (256 IPs)
       └─ us-east-1b:  10.0.21.0/24  (256 IPs)

Reserved for future expansion: 10.0.3.0/24 - 10.0.255.0/24
```

**Document the Design**:
```bash
cat > vpc-design.md <<EOF
# ML Infrastructure VPC Design

## IP Addressing
- **VPC CIDR**: 10.0.0.0/16
- **Availability Zones**: us-east-1a, us-east-1b

## Subnet Layout
| Type | AZ | CIDR | Purpose |
|------|-----|------|---------|
| Public | 1a | 10.0.1.0/24 | NAT Gateway, Bastion |
| Public | 1b | 10.0.2.0/24 | ALB |
| Private (App) | 1a | 10.0.10.0/24 | ML Inference Servers |
| Private (App) | 1b | 10.0.11.0/24 | ML Inference Servers |
| Database | 1a | 10.0.20.0/24 | RDS Primary |
| Database | 1b | 10.0.21.0/24 | RDS Standby |

## Security Groups
1. **bastion-sg**: SSH (22) from your IP
2. **alb-sg**: HTTP/HTTPS (80, 443) from internet
3. **app-sg**: Port 5000 from ALB only
4. **db-sg**: PostgreSQL (5432) from app-sg only

## Network ACLs
- Public subnets: Allow HTTP/HTTPS inbound, all outbound
- Private subnets: Allow from VPC CIDR only
- Database subnets: Allow PostgreSQL from private subnets only
EOF

cat vpc-design.md
```

---

## Part 2: Build VPC with AWS CLI

### Task 2.1: Create VPC and Subnets

**Create VPC**:
```bash
# Create VPC
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[
    {Key=Name,Value=ml-infrastructure-vpc},
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev}
  ]' \
  --query 'Vpc.VpcId' \
  --output text)

echo "VPC Created: $VPC_ID"

# Enable DNS hostnames (required for RDS)
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

# Enable DNS support
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
```

**Create Public Subnets**:
```bash
# Public Subnet 1 (us-east-1a)
PUBLIC_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-public-subnet-1a},
    {Key=Tier,Value=Public}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Public Subnet 2 (us-east-1b)
PUBLIC_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-public-subnet-1b},
    {Key=Tier,Value=Public}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Enable auto-assign public IP for public subnets
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_1 --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $PUBLIC_SUBNET_2 --map-public-ip-on-launch

echo "Public Subnets: $PUBLIC_SUBNET_1, $PUBLIC_SUBNET_2"
```

**Create Private Subnets (Application Tier)**:
```bash
# Private Subnet 1 (us-east-1a)
PRIVATE_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-private-subnet-1a},
    {Key=Tier,Value=Private-App}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Private Subnet 2 (us-east-1b)
PRIVATE_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-private-subnet-1b},
    {Key=Tier,Value=Private-App}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

echo "Private Subnets: $PRIVATE_SUBNET_1, $PRIVATE_SUBNET_2"
```

**Create Database Subnets**:
```bash
# Database Subnet 1 (us-east-1a)
DB_SUBNET_1=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.20.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-db-subnet-1a},
    {Key=Tier,Value=Database}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

# Database Subnet 2 (us-east-1b)
DB_SUBNET_2=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.21.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[
    {Key=Name,Value=ml-db-subnet-1b},
    {Key=Tier,Value=Database}
  ]' \
  --query 'Subnet.SubnetId' \
  --output text)

echo "Database Subnets: $DB_SUBNET_1, $DB_SUBNET_2"
```

### Task 2.2: Create Internet Gateway and NAT Gateways

**Internet Gateway**:
```bash
# Create Internet Gateway
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[
    {Key=Name,Value=ml-infrastructure-igw}
  ]' \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)

# Attach to VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID

echo "Internet Gateway: $IGW_ID (attached to $VPC_ID)"
```

**NAT Gateways** (one per AZ for high availability):
```bash
# Allocate Elastic IPs for NAT Gateways
EIP_1=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
EIP_2=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)

# Create NAT Gateway in Public Subnet 1
NAT_GW_1=$(aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_1 \
  --tag-specifications 'ResourceType=natgateway,Tags=[
    {Key=Name,Value=ml-nat-gateway-1a}
  ]' \
  --query 'NatGateway.NatGatewayId' \
  --output text)

# Create NAT Gateway in Public Subnet 2
NAT_GW_2=$(aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_2 \
  --allocation-id $EIP_2 \
  --tag-specifications 'ResourceType=natgateway,Tags=[
    {Key=Name,Value=ml-nat-gateway-1b}
  ]' \
  --query 'NatGateway.NatGatewayId' \
  --output text)

# Wait for NAT Gateways to be available (takes 1-2 minutes)
echo "Waiting for NAT Gateways to be available..."
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GW_1 $NAT_GW_2

echo "NAT Gateways: $NAT_GW_1, $NAT_GW_2"
```

### Task 2.3: Create Route Tables

**Public Route Table** (routes to Internet Gateway):
```bash
# Create public route table
PUBLIC_RT=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[
    {Key=Name,Value=ml-public-rt}
  ]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# Associate with public subnets
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_1
aws ec2 associate-route-table --route-table-id $PUBLIC_RT --subnet-id $PUBLIC_SUBNET_2

echo "Public Route Table: $PUBLIC_RT"
```

**Private Route Tables** (routes to NAT Gateways):
```bash
# Private Route Table 1 (us-east-1a) → NAT Gateway 1
PRIVATE_RT_1=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[
    {Key=Name,Value=ml-private-rt-1a}
  ]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

aws ec2 create-route \
  --route-table-id $PRIVATE_RT_1 \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_1

# Associate with private subnet 1 and db subnet 1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $PRIVATE_SUBNET_1
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_1 --subnet-id $DB_SUBNET_1

# Private Route Table 2 (us-east-1b) → NAT Gateway 2
PRIVATE_RT_2=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[
    {Key=Name,Value=ml-private-rt-1b}
  ]' \
  --query 'RouteTable.RouteTableId' \
  --output text)

aws ec2 create-route \
  --route-table-id $PRIVATE_RT_2 \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GW_2

# Associate with private subnet 2 and db subnet 2
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $PRIVATE_SUBNET_2
aws ec2 associate-route-table --route-table-id $PRIVATE_RT_2 --subnet-id $DB_SUBNET_2

echo "Private Route Tables: $PRIVATE_RT_1, $PRIVATE_RT_2"
```

---

## Part 3: Security Groups (Defense in Depth)

### Task 3.1: Create Security Groups

**Bastion Host Security Group**:
```bash
# Get your public IP
MY_IP=$(curl -s https://checkip.amazonaws.com)

# Create bastion security group
BASTION_SG=$(aws ec2 create-security-group \
  --group-name bastion-sg \
  --description "Security group for bastion host" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[
    {Key=Name,Value=bastion-sg}
  ]' \
  --query 'GroupId' \
  --output text)

# Allow SSH from your IP only
aws ec2 authorize-security-group-ingress \
  --group-id $BASTION_SG \
  --protocol tcp \
  --port 22 \
  --cidr ${MY_IP}/32

echo "Bastion SG: $BASTION_SG (allows SSH from $MY_IP)"
```

**ALB Security Group**:
```bash
# Create ALB security group
ALB_SG=$(aws ec2 create-security-group \
  --group-name alb-sg \
  --description "Security group for Application Load Balancer" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[
    {Key=Name,Value=alb-sg}
  ]' \
  --query 'GroupId' \
  --output text)

# Allow HTTP from internet
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow HTTPS from internet
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

echo "ALB SG: $ALB_SG"
```

**Application Server Security Group**:
```bash
# Create app server security group
APP_SG=$(aws ec2 create-security-group \
  --group-name app-server-sg \
  --description "Security group for ML inference servers" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[
    {Key=Name,Value=app-server-sg}
  ]' \
  --query 'GroupId' \
  --output text)

# Allow port 5000 from ALB only
aws ec2 authorize-security-group-ingress \
  --group-id $APP_SG \
  --protocol tcp \
  --port 5000 \
  --source-group $ALB_SG

# Allow SSH from bastion only
aws ec2 authorize-security-group-ingress \
  --group-id $APP_SG \
  --protocol tcp \
  --port 22 \
  --source-group $BASTION_SG

echo "App Server SG: $APP_SG"
```

**Database Security Group**:
```bash
# Create database security group
DB_SG=$(aws ec2 create-security-group \
  --group-name database-sg \
  --description "Security group for RDS database" \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=security-group,Tags=[
    {Key=Name,Value=database-sg}
  ]' \
  --query 'GroupId' \
  --output text)

# Allow PostgreSQL (5432) from app servers only
aws ec2 authorize-security-group-ingress \
  --group-id $DB_SG \
  --protocol tcp \
  --port 5432 \
  --source-group $APP_SG

echo "Database SG: $DB_SG"
```

### Task 3.2: Verify Security Group Rules

**List All Security Groups**:
```bash
# View all security groups in VPC
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[].[GroupId,GroupName,Description]' \
  --output table

# Detailed view of app server security group
aws ec2 describe-security-groups \
  --group-ids $APP_SG \
  --query 'SecurityGroups[0].IpPermissions[]'
```

**Generate Security Matrix**:
```bash
cat > security-matrix.md <<EOF
# Security Group Rules Matrix

## Inbound Rules

| From | To | Port | Protocol | Purpose |
|------|-----|------|----------|---------|
| Your IP | Bastion | 22 | TCP | SSH access |
| Internet | ALB | 80, 443 | TCP | HTTP/HTTPS traffic |
| ALB | App Servers | 5000 | TCP | ML inference API |
| Bastion | App Servers | 22 | TCP | SSH for maintenance |
| App Servers | Database | 5432 | TCP | PostgreSQL queries |

## Security Principles Applied

1. **Least Privilege**: Each tier only accepts traffic from the previous tier
2. **No Direct Internet Access**: App and DB servers can't be accessed from internet
3. **Bastion Host**: Single point of entry for SSH (auditable)
4. **Port Restriction**: Only necessary ports are open
5. **Source-Based Rules**: Use security group references instead of CIDR blocks
EOF

cat security-matrix.md
```

---

## Part 4: Network ACLs (Additional Layer)

### Task 4.1: Create Network ACL for Public Subnets

**Why NACLs?** Stateless firewall at subnet level. Provides additional defense even if security groups are misconfigured.

**Create Public NACL**:
```bash
# Create NACL
PUBLIC_NACL=$(aws ec2 create-network-acl \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=network-acl,Tags=[
    {Key=Name,Value=ml-public-nacl}
  ]' \
  --query 'NetworkAcl.NetworkAclId' \
  --output text)

# INBOUND RULES
# Allow HTTP from internet
aws ec2 create-network-acl-entry \
  --network-acl-id $PUBLIC_NACL \
  --rule-number 100 \
  --protocol 6 \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --ingress \
  --rule-action allow

# Allow HTTPS from internet
aws ec2 create-network-acl-entry \
  --network-acl-id $PUBLIC_NACL \
  --rule-number 110 \
  --protocol 6 \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --ingress \
  --rule-action allow

# Allow SSH from your IP
aws ec2 create-network-acl-entry \
  --network-acl-id $PUBLIC_NACL \
  --rule-number 120 \
  --protocol 6 \
  --port-range From=22,To=22 \
  --cidr-block ${MY_IP}/32 \
  --ingress \
  --rule-action allow

# Allow return traffic (ephemeral ports)
aws ec2 create-network-acl-entry \
  --network-acl-id $PUBLIC_NACL \
  --rule-number 130 \
  --protocol 6 \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --ingress \
  --rule-action allow

# OUTBOUND RULES
# Allow all outbound (can be restricted further)
aws ec2 create-network-acl-entry \
  --network-acl-id $PUBLIC_NACL \
  --rule-number 100 \
  --protocol -1 \
  --cidr-block 0.0.0.0/0 \
  --egress \
  --rule-action allow

# Associate with public subnets
aws ec2 replace-network-acl-association \
  --association-id $(aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=$PUBLIC_SUBNET_1" --query 'NetworkAcls[0].Associations[0].NetworkAclAssociationId' --output text) \
  --network-acl-id $PUBLIC_NACL

aws ec2 replace-network-acl-association \
  --association-id $(aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=$PUBLIC_SUBNET_2" --query 'NetworkAcls[0].Associations[0].NetworkAclAssociationId' --output text) \
  --network-acl-id $PUBLIC_NACL

echo "Public NACL: $PUBLIC_NACL"
```

### Task 4.2: Create Network ACL for Private Subnets

**Create Private NACL**:
```bash
# Create NACL
PRIVATE_NACL=$(aws ec2 create-network-acl \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=network-acl,Tags=[
    {Key=Name,Value=ml-private-nacl}
  ]' \
  --query 'NetworkAcl.NetworkAclId' \
  --output text)

# Allow traffic from VPC CIDR only
aws ec2 create-network-acl-entry \
  --network-acl-id $PRIVATE_NACL \
  --rule-number 100 \
  --protocol -1 \
  --cidr-block 10.0.0.0/16 \
  --ingress \
  --rule-action allow

# Allow return traffic for internet-bound requests (via NAT)
aws ec2 create-network-acl-entry \
  --network-acl-id $PRIVATE_NACL \
  --rule-number 110 \
  --protocol 6 \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --ingress \
  --rule-action allow

# Outbound: Allow all
aws ec2 create-network-acl-entry \
  --network-acl-id $PRIVATE_NACL \
  --rule-number 100 \
  --protocol -1 \
  --cidr-block 0.0.0.0/0 \
  --egress \
  --rule-action allow

# Associate with private subnets
aws ec2 replace-network-acl-association \
  --association-id $(aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=$PRIVATE_SUBNET_1" --query 'NetworkAcls[0].Associations[0].NetworkAclAssociationId' --output text) \
  --network-acl-id $PRIVATE_NACL

aws ec2 replace-network-acl-association \
  --association-id $(aws ec2 describe-network-acls --filters "Name=association.subnet-id,Values=$PRIVATE_SUBNET_2" --query 'NetworkAcls[0].Associations[0].NetworkAclAssociationId' --output text) \
  --network-acl-id $PRIVATE_NACL

echo "Private NACL: $PRIVATE_NACL"
```

---

## Part 5: Deploy Bastion Host

### Task 5.1: Launch Bastion Host

**Why Bastion Host?** Single, auditable entry point for SSH access to private instances. Also called "jump box".

**Launch Bastion**:
```bash
# Get latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

# Launch bastion in public subnet
BASTION_INSTANCE=$(aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name ml-inference-key \
  --security-group-ids $BASTION_SG \
  --subnet-id $PUBLIC_SUBNET_1 \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=bastion-host},
    {Key=Project,Value=ml-infrastructure},
    {Key=Role,Value=bastion}
  ]' \
  --query 'Instances[0].InstanceId' \
  --output text)

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $BASTION_INSTANCE

# Get public IP
BASTION_IP=$(aws ec2 describe-instances \
  --instance-ids $BASTION_INSTANCE \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Bastion Host: $BASTION_INSTANCE at $BASTION_IP"
```

### Task 5.2: Configure SSH Agent Forwarding

**Why Agent Forwarding?** Allows you to SSH from bastion to private instances without copying your private key to the bastion.

**Configure SSH** (on your local machine):
```bash
# Add SSH key to agent
ssh-add ~/.ssh/ml-inference-key.pem

# Verify key is loaded
ssh-add -l

# SSH with agent forwarding
ssh -A ec2-user@$BASTION_IP

# Once on bastion, you can SSH to private instances
# ssh ubuntu@10.0.10.x
```

**Create SSH Config** (optional, for convenience):
```bash
cat >> ~/.ssh/config <<EOF

# Bastion Host
Host bastion
  HostName $BASTION_IP
  User ec2-user
  IdentityFile ~/.ssh/ml-inference-key.pem
  ForwardAgent yes

# Private instances (accessed via bastion)
Host 10.0.*.*
  User ubuntu
  ProxyJump bastion
EOF

# Now you can SSH directly to private instances:
# ssh 10.0.10.x  (automatically jumps through bastion)
```

---

## Part 6: Deploy Application Tier

### Task 6.1: Launch Application Servers

**Launch App Server 1** (in private subnet 1):
```bash
# Ubuntu AMI
UBUNTU_AMI=$(aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

APP_INSTANCE_1=$(aws ec2 run-instances \
  --image-id $UBUNTU_AMI \
  --instance-type t2.micro \
  --key-name ml-inference-key \
  --security-group-ids $APP_SG \
  --subnet-id $PRIVATE_SUBNET_1 \
  --iam-instance-profile Name=ml-inference-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=ml-app-server-1a},
    {Key=Project,Value=ml-infrastructure},
    {Key=Tier,Value=Application}
  ]' \
  --query 'Instances[0].InstanceId' \
  --output text)

# Launch App Server 2 (in private subnet 2)
APP_INSTANCE_2=$(aws ec2 run-instances \
  --image-id $UBUNTU_AMI \
  --instance-type t2.micro \
  --key-name ml-inference-key \
  --security-group-ids $APP_SG \
  --subnet-id $PRIVATE_SUBNET_2 \
  --iam-instance-profile Name=ml-inference-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=ml-app-server-1b},
    {Key=Project,Value=ml-infrastructure},
    {Key=Tier,Value=Application}
  ]' \
  --query 'Instances[0].InstanceId' \
  --output text)

# Wait for instances
aws ec2 wait instance-running --instance-ids $APP_INSTANCE_1 $APP_INSTANCE_2

# Get private IPs
APP_IP_1=$(aws ec2 describe-instances --instance-ids $APP_INSTANCE_1 --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)
APP_IP_2=$(aws ec2 describe-instances --instance-ids $APP_INSTANCE_2 --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text)

echo "App Servers: $APP_IP_1 (1a), $APP_IP_2 (1b)"
```

### Task 6.2: Test Connectivity

**Test Internet Access from Private Instance** (via NAT Gateway):
```bash
# SSH to bastion
ssh -A ec2-user@$BASTION_IP

# From bastion, SSH to app server 1
ssh ubuntu@$APP_IP_1

# Test internet access (should work via NAT Gateway)
ping -c 3 8.8.8.8
curl https://checkip.amazonaws.com

# Test S3 access (via IAM role)
aws s3 ls

# Exit back to local machine
exit
exit
```

---

## Part 7: VPC Flow Logs (Network Troubleshooting)

### Task 7.1: Enable VPC Flow Logs

**Why Flow Logs?** Capture IP traffic metadata for troubleshooting, security analysis, and compliance.

**Create CloudWatch Log Group**:
```bash
# Create log group
aws logs create-log-group --log-group-name /aws/vpc/flow-logs

# Set retention to 7 days
aws logs put-retention-policy \
  --log-group-name /aws/vpc/flow-logs \
  --retention-in-days 7
```

**Create IAM Role for Flow Logs**:
```bash
cat > flow-logs-trust-policy.json <<EOF
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
  --role-name vpc-flow-logs-role \
  --assume-role-policy-document file://flow-logs-trust-policy.json

cat > flow-logs-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name vpc-flow-logs-role \
  --policy-name vpc-flow-logs-policy \
  --policy-document file://flow-logs-policy.json

# Wait for role propagation
sleep 10
```

**Enable Flow Logs**:
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids $VPC_ID \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-destination arn:aws:logs:us-east-1:${ACCOUNT_ID}:log-group:/aws/vpc/flow-logs \
  --deliver-logs-permission-arn arn:aws:iam::${ACCOUNT_ID}:role/vpc-flow-logs-role \
  --tag-specifications 'ResourceType=vpc-flow-log,Tags=[
    {Key=Name,Value=ml-vpc-flow-logs}
  ]'
```

### Task 7.2: Query Flow Logs

**Wait for logs to accumulate** (5-10 minutes), then query:
```bash
# View recent flow log entries
aws logs tail /aws/vpc/flow-logs --follow

# Example flow log format:
# account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
```

**Analyze Traffic**:
```bash
# Count accepted vs rejected traffic
aws logs filter-log-events \
  --log-group-name /aws/vpc/flow-logs \
  --filter-pattern "ACCEPT" \
  --max-items 100 | grep -c "ACCEPT"

aws logs filter-log-events \
  --log-group-name /aws/vpc/flow-logs \
  --filter-pattern "REJECT" \
  --max-items 100 | grep -c "REJECT"
```

---

## Part 8: Terraform Implementation (Infrastructure as Code)

### Task 8.1: Convert VPC to Terraform

**Why Terraform?** Version control infrastructure, reproducible deployments, easier to manage complex environments.

**Create Terraform Configuration**:

```bash
mkdir terraform-vpc && cd terraform-vpc

# provider.tf
cat > provider.tf <<'EOF'
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "ml-terraform-state-REPLACE_WITH_ACCOUNT_ID"
    key    = "vpc/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ml-infrastructure"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
EOF

# variables.tf
cat > variables.tf <<'EOF'
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}
EOF

# vpc.tf
cat > vpc.tf <<'EOF'
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ml-infrastructure-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ml-infrastructure-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "ml-public-subnet-${var.availability_zones[count.index]}"
    Tier = "Public"
  }
}

# Private Subnets (App Tier)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "ml-private-subnet-${var.availability_zones[count.index]}"
    Tier = "Private-App"
  }
}

# Database Subnets
resource "aws_subnet" "database" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 20}.0/24"
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "ml-db-subnet-${var.availability_zones[count.index]}"
    Tier = "Database"
  }
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"

  tags = {
    Name = "ml-nat-eip-${count.index + 1}"
  }
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "ml-nat-gateway-${var.availability_zones[count.index]}"
  }

  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "ml-public-rt"
  }
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Route Tables
resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "ml-private-rt-${var.availability_zones[count.index]}"
  }
}

# Private Route Table Associations (App Subnets)
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Private Route Table Associations (Database Subnets)
resource "aws_route_table_association" "database" {
  count          = 2
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
EOF

# security-groups.tf
cat > security-groups.tf <<'EOF'
# Bastion Security Group
resource "aws_security_group" "bastion" {
  name        = "bastion-sg"
  description = "Security group for bastion host"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH from your IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.your_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "bastion-sg"
  }
}

# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "alb-sg"
  description = "Security group for Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS from internet"
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

  tags = {
    Name = "alb-sg"
  }
}

# App Server Security Group
resource "aws_security_group" "app" {
  name        = "app-server-sg"
  description = "Security group for ML inference servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ML API from ALB"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description     = "SSH from bastion"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "app-server-sg"
  }
}

# Database Security Group
resource "aws_security_group" "database" {
  name        = "database-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL from app servers"
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

  tags = {
    Name = "database-sg"
  }
}

variable "your_ip" {
  description = "Your public IP for SSH access to bastion"
  type        = string
}
EOF

# outputs.tf
cat > outputs.tf <<'EOF'
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "Database subnet IDs"
  value       = aws_subnet.database[*].id
}

output "nat_gateway_ips" {
  description = "NAT Gateway Elastic IPs"
  value       = aws_eip.nat[*].public_ip
}

output "security_group_ids" {
  description = "Security Group IDs"
  value = {
    bastion  = aws_security_group.bastion.id
    alb      = aws_security_group.alb.id
    app      = aws_security_group.app.id
    database = aws_security_group.database.id
  }
}
EOF
```

### Task 8.2: Deploy with Terraform

**Initialize and Apply**:
```bash
# Get your IP
YOUR_IP=$(curl -s https://checkip.amazonaws.com)

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
your_ip = "${YOUR_IP}/32"
environment = "dev"
EOF

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# View outputs
terraform output
```

**Verify**:
```bash
# Get VPC ID from Terraform output
terraform output -raw vpc_id

# Compare with manually created VPC
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=ml-infrastructure-vpc"
```

---

## Part 9: Validation and Testing

### Task 9.1: Network Connectivity Test Matrix

**Create Test Script**:
```bash
cat > network-test.sh <<'EOF'
#!/bin/bash

echo "=== Network Connectivity Tests ==="
echo ""

# Test 1: Bastion → App Server 1
echo "Test 1: Bastion → App Server 1 (SSH)"
ssh -A ec2-user@$BASTION_IP "ssh -o StrictHostKeyChecking=no ubuntu@$APP_IP_1 'echo SUCCESS'"

# Test 2: App Server 1 → Internet (via NAT)
echo "Test 2: App Server 1 → Internet (via NAT Gateway)"
ssh -A ec2-user@$BASTION_IP "ssh ubuntu@$APP_IP_1 'curl -s https://checkip.amazonaws.com'"

# Test 3: App Server 1 → S3 (via IAM role)
echo "Test 3: App Server 1 → S3 (via IAM role)"
ssh -A ec2-user@$BASTION_IP "ssh ubuntu@$APP_IP_1 'aws s3 ls | head -3'"

# Test 4: Internet → App Server 1 (should FAIL)
echo "Test 4: Internet → App Server 1 (should timeout - no public IP)"
timeout 5 ssh -i ~/.ssh/ml-inference-key.pem ubuntu@$APP_IP_1 && echo "FAIL: Direct access should not work" || echo "SUCCESS: Direct access blocked"

echo ""
echo "=== Tests Complete ==="
EOF

chmod +x network-test.sh
./network-test.sh
```

### Task 9.2: Security Audit

**Run Security Audit Script**:
```bash
cat > security-audit.sh <<'EOF'
#!/bin/bash

echo "=== VPC Security Audit ==="
echo ""

# Check for open security groups
echo "1. Security Groups with unrestricted access:"
aws ec2 describe-security-groups \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`] && (FromPort==`22` || ToPort==`22`)]].{GroupId:GroupId,GroupName:GroupName}' \
  --output table

# Check for unused security groups
echo ""
echo "2. Unused Security Groups:"
# (Complex query - omitted for brevity)

# Check NAT Gateway costs
echo ""
echo "3. NAT Gateway Monthly Cost Estimate:"
echo "   2 NAT Gateways × $0.045/hour × 730 hours = $65.70/month"
echo "   Data processing: ~$0.045/GB"

# Check flow logs enabled
echo ""
echo "4. VPC Flow Logs Status:"
aws ec2 describe-flow-logs --filter "Name=resource-id,Values=$VPC_ID"

echo ""
echo "=== Audit Complete ==="
EOF

chmod +x security-audit.sh
./security-audit.sh
```

---

## Part 10: Cost Optimization

### Task 10.1: VPC Endpoint for S3 (Save NAT Gateway Costs)

**Why VPC Endpoint?** S3 traffic via NAT Gateway costs $0.045/GB. VPC endpoint is free.

**Create VPC Endpoint**:
```bash
# Create S3 VPC endpoint (gateway type)
VPC_ENDPOINT=$(aws ec2 create-vpc-endpoint \
  --vpc-id $VPC_ID \
  --service-name com.amazonaws.us-east-1.s3 \
  --route-table-ids $PRIVATE_RT_1 $PRIVATE_RT_2 \
  --query 'VpcEndpoint.VpcEndpointId' \
  --output text)

echo "S3 VPC Endpoint: $VPC_ENDPOINT"

# Verify endpoint
aws ec2 describe-vpc-endpoints --vpc-endpoint-ids $VPC_ENDPOINT
```

**Test S3 Access** (now goes via VPC endpoint, not NAT Gateway):
```bash
ssh -A ec2-user@$BASTION_IP "ssh ubuntu@$APP_IP_1 'aws s3 ls'"
# Traffic now goes via VPC endpoint (free) instead of NAT Gateway ($0.045/GB)
```

---

## Cleanup

**Terminate Resources** (save costs):
```bash
# Terminate EC2 instances
aws ec2 terminate-instances --instance-ids $BASTION_INSTANCE $APP_INSTANCE_1 $APP_INSTANCE_2

# Wait for termination
aws ec2 wait instance-terminated --instance-ids $BASTION_INSTANCE $APP_INSTANCE_1 $APP_INSTANCE_2

# Delete NAT Gateways
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_1
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GW_2

# Wait for NAT Gateway deletion (takes 1-2 minutes)
sleep 120

# Release Elastic IPs
aws ec2 release-address --allocation-id $EIP_1
aws ec2 release-address --allocation-id $EIP_2

# Delete VPC (this deletes subnets, route tables, IGW, etc.)
aws ec2 delete-vpc --vpc-id $VPC_ID

# Or use Terraform to destroy everything:
# cd terraform-vpc && terraform destroy
```

---

## Deliverables

By the end of this exercise, you should have:

1. ✅ Production VPC with multi-tier architecture (public, private, database subnets)
2. ✅ Multi-AZ deployment for high availability
3. ✅ Defense-in-depth security (Security Groups + NACLs)
4. ✅ Bastion host for secure SSH access
5. ✅ VPC Flow Logs for network troubleshooting
6. ✅ NAT Gateways for private subnet internet access
7. ✅ VPC Endpoint for cost-optimized S3 access
8. ✅ Terraform infrastructure as code implementation

**Evidence**:
- VPC architecture diagram
- Security group rules matrix
- Network connectivity test results
- Terraform configuration files

---

## Next Steps

You now have a production-ready VPC! Next:
- **Exercise 04**: Deploy containerized ML service with ECS/EKS on this VPC
- **Exercise 05**: Add RDS database, SageMaker integration, and cost optimization

Excellent work mastering AWS networking and security! 🚀
