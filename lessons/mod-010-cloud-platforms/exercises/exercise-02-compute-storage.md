# Exercise 02: Compute & Storage Foundations

**Module**: Cloud Platforms
**Difficulty**: Beginner
**Estimated Time**: 3-4 hours
**Prerequisites**: Exercise 01 (AWS Account & IAM), Lectures 01-02

---

## Learning Objectives

By completing this exercise, you will:
1. Launch and manage EC2 instances for ML workloads
2. Configure EC2 instance metadata and user data for automation
3. Work with EBS volumes for persistent storage
4. Create and manage S3 buckets with lifecycle policies
5. Implement S3 versioning and cross-region replication
6. Explore EC2 Spot instances for cost optimization
7. Monitor resource utilization with CloudWatch

---

## Overview

This hands-on exercise teaches you to provision and manage compute (EC2) and storage (S3, EBS) resources on AWS. You'll deploy a simple ML inference server, store models in S3, and implement cost optimization strategies.

**Real-World Scenario**: Your team needs to deploy a PyTorch image classification model. You'll provision EC2 instances, store the model in S3, and set up persistent storage for logs and predictions.

---

## Part 1: EC2 Instance Fundamentals

### Task 1.1: Launch Your First EC2 Instance

**Architecture**:
```
┌──────────────────────┐
│   Internet Gateway   │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│   Public Subnet      │
│  10.0.1.0/24         │
│  ┌────────────────┐  │
│  │  EC2 Instance  │  │
│  │  t2.micro      │  │
│  │  Public IP     │  │
│  └────────────────┘  │
└──────────────────────┘
```

**Find Latest Ubuntu AMI**:
```bash
# Search for Ubuntu 22.04 LTS AMI
aws ec2 describe-images \
  --owners 099720109477 \
  --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].{ID:ImageId,Name:Name,Date:CreationDate}' \
  --output table

# Save the AMI ID
AMI_ID="ami-0c55b159cbfafe1f0"  # Replace with output from above
```

**Create Security Group**:
```bash
# Get default VPC ID
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query 'Vpcs[0].VpcId' --output text)

# Create security group
aws ec2 create-security-group \
  --group-name ml-inference-sg \
  --description "Security group for ML inference server" \
  --vpc-id $VPC_ID

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=ml-inference-sg" --query 'SecurityGroups[0].GroupId' --output text)

# Allow SSH from your IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr ${MY_IP}/32

# Allow HTTP from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# Allow ML inference API (port 5000) from anywhere
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5000 \
  --cidr 0.0.0.0/0
```

**Create SSH Key Pair**:
```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name ml-inference-key \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/ml-inference-key.pem

# Set correct permissions
chmod 400 ~/.ssh/ml-inference-key.pem

# Verify key was created
aws ec2 describe-key-pairs --key-names ml-inference-key
```

**Launch EC2 Instance**:
```bash
# Launch instance
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name ml-inference-key \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=ml-inference-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=ml-inference-server},
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev},
    {Key=Owner,Value=alice}
  ]' \
  --block-device-mappings '[
    {
      "DeviceName": "/dev/sda1",
      "Ebs": {
        "VolumeSize": 20,
        "VolumeType": "gp3",
        "DeleteOnTermination": true
      }
    }
  ]'

# Get instance ID from output
INSTANCE_ID="i-0abc123def456789"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Get public IP address
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "Instance is running at: $PUBLIC_IP"
```

**Connect to Instance**:
```bash
# SSH into the instance
ssh -i ~/.ssh/ml-inference-key.pem ubuntu@$PUBLIC_IP

# Once connected, verify instance metadata
curl http://169.254.169.254/latest/meta-data/instance-id
curl http://169.254.169.254/latest/meta-data/instance-type
curl http://169.254.169.254/latest/meta-data/placement/availability-zone

# Check if IAM role is attached
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Exit SSH
exit
```

### Task 1.2: Install Software with User Data

**User Data Script** (runs on instance launch):

