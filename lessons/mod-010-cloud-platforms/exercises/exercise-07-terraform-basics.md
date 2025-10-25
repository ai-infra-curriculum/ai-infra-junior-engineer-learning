# Exercise 07: Infrastructure as Code with Terraform Basics

**Difficulty**: Beginner
**Duration**: 3-4 hours
**Prerequisites**: AWS account with CLI configured, basic cloud concepts

## Learning Objectives

By the end of this exercise, you will:

1. Understand what Infrastructure as Code (IaC) is and why it's important
2. Install and configure Terraform
3. Write basic Terraform configuration files
4. Create cloud resources using Terraform
5. Modify and destroy infrastructure with Terraform
6. Understand Terraform state and best practices
7. Use variables and outputs in Terraform

## What You'll Build

Using Terraform, you'll create:
- An AWS S3 bucket for storing ML datasets
- An EC2 instance for ML workloads
- Security groups for network access control
- IAM roles and policies
- A simple ML infrastructure stack

All defined in code that can be versioned, reviewed, and reused!

## Background: Why Infrastructure as Code?

### The Problem: Manual Infrastructure Management

**Before IaC (the old way)**:
```
1. Log into AWS Console
2. Click through 20+ screens to create EC2 instance
3. Manually configure security groups
4. Set up networking
5. Create storage
6. Document what you did (maybe)
7. Repeat for dev, staging, prod environments
8. Hope you clicked the same buttons each time
```

**Problems**:
- ❌ Not reproducible
- ❌ Error-prone (typos, forgotten steps)
- ❌ No version control
- ❌ Hard to review changes
- ❌ Difficult to clone environments
- ❌ No audit trail

### The Solution: Infrastructure as Code

**With IaC**:
```hcl
# infrastructure.tf
resource "aws_instance" "ml_server" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.large"

  tags = {
    Name = "ML Training Server"
  }
}
```

**Benefits**:
- ✅ Reproducible (run same code → get same infrastructure)
- ✅ Version controlled (Git tracks all changes)
- ✅ Reviewable (pull requests for infrastructure)
- ✅ Auditable (who changed what when)
- ✅ Testable (validate before applying)
- ✅ Documented (code is documentation)

### Why Terraform?

**Terraform** (by HashiCorp) is the most popular IaC tool:
- **Multi-cloud**: Works with AWS, GCP, Azure, 100+ providers
- **Declarative**: Describe what you want, not how to create it
- **Plan before apply**: Preview changes before making them
- **State tracking**: Knows what's actually deployed
- **Modular**: Reusable components
- **Open source**: Free to use

**Alternatives**:
- AWS CloudFormation (AWS-only)
- Pulumi (uses real programming languages)
- Ansible (configuration management + IaC)

## Part 1: Terraform Setup

### Step 1: Install Terraform

**macOS**:
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux**:
```bash
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

**Windows**:
```powershell
choco install terraform
# Or download from https://www.terraform.io/downloads
```

**Verify installation**:
```bash
terraform version
```

Expected output:
```
Terraform v1.6.0
```

### Step 2: Set Up AWS Credentials

Terraform needs AWS credentials to create resources.

**Option 1: AWS CLI** (recommended):
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

**Option 2: Environment variables**:
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**Verify credentials**:
```bash
aws sts get-caller-identity
```

### Step 3: Create Project Directory

```bash
mkdir terraform-ml-infrastructure
cd terraform-ml-infrastructure
```

## Part 2: Your First Terraform Configuration

### Step 4: Create a Simple S3 Bucket

Create `main.tf`:

```hcl
# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = "us-east-1"
}

# Create an S3 bucket for ML datasets
resource "aws_s3_bucket" "ml_datasets" {
  bucket = "my-ml-datasets-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "ML Datasets Bucket"
    Environment = "Dev"
    Purpose     = "Store training datasets"
    ManagedBy   = "Terraform"
  }
}

# Generate random suffix for unique bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Block public access to the bucket
resource "aws_s3_bucket_public_access_block" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

**What's happening here?**

1. **terraform block**: Specifies Terraform and provider versions
2. **provider block**: Configures AWS provider with region
3. **resource blocks**: Define infrastructure components
4. **random_id**: Creates unique bucket name (S3 buckets must be globally unique)
5. **tags**: Metadata for organization and cost tracking

