# Lecture 02: AWS Core Services for AI Infrastructure

## Lecture Overview

Amazon Web Services offers 200+ services, but mastering a core set of foundational services enables you to build robust AI/ML infrastructure. This lecture provides hands-on coverage of the essential AWS services you'll use daily: EC2 for compute, S3 for storage, RDS for databases, and IAM for security and access management.

You'll learn through practical AWS CLI examples how to provision virtual machines, manage object storage, deploy managed databases, and implement least-privilege security policies. By the end, you'll be confident navigating the AWS console, automating tasks via CLI, and architecting basic cloud infrastructure for ML workloads.

**Estimated Reading Time:** 75-90 minutes
**Hands-on Companion Lab:** Exercise 02 – Compute & Storage Foundations
**Prerequisites:** AWS account with free tier, AWS CLI installed and configured, basic Linux command line skills

### Learning Objectives

By the end of this lecture, you will:
- Configure AWS CLI with IAM credentials and named profiles
- Launch and manage EC2 instances for ML workloads
- Create and configure S3 buckets for ML data storage
- Deploy RDS databases for application metadata
- Implement IAM policies following least-privilege principles
- Automate AWS resource management using CLI commands
- Design security architectures using IAM roles and policies

---

## 1. AWS Account Setup and Configuration

### 1.1 AWS Free Tier Overview

AWS offers a **12-month free tier** for new accounts, plus always-free services:

**12-Month Free Tier:**
- **EC2**: 750 hours/month of t2.micro or t3.micro instances
- **S3**: 5GB standard storage, 20,000 GET requests, 2,000 PUT requests
- **RDS**: 750 hours/month of db.t2.micro, 20GB storage
- **Lambda**: 1M requests/month, 400,000 GB-seconds of compute
- **CloudWatch**: 10 custom metrics, 10 alarms

**Always Free:**
- **DynamoDB**: 25GB storage, 25 read/write capacity units
- **Lambda**: 1M requests/month (ongoing)
- **SNS**: 1M publishes/month

**Trial Offers (Limited Time):**
- **SageMaker**: 250 hours/month of notebook instances (2 months)
- **Rekognition**: 5,000 images/month (12 months)

**Cost Management Tips:**
- **Set billing alerts**: Alert when charges exceed $10, $50, $100
- **Use Cost Explorer**: Track spending by service
- **Tag resources**: `Environment=dev`, `Owner=your-name`
- **Stop instances when not in use**: t2.micro costs $0.0116/hour = $8.40/month if left running

### 1.2 AWS CLI Installation and Configuration

**Install AWS CLI v2:**

```bash
# Linux/macOS
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify
aws --version
# Output: aws-cli/2.15.0 Python/3.11.6 Linux/5.10.0 exe/x86_64.ubuntu.22
```

**Configure AWS CLI:**

```bash
# Interactive configuration
aws configure

# Prompts:
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json

# Configuration stored in:
~/.aws/credentials  # Access keys
~/.aws/config       # Default region and output format
```

**Create IAM User for CLI (Best Practice):**

```bash
# DON'T use root account access keys!
# Create IAM user via console:
# IAM → Users → Add User → Programmatic Access → Attach AdministratorAccess policy

# Configure named profile for different accounts/roles
aws configure --profile ml-dev
AWS Access Key ID: AKIAIOSFODNN7DEVEXAMPLE
AWS Secret Access Key: ...
Default region name: us-west-2
Default output format: json

# Use profile:
aws s3 ls --profile ml-dev
```

**Test Configuration:**

```bash
# List S3 buckets (should return empty list for new account)
aws s3 ls

# Get caller identity (verify which account/user you're authenticated as)
aws sts get-caller-identity
{
  "UserId": "AIDACKCEVSQ6C2EXAMPLE",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

### 1.3 AWS Regions and Availability Zones

**Regions:** Geographic locations where AWS has data centers (us-east-1, eu-west-1, ap-southeast-1, etc.)

**Choosing a Region:**
- **Latency**: Pick region closest to users (us-east-1 for US East Coast, eu-west-1 for Europe)
- **Compliance**: Data residency requirements (GDPR, HIPAA)
- **Service Availability**: Not all services available in all regions (check AWS Regional Services list)
- **Cost**: Pricing varies by region (us-east-1 is often cheapest)

**Availability Zones (AZs):** Isolated data centers within a region (us-east-1a, us-east-1b, us-east-1c)

**Why AZs Matter:**
- **Fault Isolation**: Each AZ has independent power, cooling, networking
- **High Availability**: Deploy across multiple AZs; if one fails, others continue
- **Low Latency**: AZs in same region connected by high-speed, low-latency network

**Example:**
```bash
# List availability zones in your region
aws ec2 describe-availability-zones --region us-east-1