```bash
# Create user data script
cat > user-data.sh <<'EOF'
#!/bin/bash

# Update system
apt-get update -y

# Install Python and ML libraries
apt-get install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv /home/ubuntu/ml-env
source /home/ubuntu/ml-env/bin/activate

# Install ML packages
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install flask pillow requests boto3

# Create inference server
mkdir -p /home/ubuntu/ml-app

cat > /home/ubuntu/ml-app/server.py <<PYEOF
from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
from PIL import Image
import boto3
import io
import os

app = Flask(__name__)

# Load model from S3 (placeholder for now)
s3 = boto3.client('s3')
MODEL_BUCKET = os.environ.get('MODEL_BUCKET', 'ml-models-dev')
model = None

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    # Placeholder prediction
    return jsonify({
        'prediction': 'cat',
        'confidence': 0.95,
        'model_version': '1.0'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
PYEOF

# Create systemd service
cat > /etc/systemd/system/ml-inference.service <<SVCEOF
[Unit]
Description=ML Inference Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ml-app
Environment="PATH=/home/ubuntu/ml-env/bin"
ExecStart=/home/ubuntu/ml-env/bin/python3 /home/ubuntu/ml-app/server.py
Restart=always

[Install]
WantedBy=multi-user.target
SVCEOF

# Set ownership
chown -R ubuntu:ubuntu /home/ubuntu/ml-app
chown -R ubuntu:ubuntu /home/ubuntu/ml-env

# Enable and start service
systemctl daemon-reload
systemctl enable ml-inference
systemctl start ml-inference

# Log completion
echo "ML inference server setup complete" > /var/log/user-data-complete.log
EOF
```

**Launch Instance with User Data**:
```bash
# Launch new instance with user data
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --key-name ml-inference-key \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=ml-inference-ec2-profile \
  --user-data file://user-data.sh \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=ml-inference-server-v2},
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev}
  ]'

# Get new instance ID
INSTANCE_ID_V2="i-0def456abc789012"

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID_V2

# Get public IP
PUBLIC_IP_V2=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_V2 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# Wait for user data script to complete (may take 3-5 minutes)
sleep 180

# Test health endpoint
curl http://$PUBLIC_IP_V2:5000/health

# Expected output:
# {"status": "healthy", "model_loaded": false}
```

### Task 1.3: EC2 Instance Lifecycle Management

**Stop Instance** (preserves data, stops billing for compute):
```bash
aws ec2 stop-instances --instance-ids $INSTANCE_ID_V2
aws ec2 wait instance-stopped --instance-ids $INSTANCE_ID_V2

# Verify instance state
aws ec2 describe-instances --instance-ids $INSTANCE_ID_V2 \
  --query 'Reservations[0].Instances[0].State.Name'
# Output: "stopped"
```

**Start Instance**:
```bash
aws ec2 start-instances --instance-ids $INSTANCE_ID_V2
aws ec2 wait instance-running --instance-ids $INSTANCE_ID_V2

# Note: Public IP changes after stop/start (unless using Elastic IP)
PUBLIC_IP_NEW=$(aws ec2 describe-instances \
  --instance-ids $INSTANCE_ID_V2 \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "New public IP: $PUBLIC_IP_NEW"
```

**Allocate Elastic IP** (static public IP):
```bash
# Allocate Elastic IP
EIP_ALLOC_ID=$(aws ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
EIP_ADDRESS=$(aws ec2 describe-addresses --allocation-ids $EIP_ALLOC_ID --query 'Addresses[0].PublicIp' --output text)

# Associate with instance
aws ec2 associate-address \
  --instance-id $INSTANCE_ID_V2 \
  --allocation-id $EIP_ALLOC_ID

echo "Elastic IP $EIP_ADDRESS associated with instance"

# Now the IP won't change after stop/start
```

**Reboot Instance**:
```bash
aws ec2 reboot-instances --instance-ids $INSTANCE_ID_V2
```

**Terminate Instance** (deletes instance and associated resources):
```bash
# Terminate the first test instance (we'll keep v2)
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID
```

---

## Part 2: EBS (Elastic Block Store) Volumes

### Task 2.1: Create and Attach EBS Volume

**Why EBS?** Persistent block storage that survives instance termination. Use for databases, logs, checkpoints.

**Create EBS Volume**:
```bash
# Get instance availability zone
AZ=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID_V2 \
  --query 'Reservations[0].Instances[0].Placement.AvailabilityZone' \
  --output text)

# Create 50GB gp3 volume for ML training data
VOLUME_ID=$(aws ec2 create-volume \
  --availability-zone $AZ \
  --size 50 \
  --volume-type gp3 \
  --iops 3000 \
  --throughput 125 \
  --tag-specifications 'ResourceType=volume,Tags=[
    {Key=Name,Value=ml-training-data},
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev}
  ]' \
  --query 'VolumeId' \
  --output text)

echo "Created volume: $VOLUME_ID"

# Wait for volume to be available
aws ec2 wait volume-available --volume-ids $VOLUME_ID
```

