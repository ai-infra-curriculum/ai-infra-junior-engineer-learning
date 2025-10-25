# Exercise 01: AWS Account Setup & IAM Best Practices

**Module**: Cloud Platforms
**Difficulty**: Beginner
**Estimated Time**: 2-3 hours
**Prerequisites**: Lectures 01-04

---

## Learning Objectives

By completing this exercise, you will:
1. Set up an AWS account with proper security configuration
2. Configure the AWS CLI with credentials and profiles
3. Create IAM users, groups, and roles following least privilege
4. Implement Multi-Factor Authentication (MFA) for enhanced security
5. Create a tagging strategy for cost allocation and governance
6. Establish billing alerts and budgets

---

## Overview

This foundational exercise sets up your AWS environment with security best practices. You'll learn to manage IAM identities, configure the AWS CLI, and implement cost controls - skills that are essential for all AWS work.

**Real-World Scenario**: You're a junior AI infrastructure engineer joining a new team. Your first task is to set up a secure AWS account for developing ML infrastructure, following your company's security policies.

---

## Part 1: AWS Account Setup & Security Hardening

### Task 1.1: Create AWS Account (If Needed)

**If you don't have an AWS account**:

1. Go to https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow the registration process:
   - Email address (use your personal or work email)
   - Account name: `ml-infrastructure-dev`
   - Root user password (use a strong password with 16+ characters)
   - Contact information
   - Payment method (credit card required)
   - Identity verification (phone)
   - Select "Free Tier" support plan

**Important**: The root user has unlimited access. You'll secure this account and create limited-privilege users.

### Task 1.2: Secure the Root Account

**Why?** The root account can do ANYTHING in your AWS account (delete all resources, change billing, close account). It must be secured.

**Steps**:

1. **Enable MFA for Root User**:
   - Sign in to AWS Console as root user
   - Click your account name (top right) → "Security credentials"
   - In "Multi-factor authentication (MFA)" section, click "Assign MFA device"
   - Choose "Virtual MFA device"
   - Use an authenticator app (Google Authenticator, Authy, 1Password):
     - Scan the QR code
     - Enter two consecutive MFA codes
     - Click "Assign MFA"

2. **Create a Strong Password**:
   - Go to "Security credentials" → "Password"
   - Change password to a unique, strong password (16+ characters, mixed case, numbers, symbols)
   - Store password in a password manager (1Password, LastPass, Bitwarden)

3. **Delete Root Access Keys** (if any exist):
   - In "Security credentials", check "Access keys" section
   - If any keys exist, delete them
   - **Never** create access keys for root user

**Verification**:
```bash
# Try to sign in again - you should be prompted for MFA
# This confirms MFA is working
```

### Task 1.3: Enable CloudTrail (Audit Logging)

**Why?** CloudTrail logs all API calls in your account. Essential for security audits, compliance, and troubleshooting.

**Steps**:

1. Open CloudTrail console: https://console.aws.amazon.com/cloudtrail/
2. Click "Create trail"
3. Configure trail:
   - Trail name: `ml-infrastructure-audit-trail`
   - Storage location: Create new S3 bucket
   - Bucket name: `ml-infrastructure-audit-logs-<your-account-id>`
   - Log file SSE-KMS encryption: Enabled (creates new KMS key)
   - Log file validation: Enabled
   - SNS notification delivery: Disabled (for now)
4. Choose log events:
   - Management events: ✅ Read and Write
   - Data events: ❌ (not needed for this exercise)
   - Insights events: ❌ (adds cost)
5. Click "Create trail"

**Verification**:
```bash
# Install AWS CLI first (see Task 2.1)
aws cloudtrail describe-trails

# Expected output:
# {
#   "trailList": [
#     {
#       "Name": "ml-infrastructure-audit-trail",
#       "S3BucketName": "ml-infrastructure-audit-logs-...",
#       ...
#     }
#   ]
# }
```