# Output:
{
  "AvailabilityZones": [
    {
      "ZoneName": "us-east-1a",
      "State": "available",
      "RegionName": "us-east-1"
    },
    {
      "ZoneName": "us-east-1b",
      "State": "available",
      "RegionName": "us-east-1"
    },
    ...
  ]
}
```

---

## 2. EC2 (Elastic Compute Cloud) - Virtual Machines

### 2.1 EC2 Fundamentals

**EC2 = Virtual Machines in the Cloud**

**Instance Types:**
- **General Purpose**: t3, m5 (balanced CPU, memory, network)
- **Compute Optimized**: c5, c6i (high CPU, for compute-bound workloads)
- **Memory Optimized**: r5, x1 (high RAM, for large datasets in memory)
- **Storage Optimized**: i3, d2 (high disk throughput, for databases)
- **Accelerated Computing**: p3, p4 (GPU instances for ML training/inference), inf1 (AWS Inferentia for inference)

**Instance Naming Convention:**
```
p3.2xlarge
│ │  │
│ │  └─ Size (nano, micro, small, medium, large, xlarge, 2xlarge, ...)
│ └──── Generation (3 = 3rd generation)
└────── Family (p = GPU optimized)
```

**Free Tier Instance:** `t2.micro` or `t3.micro` (1 vCPU, 1GB RAM, 750 hours/month free)

**GPU Instances for ML:**
- **p3.2xlarge**: 1 NVIDIA V100 GPU, 8 vCPUs, 61GB RAM (~$3/hour)
- **p3.8xlarge**: 4 V100 GPUs, 32 vCPUs, 244GB RAM (~$12/hour)
- **p4d.24xlarge**: 8 A100 GPUs, 96 vCPUs, 1.1TB RAM (~$32/hour)
- **g4dn.xlarge**: 1 NVIDIA T4 GPU, 4 vCPUs, 16GB RAM (~$0.50/hour, cost-effective inference)

### 2.2 Launching an EC2 Instance (CLI)

**Step 1: Create a Key Pair (for SSH access):**

```bash
# Create SSH key pair
aws ec2 create-key-pair \
  --key-name my-ml-keypair \
  --query 'KeyMaterial' \
  --output text > my-ml-keypair.pem

# Set correct permissions
chmod 400 my-ml-keypair.pem

# Key pair stored in AWS; private key saved locally
```

**Step 2: Find an Amazon Machine Image (AMI):**

```bash
# Find Ubuntu 22.04 LTS AMI in us-east-1
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images[*].[ImageId,Name,CreationDate]' \
  --output table | head -20

# Note the latest ImageId (e.g., ami-0c55b159cbfafe1f0)
```

**Step 3: Launch Instance:**

```bash
# Launch t2.micro instance (free tier)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-ml-keypair \
  --security-group-ids sg-0123456789abcdef0 \
  --subnet-id subnet-0abcdef1234567890 \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ml-dev-server},{Key=Environment,Value=dev},{Key=Owner,Value=your-name}]'

# Output includes InstanceId (e.g., i-0abcdef1234567890)
```

**Step 4: Wait for Instance to Start:**

```bash
# Check instance status
aws ec2 describe-instances \
  --instance-ids i-0abcdef1234567890 \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' \
  --output table

# Wait for "running" status and note PublicIpAddress
```

**Step 5: SSH into Instance:**

```bash
# SSH using key pair
ssh -i my-ml-keypair.pem ubuntu@<PUBLIC_IP>

# Once connected:
ubuntu@ip-172-31-0-123:~$ python3 --version
Python 3.10.6