**Attach Volume to Instance**:
```bash
# Attach volume
aws ec2 attach-volume \
  --volume-id $VOLUME_ID \
  --instance-id $INSTANCE_ID_V2 \
  --device /dev/sdf

# Wait for attachment
aws ec2 wait volume-in-use --volume-ids $VOLUME_ID

# Verify attachment
aws ec2 describe-volumes --volume-ids $VOLUME_ID \
  --query 'Volumes[0].Attachments[0].State'
# Output: "attached"
```

**Format and Mount Volume** (on EC2 instance):
```bash
# SSH to instance
ssh -i ~/.ssh/ml-inference-key.pem ubuntu@$EIP_ADDRESS

# Check if volume is attached
lsblk
# Output should show /dev/nvme1n1 or /dev/xvdf (unpartitioned)

# Create filesystem
sudo mkfs -t ext4 /dev/nvme1n1

# Create mount point
sudo mkdir -p /mnt/ml-data

# Mount volume
sudo mount /dev/nvme1n1 /mnt/ml-data

# Verify mount
df -h | grep ml-data

# Set ownership
sudo chown ubuntu:ubuntu /mnt/ml-data

# Create test file
echo "ML training data storage" > /mnt/ml-data/README.txt

# Make mount persistent (add to /etc/fstab)
DEVICE_UUID=$(sudo blkid /dev/nvme1n1 -s UUID -o value)
echo "UUID=$DEVICE_UUID  /mnt/ml-data  ext4  defaults,nofail  0  2" | sudo tee -a /etc/fstab

# Exit SSH
exit
```

### Task 2.2: EBS Snapshots (Backup)

**Create Snapshot**:
```bash
# Create snapshot
SNAPSHOT_ID=$(aws ec2 create-snapshot \
  --volume-id $VOLUME_ID \
  --description "Backup of ml-training-data volume" \
  --tag-specifications 'ResourceType=snapshot,Tags=[
    {Key=Name,Value=ml-training-data-backup-2025-10-23},
    {Key=Project,Value=ml-infrastructure}
  ]' \
  --query 'SnapshotId' \
  --output text)

echo "Created snapshot: $SNAPSHOT_ID"

# Wait for snapshot to complete (may take several minutes)
aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID

# Verify snapshot
aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID \
  --query 'Snapshots[0].{ID:SnapshotId,Progress:Progress,State:State}'
```

**Restore from Snapshot**:
```bash
# Create new volume from snapshot (in same or different AZ)
RESTORED_VOLUME_ID=$(aws ec2 create-volume \
  --snapshot-id $SNAPSHOT_ID \
  --availability-zone $AZ \
  --volume-type gp3 \
  --tag-specifications 'ResourceType=volume,Tags=[
    {Key=Name,Value=ml-training-data-restored}
  ]' \
  --query 'VolumeId' \
  --output text)

echo "Restored volume: $RESTORED_VOLUME_ID"
```

**Automated Snapshot Lifecycle**:
```bash
# Create lifecycle policy for automated snapshots
cat > lifecycle-policy.json <<EOF
{
  "ExecutionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/AWSDataLifecycleManagerDefaultRole",
  "Description": "Daily snapshots of ML volumes",
  "State": "ENABLED",
  "PolicyDetails": {
    "PolicyType": "EBS_SNAPSHOT_MANAGEMENT",
    "ResourceTypes": ["VOLUME"],
    "TargetTags": [
      {
        "Key": "Project",
        "Value": "ml-infrastructure"
      }
    ],
    "Schedules": [
      {
        "Name": "Daily snapshots",
        "CopyTags": true,
        "CreateRule": {
          "Interval": 24,
          "IntervalUnit": "HOURS",
          "Times": ["03:00"]
        },
        "RetainRule": {
          "Count": 7
        }
      }
    ]
  }
}
EOF

# Create DLM role first
aws iam create-role \
  --role-name AWSDataLifecycleManagerDefaultRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "dlm.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name AWSDataLifecycleManagerDefaultRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSDataLifecycleManagerServiceRole

# Wait for role propagation
sleep 10

# Create lifecycle policy
aws dlm create-lifecycle-policy --cli-input-json file://lifecycle-policy.json
```