### Task 1.4: Enable AWS GuardDuty (Threat Detection)

**Why?** GuardDuty uses machine learning to detect suspicious activity (compromised credentials, crypto mining, unauthorized access).

**Steps**:

1. Open GuardDuty console: https://console.aws.amazon.com/guardduty/
2. Click "Get Started"
3. Click "Enable GuardDuty"
4. GuardDuty will start monitoring immediately (30-day free trial, then ~$4/month for typical dev usage)

**Verification**:
```bash
aws guardduty list-detectors

# Expected output:
# {
#   "DetectorIds": [
#     "abc123def456ghi789..."
#   ]
# }
```

---

## Part 2: AWS CLI Configuration

### Task 2.1: Install AWS CLI v2

**Ubuntu/Debian**:
```bash
# Download AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Install unzip if not already installed
sudo apt-get update && sudo apt-get install -y unzip

# Unzip the installer
unzip awscliv2.zip

# Run the installer
sudo ./aws/install

# Verify installation
aws --version
# Expected: aws-cli/2.x.x Python/3.x.x Linux/...

# Clean up
rm -rf aws awscliv2.zip
```

**macOS**:
```bash
# Download and install
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify
aws --version
```

**Windows** (PowerShell):
```powershell
# Download installer
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify (restart terminal first)
aws --version
```

### Task 2.2: Create IAM Administrator User

**Why?** Never use root credentials for daily work. Create an IAM user with admin permissions.

**Steps via Console**:

1. Open IAM console: https://console.aws.amazon.com/iam/
2. Navigate to "Users" → "Create user"
3. User details:
   - User name: `ml-admin`
   - Select "Provide user access to the AWS Management Console"
   - Console password: Custom password (or auto-generated)
   - ✅ Users must create a new password at next sign-in
4. Click "Next"
5. Permissions:
   - Select "Attach policies directly"
   - Search for and select: `AdministratorAccess`
   - Click "Next"
6. Review and create user
7. **IMPORTANT**: Save the console sign-in URL and initial password

### Task 2.3: Create Access Keys for CLI

**Steps**:

1. In IAM console, click on the `ml-admin` user
2. Go to "Security credentials" tab
3. Scroll to "Access keys" section → Click "Create access key"
4. Select use case: "Command Line Interface (CLI)"
5. Check "I understand the above recommendation..."
6. Click "Next"
7. Description tag: `CLI access for ML infrastructure development`
8. Click "Create access key"
9. **CRITICAL**: Download the CSV file or copy the credentials:
   - Access key ID: `AKIAIOSFODNN7EXAMPLE`
   - Secret access key: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
10. Store these in a password manager - you won't see the secret key again!

### Task 2.4: Configure AWS CLI with Profiles

**Configure Default Profile**:
```bash
# Configure the default profile
aws configure

# You'll be prompted:
AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Default region name [None]: us-east-1
Default output format [None]: json
```

**Configure Additional Profiles**:
```bash
# Configure a "dev" profile
aws configure --profile dev
# Enter the same credentials, or different ones for a dev account

# Configure a "prod" profile (if you have multiple accounts)
aws configure --profile prod
```

**Verify Configuration**:
```bash
# List configured profiles
cat ~/.aws/config

# Expected output:
# [default]
# region = us-east-1
# output = json
#
# [profile dev]
# region = us-east-1
# output = json

# Test the configuration
aws sts get-caller-identity

# Expected output:
# {
#   "UserId": "AIDAI...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/ml-admin"
# }

# Test with a specific profile
aws sts get-caller-identity --profile dev
```