# Install ML libraries
sudo apt update
sudo apt install -y python3-pip
pip3 install torch torchvision numpy pandas
```

### 2.3 EC2 Instance Lifecycle Management

**Stop Instance (preserves data, no compute charges):**

```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-0abcdef1234567890

# Instance state: running → stopping → stopped
# You still pay for EBS storage, but not compute
```

**Start Instance:**

```bash
# Start stopped instance
aws ec2 start-instances --instance-ids i-0abcdef1234567890

# Instance gets NEW public IP (unless using Elastic IP)
```

**Terminate Instance (delete permanently):**

```bash
# Terminate instance
aws ec2 terminate-instances --instance-ids i-0abcdef1234567890

# Instance state: running → shutting-down → terminated
# EBS volumes deleted (unless set to persist)
```

**Reboot Instance:**

```bash
# Reboot (graceful restart, keeps same IPs)
aws ec2 reboot-instances --instance-ids i-0abcdef1234567890
```

**Best Practices:**
- **Tag everything**: Name, Environment, Owner, Project, CostCenter
- **Stop instances** when not in use (dev/test environments)
- **Use CloudWatch alarms** to auto-stop idle instances
- **Enable termination protection** for production instances

### 2.4 EC2 User Data (Bootstrap Scripts)

**User Data** = Script that runs on instance launch (automate setup)

**Example: Launch EC2 with PyTorch Pre-installed:**

```bash
# Create user data script
cat > user-data.sh <<'EOF'
#!/bin/bash
# This script runs at instance launch

# Update system
apt-get update -y

# Install Python and pip
apt-get install -y python3-pip

# Install ML libraries
pip3 install torch torchvision torchaudio \
  pandas numpy scikit-learn jupyter matplotlib

# Create Jupyter config
mkdir -p /home/ubuntu/.jupyter
cat > /home/ubuntu/.jupyter/jupyter_notebook_config.py <<EOL
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888
EOL

# Start Jupyter in background
su - ubuntu -c "nohup jupyter notebook --no-browser --port=8888 > /home/ubuntu/jupyter.log 2>&1 &"

echo "Setup complete! Jupyter running on port 8888"
EOF

# Launch instance with user data
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --key-name my-ml-keypair \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ml-jupyter-server}]'

# After instance starts, Jupyter is running
# Access: http://<PUBLIC_IP>:8888
```

**User Data Logs:**
```bash
# SSH to instance and check user data execution
sudo cat /var/log/cloud-init-output.log
```

### 2.5 EC2 Storage Options

**1. Instance Store (Ephemeral)**
- **Physically attached** to host machine
- **Temporary**: Lost when instance stops/terminates
- **High performance**: NVMe SSDs, low latency
- **Use case**: Temporary processing, caches, scratch space

**2. EBS (Elastic Block Store)**
- **Network-attached** block storage (like a hard drive)
- **Persistent**: Data survives instance stop/start
- **Types**:
  - **gp3**: General purpose SSD (3,000-16,000 IOPS, $0.08/GB/month)
  - **io2**: Provisioned IOPS SSD (up to 64,000 IOPS, low latency databases)
  - **st1**: Throughput-optimized HDD (big data, log processing)
  - **sc1**: Cold HDD (archival, infrequent access)

**Create and Attach EBS Volume:**

```bash
# Create 100GB EBS volume in same AZ as instance
aws ec2 create-volume \
  --availability-zone us-east-1a \
  --size 100 \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[{Key=Name,Value=ml-data-volume}]'

# Note VolumeId (e.g., vol-0abcdef1234567890)

# Attach to instance
aws ec2 attach-volume \
  --volume-id vol-0abcdef1234567890 \
  --instance-id i-0abcdef1234567890 \
  --device /dev/sdf

# SSH to instance and format/mount
sudo mkfs -t ext4 /dev/sdf
sudo mkdir /mnt/ml-data
sudo mount /dev/sdf /mnt/ml-data

# Persist mount across reboots
echo '/dev/sdf /mnt/ml-data ext4 defaults,nofail 0 2' | sudo tee -a /etc/fstab
```

**EBS Snapshots (Backups):**

```bash
# Create snapshot of EBS volume
aws ec2 create-snapshot \
  --volume-id vol-0abcdef1234567890 \
  --description "ML data backup before experiment"