---

## Part 3: S3 (Simple Storage Service)

### Task 3.1: Create S3 Bucket for ML Models

**Create Bucket**:
```bash
# S3 bucket names must be globally unique
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="ml-models-dev-${ACCOUNT_ID}"

# Create bucket
aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Verify bucket creation
aws s3 ls | grep ml-models
```

**Configure Bucket Encryption**:
```bash
# Enable default encryption (AES-256)
aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      },
      "BucketKeyEnabled": true
    }]
  }'

# Verify encryption
aws s3api get-bucket-encryption --bucket $BUCKET_NAME
```

**Enable Versioning**:
```bash
# Enable versioning (protects against accidental deletion)
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

# Verify versioning
aws s3api get-bucket-versioning --bucket $BUCKET_NAME
# Output: {"Status": "Enabled"}
```

**Block Public Access**:
```bash
# Block all public access (best practice for ML models)
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Verify
aws s3api get-public-access-block --bucket $BUCKET_NAME
```

### Task 3.2: Upload ML Models and Data

**Create Sample Model File**:
```bash
# Create a dummy PyTorch model file
cat > model.py <<'EOF'
import torch
import torch.nn as nn

# Simple CNN for image classification
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.fc1 = nn.Linear(64 * 56 * 56, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = torch.max_pool2d(x, 2)
        x = torch.relu(self.conv2(x))
        x = torch.max_pool2d(x, 2)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Save model
model = SimpleCNN()
torch.save(model.state_dict(), 'resnet50.pth')
print("Model saved to resnet50.pth")
EOF

# Run the script (requires PyTorch)
# python3 model.py

# For this exercise, create a dummy file
echo "Placeholder PyTorch model" > resnet50.pth
```

**Upload to S3**:
```bash
# Upload model with metadata
aws s3 cp resnet50.pth s3://$BUCKET_NAME/models/v1.0/resnet50.pth \
  --metadata model_version=1.0,framework=pytorch,accuracy=0.95 \
  --storage-class STANDARD

# Upload with server-side encryption (KMS)
# aws s3 cp resnet50.pth s3://$BUCKET_NAME/models/v1.0/resnet50.pth \
#   --server-side-encryption aws:kms \
#   --ssekms-key-id <kms-key-id>

# Verify upload
aws s3 ls s3://$BUCKET_NAME/models/v1.0/

# Get object metadata
aws s3api head-object --bucket $BUCKET_NAME --key models/v1.0/resnet50.pth
```

**Sync Directory to S3**:
```bash
# Create training data directory
mkdir -p training-data/images
echo "image1.jpg" > training-data/images/cat1.jpg
echo "image2.jpg" > training-data/images/dog1.jpg

# Sync entire directory
aws s3 sync training-data/ s3://$BUCKET_NAME/training-data/ --delete

# Verify sync
aws s3 ls s3://$BUCKET_NAME/training-data/ --recursive
```

### Task 3.3: S3 Lifecycle Policies

**Why?** Automatically transition objects to cheaper storage classes or delete old versions.

**Create Lifecycle Policy**:
```bash
cat > s3-lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "archive-old-models",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "models/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "NoncurrentVersionTransitions": [
        {
          "NoncurrentDays": 7,
          "StorageClass": "STANDARD_IA"
        },
        {
          "NoncurrentDays": 30,
          "StorageClass": "GLACIER_IR"
        }
      ],
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 180
      }
    },
    {
      "Id": "delete-old-logs",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "logs/"
      },
      "Expiration": {
        "Days": 30
      }
    },
    {
      "Id": "cleanup-incomplete-uploads",
      "Status": "Enabled",
      "Filter": {},
      "AbortIncompleteMultipartUpload": {
        "DaysAfterInitiation": 7
      }
    }
  ]
}
EOF

# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket $BUCKET_NAME \
  --lifecycle-configuration file://s3-lifecycle-policy.json

# Verify lifecycle policy
aws s3api get-bucket-lifecycle-configuration --bucket $BUCKET_NAME
```

**Storage Class Comparison**:
| Class | Cost ($/GB/month) | Retrieval Time | Use Case |
|-------|-------------------|----------------|----------|
| **Standard** | $0.023 | Instant | Active models |
| **Intelligent-Tiering** | $0.0025-0.023 | Instant | Unknown patterns |
| **Standard-IA** | $0.0125 | Instant | Models accessed < 1/month |
| **Glacier Instant Retrieval** | $0.004 | Instant | Archived models (quarterly access) |
| **Glacier Flexible Retrieval** | $0.0036 | Minutes-hours | Long-term archives |
| **Deep Archive** | $0.00099 | 12 hours | Compliance archives |