**Set Environment Variables** (optional, for convenience):
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export AWS_PROFILE=dev' >> ~/.bashrc
echo 'export AWS_DEFAULT_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $AWS_PROFILE
# Expected: dev
```

---

## Part 3: IAM Users, Groups, and Roles

### Task 3.1: Create IAM Groups with Policies

**Why?** Groups allow you to manage permissions for multiple users at once. Instead of attaching policies to individual users, attach them to groups.

**Group Design**:
```
ml-admins         → AdministratorAccess
ml-developers     → EC2, S3, RDS, SageMaker (read/write)
ml-data-scientists → SageMaker, S3 (read-only EC2)
ml-readonly       → ViewOnlyAccess
```

**Create Groups via CLI**:

```bash
# Create ml-developers group
aws iam create-group --group-name ml-developers

# Attach policies to ml-developers
aws iam attach-group-policy \
  --group-name ml-developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

aws iam attach-group-policy \
  --group-name ml-developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-group-policy \
  --group-name ml-developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonRDSFullAccess

aws iam attach-group-policy \
  --group-name ml-developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

# Create ml-data-scientists group
aws iam create-group --group-name ml-data-scientists

aws iam attach-group-policy \
  --group-name ml-data-scientists \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-group-policy \
  --group-name ml-data-scientists \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-group-policy \
  --group-name ml-data-scientists \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess

# Create ml-readonly group
aws iam create-group --group-name ml-readonly

aws iam attach-group-policy \
  --group-name ml-readonly \
  --policy-arn arn:aws:iam::aws:policy/ViewOnlyAccess
```

**Verification**:
```bash
# List all groups
aws iam list-groups

# Get policies attached to a group
aws iam list-attached-group-policies --group-name ml-developers
```

### Task 3.2: Create IAM Users and Assign to Groups

**Create Users**:

```bash
# Create a developer user
aws iam create-user --user-name alice-developer

# Add user to ml-developers group
aws iam add-user-to-group \
  --user-name alice-developer \
  --group-name ml-developers

# Create console login profile for Alice
aws iam create-login-profile \
  --user-name alice-developer \
  --password "TempPassword123!" \
  --password-reset-required

# Create a data scientist user
aws iam create-user --user-name bob-data-scientist

aws iam add-user-to-group \
  --user-name bob-data-scientist \
  --group-name ml-data-scientists

aws iam create-login-profile \
  --user-name bob-data-scientist \
  --password "TempPassword456!" \
  --password-reset-required

# Create a read-only user
aws iam create-user --user-name charlie-readonly

aws iam add-user-to-group \
  --user-name charlie-readonly \
  --group-name ml-readonly

aws iam create-login-profile \
  --user-name charlie-readonly \
  --password "TempPassword789!" \
  --password-reset-required
```

**Verification**:
```bash
# List all users
aws iam list-users

# Get groups for a specific user
aws iam list-groups-for-user --user-name alice-developer

# Get effective permissions for a user
aws iam list-attached-user-policies --user-name alice-developer
aws iam list-groups-for-user --user-name alice-developer
```

### Task 3.3: Create IAM Roles for EC2

**Why?** Roles allow EC2 instances to access AWS services without embedding credentials in code.

**Create EC2 Role for ML Inference**:

```bash
# Create trust policy (allows EC2 to assume this role)
cat > ec2-trust-policy.json <<EOF
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

# Create the role
aws iam create-role \
  --role-name ml-inference-ec2-role \
  --assume-role-policy-document file://ec2-trust-policy.json \
  --description "Role for EC2 instances running ML inference"

# Attach policies to the role
aws iam attach-role-policy \
  --role-name ml-inference-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

aws iam attach-role-policy \
  --role-name ml-inference-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy

# Create custom policy for writing inference logs to S3
cat > inference-logs-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::ml-inference-logs-*/*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name ml-inference-logs-write \
  --policy-document file://inference-logs-policy.json

# Get the policy ARN from the output above, then attach it
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws iam attach-role-policy \
  --role-name ml-inference-ec2-role \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/ml-inference-logs-write

# Create instance profile (required to attach role to EC2)
aws iam create-instance-profile \
  --instance-profile-name ml-inference-ec2-profile

aws iam add-role-to-instance-profile \
  --instance-profile-name ml-inference-ec2-profile \
  --role-name ml-inference-ec2-role
```

**Verification**:
```bash
# List roles
aws iam list-roles | grep ml-inference

# Get role details
aws iam get-role --role-name ml-inference-ec2-role

# List policies attached to role
aws iam list-attached-role-policies --role-name ml-inference-ec2-role
```

### Task 3.4: Create Custom IAM Policy (Least Privilege)

**Scenario**: Create a policy that allows data scientists to use SageMaker but restricts instance types to cost-effective options.

**Create Custom Policy**:

```bash
cat > sagemaker-restricted-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "SageMakerAllowedActions",
      "Effect": "Allow",
      "Action": [
        "sagemaker:CreateTrainingJob",
        "sagemaker:CreateNotebookInstance",
        "sagemaker:DescribeTrainingJob",
        "sagemaker:DescribeNotebookInstance",
        "sagemaker:StopTrainingJob",
        "sagemaker:StopNotebookInstance"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "sagemaker:InstanceTypes": [
            "ml.t3.medium",
            "ml.t3.large",
            "ml.m5.large",
            "ml.m5.xlarge"
          ]
        }
      }
    },
    {
      "Sid": "S3AccessForSageMaker",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::ml-training-data-*",
        "arn:aws:s3:::ml-training-data-*/*"
      ]
    },
    {
      "Sid": "DenyExpensiveInstances",
      "Effect": "Deny",
      "Action": [
        "sagemaker:CreateTrainingJob",
        "sagemaker:CreateNotebookInstance"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "sagemaker:InstanceTypes": [
            "ml.p3.8xlarge",
            "ml.p3.16xlarge",
            "ml.p4d.24xlarge"
          ]
        }
      }
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name sagemaker-cost-optimized-access \
  --policy-document file://sagemaker-restricted-policy.json \
  --description "Allows SageMaker usage but restricts expensive instance types"

# Attach to ml-data-scientists group
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws iam attach-group-policy \
  --group-name ml-data-scientists \
  --policy-arn arn:aws:iam::$ACCOUNT_ID:policy/sagemaker-cost-optimized-access
```

**Verification**:
```bash
# Test as bob-data-scientist (requires bob's credentials)
# This should succeed:
aws sagemaker create-notebook-instance \
  --notebook-instance-name test-notebook \
  --instance-type ml.t3.medium \
  --role-arn <role-arn>

# This should fail:
aws sagemaker create-notebook-instance \
  --notebook-instance-name test-notebook-expensive \
  --instance-type ml.p3.8xlarge \
  --role-arn <role-arn>
# Expected error: User is not authorized to perform sagemaker:CreateNotebookInstance
```

---

## Part 4: Tagging Strategy for Cost Allocation

### Task 4.1: Define Tagging Standards

**Why?** Tags allow you to track costs by project, environment, team, and owner. Essential for cost optimization.

**Tagging Standards**:
```
Required Tags (all resources):
  - Project      : ml-infrastructure | data-pipeline | model-training
  - Environment  : dev | staging | prod
  - Owner        : alice | bob | team-ml
  - CostCenter   : engineering | data-science | research

Optional Tags:
  - Name         : Human-readable resource name
  - ManagedBy    : terraform | cloudformation | manual
  - Version      : v1.0, v2.0, etc.
  - Compliance   : hipaa | gdpr | sox
```

**Create Tagging Policy** (AWS Organizations required):

```bash
# If you have AWS Organizations enabled:
cat > tagging-policy.json <<EOF
{
  "tags": {
    "Project": {
      "tag_key": {
        "@@assign": "Project"
      },
      "tag_value": {
        "@@assign": ["ml-infrastructure", "data-pipeline", "model-training"]
      },
      "enforced_for": {
        "@@assign": ["ec2:instance", "s3:bucket", "rds:db", "sagemaker:*"]
      }
    },
    "Environment": {
      "tag_key": {
        "@@assign": "Environment"
      },
      "tag_value": {
        "@@assign": ["dev", "staging", "prod"]
      },
      "enforced_for": {
        "@@assign": ["ec2:instance", "s3:bucket", "rds:db"]
      }
    }
  }
}
EOF