# Restore from snapshot (create new volume)
aws ec2 create-volume \
  --snapshot-id snap-0123456789abcdef0 \
  --availability-zone us-east-1a
```

### 2.6 EC2 Pricing Strategies

**1. On-Demand (Default)**
- **Price**: $0.0116/hour for t2.micro
- **Use**: Development, unpredictable workloads
- **Billing**: Per second (1-hour minimum for some instances)

**2. Reserved Instances**
- **Commitment**: 1 or 3 years
- **Discount**: Up to 72% vs on-demand
- **Payment**: All upfront, partial upfront, no upfront
- **Use**: Steady-state production workloads

**3. Spot Instances**
- **Price**: Up to 90% discount (market-based pricing)
- **Risk**: Can be terminated with 2-minute warning
- **Use**: Fault-tolerant workloads (batch processing, ML training with checkpointing)

**Example Spot Request:**

```bash
# Request spot instance
aws ec2 request-spot-instances \
  --spot-price "0.05" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification '{
    "ImageId": "ami-0c55b159cbfafe1f0",
    "InstanceType": "p3.2xlarge",
    "KeyName": "my-ml-keypair"
  }'

# Monitor spot instance
aws ec2 describe-spot-instance-requests
```

**4. Savings Plans**
- **Commitment**: $/hour for 1-3 years
- **Flexibility**: Can change instance types/regions
- **Discount**: Up to 72%
- **Use**: Flexible compute commitment

**Cost Comparison (p3.2xlarge, 1 GPU):**
- **On-Demand**: $3.06/hour = $2,203/month (24/7)
- **1-Year Reserved**: $1.84/hour = $1,325/month (40% savings)
- **3-Year Reserved**: $1.23/hour = $886/month (60% savings)
- **Spot**: $0.92/hour = $662/month (70% savings, interruptible)

---

## 3. S3 (Simple Storage Service) - Object Storage

### 3.1 S3 Fundamentals

**S3 = Object Storage** (files + metadata, accessible via HTTP/HTTPS)

**Key Concepts:**
- **Bucket**: Container for objects (globally unique name)
- **Object**: File + metadata (max 5TB)
- **Key**: Unique identifier for object (like a file path)

**Use Cases for AI/ML:**
- **Data Lake**: Store raw training data (images, text, logs)
- **Model Artifacts**: Store trained models (.pt, .h5, .pkl files)
- **Feature Store**: Store precomputed features (Parquet files)
- **Results**: Store prediction outputs, experiment results

**Bucket Naming Rules:**
- Globally unique across all AWS accounts
- 3-63 characters, lowercase, no underscores
- Example: `my-ml-training-data-123456789`

### 3.2 S3 Bucket Operations (CLI)

**Create Bucket:**

```bash
# Create bucket in us-east-1
aws s3 mb s3://my-ml-training-data-123456789 --region us-east-1

# Verify bucket created
aws s3 ls
# Output: 2025-10-23 12:00:00 my-ml-training-data-123456789
```

**Upload Files:**

```bash
# Upload single file
aws s3 cp model.pth s3://my-ml-training-data-123456789/models/

# Upload directory (recursive)
aws s3 cp ./training-data/ s3://my-ml-training-data-123456789/data/ --recursive

# Sync directory (only uploads changed files)
aws s3 sync ./training-data/ s3://my-ml-training-data-123456789/data/
```

**Download Files:**

```bash
# Download single file
aws s3 cp s3://my-ml-training-data-123456789/models/model.pth ./

# Download directory
aws s3 cp s3://my-ml-training-data-123456789/data/ ./training-data/ --recursive

# Sync to local (download only new/changed files)
aws s3 sync s3://my-ml-training-data-123456789/data/ ./training-data/
```

**List Objects:**

```bash
# List all objects in bucket
aws s3 ls s3://my-ml-training-data-123456789/ --recursive

# List objects with size and timestamp
aws s3 ls s3://my-ml-training-data-123456789/models/ --human-readable