### Step 5: Initialize Terraform

```bash
terraform init
```

**What this does**:
- Downloads AWS provider plugin
- Initializes backend (where state is stored)
- Creates `.terraform` directory

**Expected output**:
```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/aws versions matching "~> 5.0"...
- Installing hashicorp/aws v5.25.0...
- Installed hashicorp/aws v5.25.0

Terraform has been successfully initialized!
```

### Step 6: Plan the Changes

```bash
terraform plan
```

**What this does**:
- Shows what Terraform will create/change/destroy
- Validates configuration syntax
- Checks state vs desired configuration

**Expected output**:
```
Terraform will perform the following actions:

  # aws_s3_bucket.ml_datasets will be created
  + resource "aws_s3_bucket" "ml_datasets" {
      + bucket                      = "my-ml-datasets-bucket-a1b2c3d4"
      + bucket_domain_name          = (known after apply)
      ...
    }

Plan: 3 to add, 0 to change, 0 to destroy.
```

**Key points**:
- `+` means resource will be created
- `~` means resource will be modified
- `-` means resource will be destroyed
- Nothing happens yet! This is just a preview.

### Step 7: Apply the Changes

```bash
terraform apply
```

Terraform will show the plan again and ask for confirmation:
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

Type `yes` and press Enter.

**Expected output**:
```
aws_s3_bucket.ml_datasets: Creating...
aws_s3_bucket.ml_datasets: Creation complete after 2s

Apply complete! Resources: 3 added, 0 changed, 0 destroyed.
```

**Verify in AWS Console**:
1. Go to AWS Console → S3
2. You should see your new bucket!

### Step 8: Understanding Terraform State

After applying, Terraform creates `terraform.tfstate`:

```bash
ls -la
```

You'll see:
```
main.tf
terraform.tfstate
terraform.tfstate.backup
.terraform/
```

**What is state?**
- JSON file tracking actual infrastructure
- Maps Terraform config to real resources
- **CRITICAL**: Don't delete or manually edit!
- **IMPORTANT**: Don't commit to Git (contains sensitive data)

Create `.gitignore`:
```
# .gitignore
.terraform/
terraform.tfstate
terraform.tfstate.backup
*.tfvars
.terraform.lock.hcl
```

## Part 3: Adding Variables and Outputs

### Step 9: Use Variables

Create `variables.tf`:

```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "ml-infrastructure"
}

variable "enable_versioning" {
  description = "Enable versioning for S3 bucket"
  type        = bool
  default     = true
}
```

Update `main.tf` to use variables:

```hcl
provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "ml_datasets" {
  bucket = "${var.project_name}-datasets-${var.environment}-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name} Datasets"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Enable versioning if configured
resource "aws_s3_bucket_versioning" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}
```

### Step 10: Add Outputs

Create `outputs.tf`:

```hcl
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.ml_datasets.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.ml_datasets.arn
}

output "bucket_region" {
  description = "Region where bucket is created"
  value       = aws_s3_bucket.ml_datasets.region
}
```

Apply changes:

```bash
terraform apply
```

**After apply, you'll see outputs**:
```
Outputs:

bucket_arn = "arn:aws:s3:::ml-infrastructure-datasets-dev-a1b2c3d4"
bucket_name = "ml-infrastructure-datasets-dev-a1b2c3d4"
bucket_region = "us-east-1"
```

**View outputs anytime**:
```bash
terraform output
terraform output bucket_name
```

## Part 4: Creating EC2 Instance for ML

### Step 11: Add EC2 Instance

Add to `main.tf`:

```hcl
# Data source to get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Security group for EC2 instance
resource "aws_security_group" "ml_instance" {
  name        = "${var.project_name}-ml-instance-sg"
  description = "Security group for ML training instance"

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # WARNING: Open to internet (for demo only!)
    description = "SSH access"
  }

  # Jupyter notebook access
  ingress {
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Jupyter Notebook"
  }

  # Outbound internet access
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name        = "${var.project_name}-ml-sg"
    Environment = var.environment
  }
}

# EC2 instance for ML training
resource "aws_instance" "ml_training" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.ml_instance.id]

  root_block_device {
    volume_size = 50  # GB
    volume_type = "gp3"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y python3 python3-pip git
              pip3 install jupyter numpy pandas scikit-learn torch

              # Create jupyter config
              mkdir -p /home/ec2-user/.jupyter
              echo "c.NotebookApp.ip = '0.0.0.0'" > /home/ec2-user/.jupyter/jupyter_notebook_config.py
              echo "c.NotebookApp.open_browser = False" >> /home/ec2-user/.jupyter/jupyter_notebook_config.py
              echo "c.NotebookApp.token = ''" >> /home/ec2-user/.jupyter/jupyter_notebook_config.py

              chown -R ec2-user:ec2-user /home/ec2-user/.jupyter
              EOF

  tags = {
    Name        = "${var.project_name}-ml-training"
    Environment = var.environment
    Purpose     = "ML Training"
  }
}
```

Add variable to `variables.tf`:

```hcl
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}
```

Add outputs to `outputs.tf`:

```hcl
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.ml_training.id
}

output "instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.ml_training.public_ip
}

output "jupyter_url" {
  description = "URL to access Jupyter Notebook"
  value       = "http://${aws_instance.ml_training.public_ip}:8888"
}
```

Apply changes:

```bash
terraform apply
```

**After creation**:
```
Outputs:

instance_id = "i-0123456789abcdef0"
instance_public_ip = "54.123.45.67"
jupyter_url = "http://54.123.45.67:8888"
bucket_arn = "arn:aws:s3:::ml-infrastructure-datasets-dev-a1b2c3d4"
bucket_name = "ml-infrastructure-datasets-dev-a1b2c3d4"
```

**Test SSH access**:
```bash
# First, create and add SSH key to AWS (manual step for now)
# Then:
ssh ec2-user@$(terraform output -raw instance_public_ip)
```

## Part 5: Using Terraform Workspaces

### Step 12: Multiple Environments

Create separate environments (dev, staging, prod):

```bash
# List workspaces
terraform workspace list

# Create dev workspace
terraform workspace new dev

# Create staging workspace
terraform workspace new staging

# Switch between workspaces
terraform workspace select dev
```

Update `main.tf` to use workspace:

```hcl
locals {
  environment = terraform.workspace
}

resource "aws_s3_bucket" "ml_datasets" {
  bucket = "${var.project_name}-datasets-${local.environment}-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.project_name} Datasets"
    Environment = local.environment
    ManagedBy   = "Terraform"
  }
}
```

Now you can deploy separate infrastructure per environment!

```bash
# Deploy to dev
terraform workspace select dev
terraform apply

# Deploy to staging
terraform workspace select staging
terraform apply
```

## Part 6: Terraform Commands Reference

### Essential Commands

```bash
# Initialize directory
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt

# Show execution plan
terraform plan

# Apply changes
terraform apply

# Apply without confirmation
terraform apply -auto-approve

# Destroy all resources
terraform destroy

# Show current state
terraform show

# List resources in state
terraform state list

# View outputs
terraform output

# Refresh state
terraform refresh
```

## Part 7: Clean Up

### Step 13: Destroy Infrastructure

**IMPORTANT**: Always clean up to avoid AWS charges!

```bash
terraform destroy
```

Review the plan, type `yes` to confirm.

**Expected output**:
```
aws_instance.ml_training: Destroying...
aws_s3_bucket.ml_datasets: Destroying...

Destroy complete! Resources: 5 destroyed.
```

**Verify in AWS Console**:
- S3 bucket should be gone
- EC2 instance should be terminated

## Challenges

### Challenge 1: Add IAM Role

Create an IAM role for the EC2 instance with S3 access:

```hcl
resource "aws_iam_role" "ml_instance_role" {
  name = "${var.project_name}-ml-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.ml_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_instance_profile" "ml_instance" {
  name = "${var.project_name}-ml-instance-profile"
  role = aws_iam_role.ml_instance_role.name
}
```

Attach to EC2 instance:
```hcl
resource "aws_instance" "ml_training" {
  # ... other config ...
  iam_instance_profile = aws_iam_instance_profile.ml_instance.name
}
```

### Challenge 2: Create Terraform Module

Organize code into reusable module structure:

```
modules/
  ml-infrastructure/
    main.tf
    variables.tf
    outputs.tf
environments/
  dev/
    main.tf
  staging/
    main.tf
  prod/
    main.tf
```