### Task 3.4: S3 Cross-Region Replication (CRR)

**Why?** Disaster recovery, compliance (data locality), lower latency for global users.

**Create Destination Bucket** (in different region):
```bash
# Create bucket in us-west-2
BUCKET_REPLICA="ml-models-replica-${ACCOUNT_ID}"
aws s3 mb s3://$BUCKET_REPLICA --region us-west-2

# Enable versioning on destination bucket (required for CRR)
aws s3api put-bucket-versioning \
  --bucket $BUCKET_REPLICA \
  --versioning-configuration Status=Enabled \
  --region us-west-2
```

**Create Replication Role**:
```bash
cat > replication-role-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "s3.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name s3-replication-role \
  --assume-role-policy-document file://replication-role-trust-policy.json

# Create replication policy
cat > replication-role-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetReplicationConfiguration",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_NAME}"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObjectVersionForReplication",
        "s3:GetObjectVersionAcl"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete"
      ],
      "Resource": "arn:aws:s3:::${BUCKET_REPLICA}/*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name s3-replication-role \
  --policy-name s3-replication-policy \
  --policy-document file://replication-role-policy.json
```

**Configure Replication**:
```bash
cat > replication-config.json <<EOF
{
  "Role": "arn:aws:iam::${ACCOUNT_ID}:role/s3-replication-role",
  "Rules": [
    {
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": {"Status": "Enabled"},
      "Filter": {"Prefix": "models/"},
      "Destination": {
        "Bucket": "arn:aws:s3:::${BUCKET_REPLICA}",
        "ReplicationTime": {
          "Status": "Enabled",
          "Time": {"Minutes": 15}
        },
        "Metrics": {
          "Status": "Enabled",
          "EventThreshold": {"Minutes": 15}
        }
      }
    }
  ]
}
EOF

# Wait for role propagation
sleep 10

# Apply replication configuration
aws s3api put-bucket-replication \
  --bucket $BUCKET_NAME \
  --replication-configuration file://replication-config.json

# Verify replication
aws s3api get-bucket-replication --bucket $BUCKET_NAME
```

**Test Replication**:
```bash
# Upload a new file
echo "test replication" > test-replication.txt
aws s3 cp test-replication.txt s3://$BUCKET_NAME/models/test-replication.txt

# Wait for replication (up to 15 minutes)
sleep 60

# Check if file exists in replica bucket
aws s3 ls s3://$BUCKET_REPLICA/models/ --region us-west-2
```

---

## Part 4: EC2 Spot Instances for Cost Optimization

### Task 4.1: Understand Spot Pricing

**Check Spot Price History**:
```bash
# Get current spot price for t2.micro in us-east-1a
aws ec2 describe-spot-price-history \
  --instance-types t2.micro \
  --product-descriptions "Linux/UNIX" \
  --availability-zone us-east-1a \
  --start-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --query 'SpotPriceHistory[0].{AZ:AvailabilityZone,Price:SpotPrice,Time:Timestamp}' \
  --output table

# Compare to On-Demand price (t2.micro = $0.0116/hour)
# Typical spot price: $0.0035/hour (70% savings)
```

### Task 4.2: Launch Spot Instance

**Create Spot Instance Request**:
```bash
# Create spot request specification
cat > spot-request.json <<EOF
{
  "ImageId": "$AMI_ID",
  "InstanceType": "t2.micro",
  "KeyName": "ml-inference-key",
  "SecurityGroupIds": ["$SG_ID"],
  "IamInstanceProfile": {"Name": "ml-inference-ec2-profile"},
  "TagSpecifications": [{
    "ResourceType": "instance",
    "Tags": [
      {"Key": "Name", "Value": "ml-training-spot"},
      {"Key": "Project", "Value": "ml-infrastructure"},
      {"Key": "Environment", "Value": "dev"}
    ]
  }]
}
EOF

# Request spot instance (with max price = on-demand price)
aws ec2 request-spot-instances \
  --spot-price "0.0116" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification file://spot-request.json

# Get spot request ID from output
SPOT_REQUEST_ID="sir-abc123"

# Check spot request status
aws ec2 describe-spot-instance-requests \
  --spot-instance-request-ids $SPOT_REQUEST_ID

# Get instance ID once fulfilled
SPOT_INSTANCE_ID=$(aws ec2 describe-spot-instance-requests \
  --spot-instance-request-ids $SPOT_REQUEST_ID \
  --query 'SpotInstanceRequests[0].InstanceId' \
  --output text)

echo "Spot instance: $SPOT_INSTANCE_ID"
```