# Enable tagging policy (requires AWS Organizations)
# aws organizations enable-policy-type --root-id <root-id> --policy-type TAG_POLICY
# aws organizations create-policy --name ml-tagging-policy --type TAG_POLICY --content file://tagging-policy.json
```

### Task 4.2: Apply Tags to Resources

**Tag Existing Resources**:

```bash
# Tag S3 buckets
aws s3api put-bucket-tagging \
  --bucket ml-models-bucket \
  --tagging 'TagSet=[
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev},
    {Key=Owner,Value=alice},
    {Key=CostCenter,Value=engineering}
  ]'

# Tag EC2 instances
INSTANCE_ID="i-0abc123def456"
aws ec2 create-tags \
  --resources $INSTANCE_ID \
  --tags \
    Key=Project,Value=ml-infrastructure \
    Key=Environment,Value=dev \
    Key=Owner,Value=alice \
    Key=CostCenter,Value=engineering \
    Key=Name,Value=ml-inference-server

# Tag with AWS CLI (generic)
aws resourcegroupstaggingapi tag-resources \
  --resource-arn-list arn:aws:s3:::my-bucket \
  --tags Project=ml-infrastructure,Environment=dev
```

**Query Resources by Tags**:

```bash
# Find all dev resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Environment,Values=dev

# Find all resources owned by alice
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Owner,Values=alice

# Find ml-infrastructure project resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=ml-infrastructure
```

---

## Part 5: Billing Alerts and Cost Budgets

### Task 5.1: Enable Billing Alerts

**Steps**:

1. Open Billing console: https://console.aws.amazon.com/billing/
2. Go to "Billing Preferences"
3. Enable:
   - ✅ Receive PDF Invoice By Email
   - ✅ Receive Free Tier Usage Alerts
   - ✅ Receive Billing Alerts
4. Enter email address for alerts
5. Click "Save preferences"

### Task 5.2: Create CloudWatch Billing Alarm

**Create SNS Topic for Alerts**:

```bash
# Create SNS topic
aws sns create-topic --name billing-alerts

# Subscribe email to topic
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456789012:billing-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription via email (check your inbox)
```

**Create CloudWatch Alarm** (must be in us-east-1):

```bash
# Switch to us-east-1 region (billing metrics only available here)
aws cloudwatch put-metric-alarm \
  --alarm-name billing-alarm-50usd \
  --alarm-description "Alert when estimated charges exceed $50" \
  --metric-name EstimatedCharges \
  --namespace AWS/Billing \
  --statistic Maximum \
  --period 21600 \
  --evaluation-periods 1 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=Currency,Value=USD \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:billing-alerts \
  --region us-east-1
```

**Verification**:
```bash
aws cloudwatch describe-alarms --alarm-names billing-alarm-50usd --region us-east-1
```

### Task 5.3: Create AWS Budget

**Create Monthly Budget** ($100 limit):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > budget.json <<EOF
{
  "BudgetName": "ml-infrastructure-monthly-budget",
  "BudgetLimit": {
    "Amount": "100",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:Project\$ml-infrastructure"]
  }
}
EOF

cat > notifications.json <<EOF
[
  {
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  },
  {
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 100,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [
      {
        "SubscriptionType": "EMAIL",
        "Address": "your-email@example.com"
      }
    ]
  }
]
EOF

aws budgets create-budget \
  --account-id $ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

**Verification**:
```bash
aws budgets describe-budgets --account-id $ACCOUNT_ID
```

---

## Part 6: IAM Best Practices Checklist

### Task 6.1: Security Audit

**Run IAM Security Audit**:

```bash
# Check for users without MFA
aws iam get-credential-report || aws iam generate-credential-report
sleep 5  # Wait for report generation
aws iam get-credential-report --output text | \
  awk -F',' '$4 == "false" && $1 != "<root_account>" {print "User without MFA:", $1}'