# Output:
2025-10-23 12:30:00  150.5 MiB model-v1.0.pth
2025-10-23 13:45:00  200.1 MiB model-v1.1.pth
```

**Delete Objects:**

```bash
# Delete single object
aws s3 rm s3://my-ml-training-data-123456789/models/old-model.pth

# Delete all objects in prefix
aws s3 rm s3://my-ml-training-data-123456789/experiments/failed/ --recursive

# Delete bucket (must be empty first)
aws s3 rb s3://my-ml-training-data-123456789 --force
# --force deletes all objects first, then bucket
```

### 3.3 S3 Storage Classes and Lifecycle Policies

**Storage Classes:**

| Class | Use Case | Retrieval | Cost ($/GB/month) |
|-------|----------|-----------|-------------------|
| **S3 Standard** | Frequent access | Immediate | $0.023 |
| **S3 Intelligent-Tiering** | Unknown access patterns | Immediate | $0.023-$0.0125 (auto) |
| **S3 Standard-IA** | Infrequent access | Immediate | $0.0125 |
| **S3 One Zone-IA** | Infrequent, non-critical | Immediate | $0.01 |
| **S3 Glacier Instant Retrieval** | Archive, instant access | Milliseconds | $0.004 |
| **S3 Glacier Flexible Retrieval** | Archive | Minutes-hours | $0.0036 |
| **S3 Glacier Deep Archive** | Long-term archive | Hours | $0.00099 |

**Lifecycle Policy Example:**

```bash
# Create lifecycle policy JSON
cat > lifecycle-policy.json <<'EOF'
{
  "Rules": [
    {
      "Id": "MoveOldExperimentsToGlacier",
      "Status": "Enabled",
      "Prefix": "experiments/",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    },
    {
      "Id": "DeleteTempFiles",
      "Status": "Enabled",
      "Prefix": "temp/",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
EOF

# Apply lifecycle policy to bucket
aws s3api put-bucket-lifecycle-configuration \
  --bucket my-ml-training-data-123456789 \
  --lifecycle-configuration file://lifecycle-policy.json
```

**Cost Savings Example:**
- **Scenario**: 1TB of experiment data, accessed only for first 30 days
- **S3 Standard (always)**: $23/month × 12 months = $276/year
- **With lifecycle**:
  - Month 1: Standard ($23)
  - Months 2-3: Standard-IA ($12.50 × 2 = $25)
  - Months 4-12: Glacier ($3.60 × 9 = $32.40)
  - **Total**: $80.40/year (71% savings)

### 3.4 S3 Versioning and Backup

**Enable Versioning:**

```bash
# Enable versioning on bucket
aws s3api put-bucket-versioning \
  --bucket my-ml-training-data-123456789 \
  --versioning-configuration Status=Enabled

# Now every upload creates a new version (old versions retained)
```

**Access Previous Versions:**

```bash
# List all versions of an object
aws s3api list-object-versions \
  --bucket my-ml-training-data-123456789 \
  --prefix models/model.pth

# Download specific version
aws s3api get-object \
  --bucket my-ml-training-data-123456789 \
  --key models/model.pth \
  --version-id "3/L4kqtJlcpXroDTDmpUMLUo" \
  ./model-old-version.pth
```

**Why Versioning for ML:**
- **Model Rollback**: Revert to previous model if new version performs poorly
- **Experiment Reproducibility**: Access exact data/code used in past experiments
- **Accidental Deletion Protection**: Recover deleted files

### 3.5 S3 Security and Access Control

**Bucket Policies (Resource-Based):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-public-models-bucket/*"
    }
  ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
  --bucket my-public-models-bucket \
  --policy file://bucket-policy.json
```

**IAM Policies (User-Based):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-ml-training-data-123456789",
        "arn:aws:s3:::my-ml-training-data-123456789/*"
      ]
    }
  ]
}
```

**Encryption:**

```bash
# Enable default encryption (AES-256)
aws s3api put-bucket-encryption \
  --bucket my-ml-training-data-123456789 \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# All new objects automatically encrypted
```

**Access Logging:**

```bash
# Enable S3 access logging
aws s3api put-bucket-logging \
  --bucket my-ml-training-data-123456789 \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "my-logs-bucket",
      "TargetPrefix": "s3-access-logs/"
    }
  }'