**Handle Spot Interruptions** (2-minute warning):

On the instance, create an interruption handler:
```bash
# SSH to spot instance
ssh -i ~/.ssh/ml-inference-key.pem ubuntu@<spot-instance-ip>

# Create interruption monitoring script
cat > /home/ubuntu/spot-monitor.sh <<'EOF'
#!/bin/bash

while true; do
  # Check for spot interruption notice
  RESPONSE=$(curl -s http://169.254.169.254/latest/meta-data/spot/instance-action)

  if [ "$RESPONSE" != "404 - Not Found" ]; then
    echo "$(date): Spot interruption detected: $RESPONSE"

    # Save checkpoint to S3
    aws s3 sync /mnt/ml-data/checkpoints/ s3://ml-training-checkpoints/

    # Gracefully shutdown application
    systemctl stop ml-inference

    exit 0
  fi

  sleep 5
done
EOF

chmod +x /home/ubuntu/spot-monitor.sh

# Run as background service (in production, use systemd)
nohup /home/ubuntu/spot-monitor.sh > /var/log/spot-monitor.log 2>&1 &
```

### Task 4.3: Spot Fleet (Advanced)

**Create Spot Fleet** (multiple instance types for better availability):
```bash
cat > spot-fleet-config.json <<EOF
{
  "IamFleetRole": "arn:aws:iam::${ACCOUNT_ID}:role/aws-ec2-spot-fleet-tagging-role",
  "AllocationStrategy": "lowestPrice",
  "TargetCapacity": 2,
  "SpotPrice": "0.05",
  "LaunchSpecifications": [
    {
      "ImageId": "$AMI_ID",
      "InstanceType": "t2.small",
      "KeyName": "ml-inference-key",
      "SecurityGroups": [{"GroupId": "$SG_ID"}],
      "IamInstanceProfile": {"Arn": "arn:aws:iam::${ACCOUNT_ID}:instance-profile/ml-inference-ec2-profile"}
    },
    {
      "ImageId": "$AMI_ID",
      "InstanceType": "t3.small",
      "KeyName": "ml-inference-key",
      "SecurityGroups": [{"GroupId": "$SG_ID"}],
      "IamInstanceProfile": {"Arn": "arn:aws:iam::${ACCOUNT_ID}:instance-profile/ml-inference-ec2-profile"}
    }
  ]
}
EOF

# Note: Spot fleet requires IAM role creation (complex, skip for beginner)
# aws ec2 request-spot-fleet --spot-fleet-request-config file://spot-fleet-config.json
```

---

## Part 5: CloudWatch Monitoring

### Task 5.1: Monitor EC2 Metrics