# Check for unused access keys (> 90 days)
aws iam get-credential-report --output text | \
  awk -F',' -v today=$(date +%s) '
    NR > 1 {
      if ($11 != "N/A" && $11 != "no_information") {
        cmd = "date -d " $11 " +%s"
        cmd | getline key_date
        close(cmd)
        if ((today - key_date) > 7776000) {  # 90 days in seconds
          print "Unused access key (>90 days):", $1, "Last used:", $11
        }
      }
    }
  '

# Check for overly permissive policies
aws iam list-policies --scope Local --query 'Policies[?PolicyName==`AdminAccess`]'

# Check for root account usage (should be zero)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=root \
  --max-results 10 \
  --query 'Events[].{Time:EventTime,Event:EventName}'
```

### Task 6.2: Implement IAM Best Practices

**Checklist**:

- [ ] **Root Account**:
  - [ ] MFA enabled on root account
  - [ ] No access keys for root account
  - [ ] Strong password (16+ characters)
  - [ ] Root account only used for billing/account closure

- [ ] **IAM Users**:
  - [ ] All users have MFA enabled
  - [ ] Users assigned to groups (not individual policies)
  - [ ] Access keys rotated every 90 days
  - [ ] Inactive users disabled or deleted

- [ ] **IAM Roles**:
  - [ ] EC2 instances use roles (not embedded credentials)
  - [ ] Least privilege principle applied
  - [ ] Trust policies reviewed regularly

- [ ] **Policies**:
  - [ ] No policies with `"Effect": "Allow", "Action": "*", "Resource": "*"`
  - [ ] Condition blocks used where appropriate
  - [ ] Custom policies follow least privilege

- [ ] **Monitoring**:
  - [ ] CloudTrail enabled in all regions
  - [ ] GuardDuty enabled
  - [ ] Billing alerts configured
  - [ ] Budgets created

**Generate IAM Best Practices Report**:

```bash
cat > iam-audit.sh <<'EOF'
#!/bin/bash

echo "=== IAM Security Audit ==="
echo ""

# Check root account MFA
echo "1. Root Account MFA Status:"
aws iam get-account-summary | grep AccountMFAEnabled

# Check number of users
echo ""
echo "2. Total IAM Users:"
aws iam list-users --query 'Users | length(@)'

# Check users without MFA
echo ""
echo "3. Users Without MFA:"
aws iam get-credential-report --output text | \
  awk -F',' '$4 == "false" && $1 != "<root_account>" {print $1}'

# Check CloudTrail status
echo ""
echo "4. CloudTrail Status:"
aws cloudtrail describe-trails --query 'trailList[].{Name:Name,Status:IsMultiRegionTrail}'

# Check GuardDuty status
echo ""
echo "5. GuardDuty Detectors:"
aws guardduty list-detectors

echo ""
echo "=== Audit Complete ==="
EOF

chmod +x iam-audit.sh
./iam-audit.sh
```

---

## Part 7: Validation and Testing

### Task 7.1: Validate IAM Configuration

**Test User Permissions**:

```bash
# Test alice-developer (should have EC2 access)
aws ec2 describe-instances --profile alice-dev
# Should succeed

# Test alice-developer trying to delete IAM users (should fail)
aws iam delete-user --user-name test-user --profile alice-dev
# Expected error: User alice-developer is not authorized to perform iam:DeleteUser

# Test bob-data-scientist (should have SageMaker access but limited instance types)
aws sagemaker list-notebook-instances --profile bob-ds
# Should succeed

# Test charlie-readonly (should only have read access)
aws s3 ls --profile charlie-ro
# Should succeed