```

---

## 4. RDS (Relational Database Service)

### 4.1 RDS Overview

**RDS = Managed Relational Databases**

**Supported Engines:**
- **MySQL**
- **PostgreSQL** (recommended for ML: supports JSON, vector extensions)
- **MariaDB**
- **Oracle**
- **SQL Server**
- **Aurora** (AWS proprietary, MySQL/PostgreSQL compatible, 5x faster)

**Why RDS for ML:**
- **Metadata Storage**: Experiment tracking (MLflow backend)
- **Feature Store**: Serve features for real-time inference
- **Application Backend**: User data, prediction history
- **Analytics**: Query results, metrics

**RDS vs Self-Managed Database:**
- **RDS Handles**: Backups, patching, high availability, scaling
- **You Handle**: Schema design, queries, application integration

### 4.2 Launching an RDS Instance (CLI)

**Create PostgreSQL Database:**

```bash
# Create RDS instance (db.t3.micro, free tier eligible)
aws rds create-db-instance \
  --db-instance-identifier ml-metadata-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password 'YourSecurePassword123!' \
  --allocated-storage 20 \
  --storage-type gp3 \
  --backup-retention-period 7 \
  --publicly-accessible \
  --tags Key=Name,Value=ml-metadata-db Key=Environment,Value=dev

# Wait for "available" status (takes 5-10 minutes)
aws rds wait db-instance-available --db-instance-identifier ml-metadata-db

# Get connection endpoint
aws rds describe-db-instances \
  --db-instance-identifier ml-metadata-db \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
# Output: ml-metadata-db.c9akznl4qo5q.us-east-1.rds.amazonaws.com
```

**Connect to RDS:**

```bash
# Install PostgreSQL client
sudo apt install -y postgresql-client

# Connect
psql -h ml-metadata-db.c9akznl4qo5q.us-east-1.rds.amazonaws.com \
     -U admin \
     -d postgres

# Inside psql:
postgres=> CREATE DATABASE mlflow;
postgres=> \c mlflow
mlflow=> CREATE TABLE experiments (
  experiment_id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  artifact_location VARCHAR(500)
);
```

### 4.3 RDS High Availability (Multi-AZ)

**Multi-AZ Deployment:**

```bash
# Create Multi-AZ RDS (automatic failover)
aws rds create-db-instance \
  --db-instance-identifier ml-prod-db \
  --db-instance-class db.t3.small \
  --engine postgres \
  --engine-version 15.3 \
  --master-username admin \
  --master-user-password 'YourSecurePassword123!' \
  --allocated-storage 100 \
  --multi-az \
  --backup-retention-period 30

# AWS automatically:
# - Maintains standby replica in different AZ
# - Synchronous replication
# - Auto-failover in 60-120 seconds if primary fails
```

**Read Replicas (for read scaling):**

```bash
# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier ml-prod-db-replica \
  --source-db-instance-identifier ml-prod-db

# Use read replica for analytics queries (offload primary)
```

### 4.4 RDS Snapshots and Backups

**Automated Backups:**
- Enabled by default, retention 1-35 days
- Point-in-time recovery (restore to any second within retention)

**Manual Snapshots:**

```bash
# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ml-metadata-db \
  --db-snapshot-identifier ml-metadata-backup-2025-10-23

# List snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier ml-metadata-db

# Restore from snapshot (creates new instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ml-metadata-db-restored \
  --db-snapshot-identifier ml-metadata-backup-2025-10-23
```

### 4.5 RDS Cost Optimization

**Pricing:**
- **Instance**: Charged per hour (db.t3.micro: $0.017/hour = $12/month)
- **Storage**: $0.115/GB/month (gp3)
- **Backup**: First 100GB free, then $0.095/GB/month
- **Data Transfer**: Inbound free, outbound $0.09/GB

**Cost Optimization Tips:**
- **Stop instances** in dev/test (storage charges continue)
- **Use reserved instances** for production (up to 69% savings)
- **Delete old snapshots** (keep only necessary)
- **Use Aurora Serverless** for variable workloads (pay per second)

```bash
# Stop RDS instance (dev environment)
aws rds stop-db-instance --db-instance-identifier ml-metadata-db