**View Built-in Metrics**:
```bash
# Get CPU utilization for last hour
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID_V2 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --query 'Datapoints | sort_by(@, &Timestamp)[-5:]' \
  --output table

# Get network in (bytes)
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name NetworkIn \
  --dimensions Name=InstanceId,Value=$INSTANCE_ID_V2 \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Task 5.2: Create CloudWatch Dashboard

**Create Dashboard**:
```bash
cat > dashboard-config.json <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "CPUUtilization", {"stat": "Average", "label": "CPU %"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "EC2 CPU Utilization"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/EC2", "NetworkIn", {"stat": "Sum"}],
          [".", "NetworkOut", {"stat": "Sum"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "EC2 Network Traffic"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name ml-infrastructure-dashboard \
  --dashboard-body file://dashboard-config.json
```

**View Dashboard**:
```bash
# Get dashboard URL
echo "https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=ml-infrastructure-dashboard"
```

---

## Part 6: Validation and Cost Analysis

### Task 6.1: Validate All Resources

**Check Resource Inventory**:
```bash
# List all EC2 instances
aws ec2 describe-instances \
  --filters "Name=tag:Project,Values=ml-infrastructure" \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,State.Name,PublicIpAddress,Tags[?Key==`Name`].Value|[0]]' \
  --output table

# List all EBS volumes
aws ec2 describe-volumes \
  --filters "Name=tag:Project,Values=ml-infrastructure" \
  --query 'Volumes[].[VolumeId,Size,VolumeType,State,Attachments[0].InstanceId]' \
  --output table

# List all S3 buckets
aws s3 ls | grep ml-

# Get S3 bucket size
aws s3 ls s3://$BUCKET_NAME --recursive --summarize | tail -2
```

### Task 6.2: Estimate Monthly Costs

**Calculate Estimated Costs**:
```bash
cat > cost-estimate.sh <<'EOF'
#!/bin/bash

echo "=== Monthly Cost Estimate ==="
echo ""

# EC2 Costs
echo "EC2 (1x t2.micro, 100% uptime):"
echo "  $0.0116/hour × 730 hours = $8.47/month"
echo ""

# EBS Costs
echo "EBS (50GB gp3):"
echo "  $0.08/GB × 50GB = $4.00/month"
echo "  IOPS (3000) included"
echo "  Throughput (125 MB/s) included"
echo ""

# S3 Costs (assuming 10GB storage, 1000 requests/month)
echo "S3 Standard (10GB):"
echo "  Storage: $0.023/GB × 10GB = $0.23/month"
echo "  PUT requests: $0.005/1000 × 1 = $0.005/month"
echo "  GET requests: $0.0004/1000 × 1 = $0.0004/month"
echo "  Total S3: ~$0.24/month"
echo ""

# Data Transfer (assuming 10GB out/month)
echo "Data Transfer:"
echo "  First 1GB free, then $0.09/GB"
echo "  10GB - 1GB = 9GB × $0.09 = $0.81/month"
echo ""

# Total
echo "=== TOTAL ESTIMATED COST ==="
echo "EC2:           $8.47"
echo "EBS:           $4.00"
echo "S3:            $0.24"
echo "Data Transfer: $0.81"
echo "------------------------"
echo "TOTAL:        $13.52/month"
echo ""
echo "With Spot Instances (70% savings on EC2):"
echo "  EC2 Spot:      $2.54"
echo "  Other:        $5.05"
echo "  TOTAL:        $7.59/month (44% savings)"
EOF

chmod +x cost-estimate.sh
./cost-estimate.sh
```

---

## Cleanup

**Terminate Resources** (to avoid charges):
```bash
# Terminate EC2 instances
aws ec2 terminate-instances --instance-ids $INSTANCE_ID_V2 $SPOT_INSTANCE_ID

# Release Elastic IP
aws ec2 release-address --allocation-id $EIP_ALLOC_ID

# Delete EBS volumes (wait for instances to terminate first)
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID_V2
aws ec2 delete-volume --volume-id $VOLUME_ID
aws ec2 delete-volume --volume-id $RESTORED_VOLUME_ID

# Delete EBS snapshots
aws ec2 delete-snapshot --snapshot-id $SNAPSHOT_ID

# Delete S3 buckets (must be empty first)
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME

aws s3 rm s3://$BUCKET_REPLICA --recursive --region us-west-2
aws s3 rb s3://$BUCKET_REPLICA --region us-west-2

# Delete security group
aws ec2 delete-security-group --group-id $SG_ID

# Delete key pair
aws ec2 delete-key-pair --key-name ml-inference-key
rm ~/.ssh/ml-inference-key.pem
```

---

## Deliverables

By the end of this exercise, you should have:

1. ✅ Launched EC2 instances with user data automation
2. ✅ Created and attached EBS volumes
3. ✅ Implemented EBS snapshot backups
4. ✅ Created S3 buckets with encryption and versioning
5. ✅ Configured S3 lifecycle policies
6. ✅ Set up cross-region replication
7. ✅ Launched Spot instances for cost savings
8. ✅ Monitored resources with CloudWatch
9. ✅ Calculated cost estimates

**Evidence**:
- Screenshots of running EC2 instances
- S3 bucket list showing models and training data
- CloudWatch dashboard showing metrics
- Cost estimate output

---

## Next Steps

Now that you can provision compute and storage, you're ready for:
- **Exercise 03**: Build production VPC with multi-tier networking
- **Exercise 04**: Deploy containerized ML service with ECS/EKS
- **Exercise 05**: SageMaker training and cost optimization

Great work! You now have hands-on experience with AWS core services.