aws s3 rm s3://my-bucket/test.txt --profile charlie-ro
# Expected error: Access Denied
```

### Task 7.2: Test IAM Role

**Launch EC2 Instance with IAM Role**:

```bash
# Find latest Amazon Linux 2 AMI
AMI_ID=$(aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn2-ami-hvm-*-x86_64-gp2" \
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
  --output text)

# Launch instance with IAM role
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type t2.micro \
  --iam-instance-profile Name=ml-inference-ec2-profile \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=iam-role-test},
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev}
  ]'

# Get instance ID from output
INSTANCE_ID="i-0abc123..."

# Wait for instance to be running
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

# Connect to instance (requires SSH key setup)
# Once connected, test role permissions:
# $ aws s3 ls  # Should work (S3 read-only)
# $ aws s3 mb s3://test-bucket  # Should fail (no write permission)
```

### Task 7.3: Validate Cost Alerts

**Simulate Cost Alert** (optional, costs money):

```bash
# Launch a larger instance to trigger billing alert
# WARNING: This will incur costs (~$0.10/hour)
aws ec2 run-instances \
  --image-id $AMI_ID \
  --instance-type m5.large \
  --tag-specifications 'ResourceType=instance,Tags=[
    {Key=Name,Value=billing-test},
    {Key=Project,Value=ml-infrastructure}
  ]'

# Check billing alarm after a few hours
aws cloudwatch describe-alarms --alarm-names billing-alarm-50usd --region us-east-1

# IMPORTANT: Terminate the instance when done testing
aws ec2 terminate-instances --instance-ids <instance-id>
```

---

## Challenge Tasks (Optional)

### Challenge 1: Implement Password Policy

Create a strong password policy for IAM users:

```bash
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5 \
  --hard-expiry
```

### Challenge 2: Create Service Control Policy (SCP)

If you have AWS Organizations, create an SCP to prevent users from disabling CloudTrail:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail"
      ],
      "Resource": "*"
    }
  ]
}
```

### Challenge 3: Implement Cross-Account Access

Create a role that allows users from another AWS account to access specific resources (useful for multi-account setups).

---

## Deliverables

By the end of this exercise, you should have:

1. ✅ Secured AWS root account with MFA
2. ✅ AWS CLI installed and configured with profiles
3. ✅ Created IAM users, groups, and roles following least privilege
4. ✅ Implemented custom IAM policies
5. ✅ Defined and applied tagging standards
6. ✅ Configured billing alerts and budgets
7. ✅ Enabled CloudTrail and GuardDuty
8. ✅ Generated IAM security audit report

**Evidence**:
- Screenshots of IAM dashboard showing users and groups
- Output of `aws iam get-account-summary`
- Output of `aws budgets describe-budgets --account-id <account-id>`
- IAM audit script results

---

## Troubleshooting

**Issue**: `aws` command not found after installation

**Solution**:
```bash
# Check if AWS CLI is in PATH
which aws

# If not, add to PATH (Ubuntu/Debian)
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc
```

**Issue**: Access denied when running AWS CLI commands

**Solution**:
```bash
# Verify credentials are configured
aws configure list

# Check if credentials are valid
aws sts get-caller-identity

# If using profiles, specify profile explicitly
aws s3 ls --profile dev
```

**Issue**: Billing alarm not triggering

**Solution**:
- Billing metrics take 6-8 hours to update
- Ensure alarm is created in **us-east-1** region
- Verify SNS topic subscription is confirmed (check email)
- Check alarm state: `aws cloudwatch describe-alarms --region us-east-1`

---

## Next Steps

Now that your AWS account is properly configured, you're ready for:
- **Exercise 02**: Provision compute (EC2) and storage (S3, EBS)
- **Exercise 03**: Build production VPC with Terraform
- **Exercise 04**: Deploy containerized ML application with ECS/EKS
- **Exercise 05**: SageMaker training and cost optimization

**Keep your IAM credentials secure** - never commit them to Git or share them!