# Start when needed
aws rds start-db-instance --db-instance-identifier ml-metadata-db
```

---

## 5. IAM (Identity and Access Management)

### 5.1 IAM Fundamentals

**IAM = Who can do what in AWS**

**Core Concepts:**
- **Users**: Individual people or applications
- **Groups**: Collection of users (e.g., "Developers", "Data Scientists")
- **Roles**: Temporary credentials for services/applications
- **Policies**: JSON documents defining permissions

**Best Practices:**
- **Never use root account** for daily tasks
- **Enable MFA** (Multi-Factor Authentication)
- **Principle of Least Privilege**: Grant minimum required permissions
- **Use roles** for EC2/Lambda, not hardcoded access keys

### 5.2 IAM Users and Groups

**Create IAM User:**

```bash
# Create user
aws iam create-user --user-name alice

# Add user to group
aws iam add-user-to-group --user-name alice --group-name DataScientists

# Create access key (for CLI/SDK)
aws iam create-access-key --user-name alice
{
  "AccessKey": {
    "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "UserName": "alice"
  }
}

# Alice configures her CLI
aws configure
# Uses the above access key and secret
```

**Create IAM Group with Policy:**

```bash
# Create group
aws iam create-group --group-name DataScientists

# Attach AWS managed policy
aws iam attach-group-policy \
  --group-name DataScientists \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach custom policy (see below)
aws iam put-group-policy \
  --group-name DataScientists \
  --policy-name SageMakerAccess \
  --policy-document file://sagemaker-policy.json
```

### 5.3 IAM Policies

**Policy Structure:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",  // or "Deny"
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-ml-training-data-123456789/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

**Example Policy: Data Scientist Access:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3DataAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::ml-training-data",
        "arn:aws:s3:::ml-training-data/*"
      ]
    },
    {
      "Sid": "SageMakerFullAccess",
      "Effect": "Allow",
      "Action": "sagemaker:*",
      "Resource": "*"
    },
    {
      "Sid": "EC2ReadOnly",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:Get*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyExpensiveInstances",
      "Effect": "Deny",
      "Action": "ec2:RunInstances",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringNotEquals": {
          "ec2:InstanceType": [
            "t2.micro",
            "t3.micro",
            "t3.small"
          ]
        }
      }
    }
  ]
}
```

**Attach Policy to User:**

```bash
# Save policy to file
cat > data-scientist-policy.json <<'EOF'
{...policy JSON...}
EOF

# Create custom policy
aws iam create-policy \
  --policy-name DataScientistPolicy \
  --policy-document file://data-scientist-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name alice \
  --policy-arn arn:aws:iam::123456789012:policy/DataScientistPolicy
```

### 5.4 IAM Roles (for Services)