### Challenge 3: Remote State Backend

Store state in S3 instead of locally:

```hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state-bucket"
    key    = "ml-infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### Challenge 4: Add Monitoring

Add CloudWatch alarms for EC2 instance:
- CPU utilization > 80%
- Disk usage > 90%
- Network errors

## Best Practices

### 1. Version Control
```bash
# Always use Git
git init
git add *.tf .gitignore
git commit -m "Initial Terraform configuration"
```

### 2. Code Organization
```
project/
├── main.tf           # Main resources
├── variables.tf      # Variable definitions
├── outputs.tf        # Output definitions
├── terraform.tfvars  # Variable values (DON'T commit!)
├── versions.tf       # Provider versions
└── README.md         # Documentation
```

### 3. Naming Conventions
```hcl
# Use descriptive names
resource "aws_s3_bucket" "ml_training_datasets" { }  # Good
resource "aws_s3_bucket" "bucket1" { }               # Bad

# Use consistent prefixes
var.project_name = "ml-infra"

# Tag everything
tags = {
  Name        = "..."
  Environment = "..."
  ManagedBy   = "Terraform"
  Owner       = "..."
  CostCenter  = "..."
}
```

### 4. Security
```hcl
# Never commit secrets
# Use variables or AWS Secrets Manager

# Restrict access
cidr_blocks = ["YOUR_IP/32"]  # Not 0.0.0.0/0

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

### 5. State Management
```bash
# Never manually edit state
# Use terraform state commands instead

# List resources
terraform state list

# Show specific resource
terraform state show aws_instance.ml_training

# Remove resource from state (doesn't delete actual resource)
terraform state rm aws_instance.ml_training
```

## Key Takeaways

1. **IaC is essential**: Version-controlled, reproducible infrastructure
2. **Terraform is declarative**: Describe desired state, not steps
3. **Plan before apply**: Always preview changes
4. **State is critical**: Tracks real infrastructure, protect it
5. **Use variables**: Make configurations reusable
6. **Tag everything**: Organization and cost tracking
7. **Workspaces for environments**: Manage dev/staging/prod
8. **Modules for reusability**: Don't repeat yourself

## Infrastructure Considerations

### Cost Estimation

Before `terraform apply`, estimate costs:
- **t3.medium EC2**: ~$30/month (if running 24/7)
- **50GB EBS**: ~$5/month
- **S3 storage**: ~$0.023/GB/month
- **Data transfer**: Variable

**Cost optimization**:
```bash
# Stop instance when not in use
aws ec2 stop-instances --instance-ids $(terraform output -raw instance_id)

# Or destroy completely
terraform destroy
```

### Production Checklist

Before using in production:
- [ ] Remote state backend (S3 + DynamoDB for locking)
- [ ] State encryption enabled
- [ ] Terraform Cloud/Enterprise for team collaboration
- [ ] CI/CD integration for automated plans
- [ ] Code review process for infrastructure changes
- [ ] Separate AWS accounts for environments
- [ ] Restricted IAM permissions (least privilege)
- [ ] Comprehensive tagging strategy
- [ ] Backup and disaster recovery plan
- [ ] Monitoring and alerting configured

## Next Steps

1. **Learn advanced Terraform**:
   - Modules and module composition
   - Dynamic blocks and for_each
   - Terraform functions
   - Provisioners (use sparingly)

2. **Explore other providers**:
   - Google Cloud (google)
   - Azure (azurerm)
   - Kubernetes (kubernetes)
   - Datadog, PagerDuty, etc.

3. **Study state management**:
   - Remote backends
   - State locking
   - State migration
   - Workspace strategies

4. **Integration**:
   - CI/CD pipelines
   - Terraform Cloud
   - GitOps workflows
   - Policy as Code (Sentinel, OPA)

## Resources

- [Terraform Documentation](https://www.terraform.io/docs)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [HashiCorp Learn](https://learn.hashicorp.com/terraform)
- [Terraform Registry](https://registry.terraform.io/)

---

**Congratulations!** You've learned Infrastructure as Code fundamentals with Terraform. You can now define, version, and manage cloud infrastructure as code - a critical skill for modern infrastructure engineers!