**Why Roles?**
- EC2 instance needs to access S3 (don't hardcode access keys!)
- Lambda function needs to write to DynamoDB
- ECS task needs to pull image from ECR

**Create Role for EC2:**

```bash
# Create trust policy (who can assume this role)
cat > ec2-trust-policy.json <<'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name EC2-S3-Access-Role \
  --assume-role-policy-document file://ec2-trust-policy.json

# Attach S3 access policy to role
aws iam attach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Create instance profile (EC2 specific wrapper for role)
aws iam create-instance-profile --instance-profile-name EC2-S3-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-Profile \
  --role-name EC2-S3-Access-Role

# Launch EC2 with role
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t2.micro \
  --iam-instance-profile Name=EC2-S3-Profile
```

**Now EC2 instance can access S3 without access keys:**

```bash
# SSH to instance
ssh -i keypair.pem ubuntu@<PUBLIC_IP>

# AWS CLI automatically uses instance role
aws s3 ls s3://my-ml-training-data-123456789/
# Works! No credentials configured on instance
```

### 5.5 MFA (Multi-Factor Authentication)

**Enable MFA for IAM User:**

```bash
# Enable virtual MFA device (Google Authenticator, Authy)
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name alice-mfa \
  --outfile alice-mfa-qr.png \
  --bootstrap-method QRCodePNG

# Scan QR code with authenticator app, get two codes

# Activate MFA
aws iam enable-mfa-device \
  --user-name alice \
  --serial-number arn:aws:iam::123456789012:mfa/alice-mfa \
  --authentication-code1 123456 \
  --authentication-code2 789012
```

**MFA-Protected Actions:**

```json
{
  "Effect": "Deny",
  "Action": "ec2:TerminateInstances",
  "Resource": "*",
  "Condition": {
    "BoolIfExists": {
      "aws:MultiFactorAuthPresent": "false"
    }
  }
}
```

---

## 6. Putting It All Together: ML Inference Architecture

**Scenario:** Deploy a trained PyTorch model for real-time inference.

**Architecture:**

```
User Request → [ALB] → [EC2 Auto-Scaling Group]
                             ├─ EC2 Instance 1 (with IAM role)
                             ├─ EC2 Instance 2
                             └─ EC2 Instance 3
                                   ↓
                             [S3: model artifacts]
                                   ↓
                             [RDS: request logs, predictions]
```

**Implementation Steps:**

**1. Store Model in S3:**
```bash
aws s3 cp model.pth s3://my-ml-models/pytorch-classifier/v1.0/model.pth
```

**2. Create IAM Role for EC2 (S3 + RDS access):**
```bash
# Create role with S3 read + RDS write permissions (see section 5.4)
```

**3. Launch EC2 Instances with User Data:**
```bash
# user-data.sh
#!/bin/bash
apt-get update -y
apt-get install -y python3-pip postgresql-client
pip3 install torch flask boto3 psycopg2-binary

# Download model from S3
aws s3 cp s3://my-ml-models/pytorch-classifier/v1.0/model.pth /opt/model.pth

# Start inference server
cat > /opt/server.py <<EOF
import torch
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)
model = torch.load('/opt/model.pth')
model.eval()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json['features']
    input_tensor = torch.tensor(data)
    with torch.no_grad():
        prediction = model(input_tensor).item()

    # Log to RDS
    conn = psycopg2.connect(
        host='ml-metadata-db.abc123.us-east-1.rds.amazonaws.com',
        database='predictions',
        user='admin',
        password='SecurePass123!'
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO predictions (input, output) VALUES (%s, %s)", (str(data), prediction))
    conn.commit()
    conn.close()

    return jsonify({'prediction': prediction})

app.run(host='0.0.0.0', port=5000)
EOF

python3 /opt/server.py
```

**4. Create Load Balancer (CLI omitted, use Console or Terraform):**
- Points to Auto-Scaling Group
- Health checks: `/health` endpoint
- Distributes traffic across instances

**5. Test:**
```bash
curl -X POST http://my-alb-123456.us-east-1.elb.amazonaws.com/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 0.3, 0.8]}'

# Response: {"prediction": 0.92}
```

---

## 7. Key Takeaways

1. **EC2** provides flexible compute; choose instance types based on workload (GPU for training, CPU for lightweight inference).

2. **S3** is the backbone of ML data storage; use lifecycle policies to optimize costs (move old experiments to Glacier).

3. **RDS** manages databases for you; use for metadata, feature serving, and application backends.

4. **IAM** is critical for security; use roles for EC2/Lambda, enforce least privilege, enable MFA.

5. **AWS CLI** automates everything; learn it to script infrastructure provisioning and reduce manual work.

6. **Cost Management**: Stop instances when not in use, use spot instances for training, leverage free tier, set billing alerts.

---

## What's Next?

**Lecture 03** covers **Networking & Security**—VPCs, subnets, security groups, NACLs, and advanced IAM policies. You'll learn to design secure, isolated network architectures for production ML systems.

**Exercise 02** provides hands-on practice provisioning EC2 instances, attaching EBS volumes, uploading datasets to S3, and deploying RDS databases—all via Terraform and AWS CLI.

---

## Further Reading

- **AWS EC2 User Guide**: https://docs.aws.amazon.com/ec2/
- **AWS S3 User Guide**: https://docs.aws.amazon.com/s3/
- **AWS RDS User Guide**: https://docs.aws.amazon.com/rds/
- **AWS IAM Best Practices**: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **AWS CLI Reference**: https://awscli.amazonaws.com/v2/documentation/api/latest/index.html

---

**End of Lecture 02**
