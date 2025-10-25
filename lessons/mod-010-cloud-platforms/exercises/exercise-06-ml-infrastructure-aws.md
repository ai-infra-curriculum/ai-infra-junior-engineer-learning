# Exercise 06: Deploy Complete ML Infrastructure on AWS

## Overview

This capstone exercise guides you through deploying a complete, production-ready ML infrastructure on AWS using Infrastructure as Code (Terraform), including model training, inference, monitoring, and CI/CD. You'll build a real-world ML platform that demonstrates all cloud skills learned in this module.

## Learning Objectives

By completing this exercise, you will:
- Deploy ML infrastructure using Terraform (IaC)
- Set up S3 for data and model storage
- Configure EC2/ECS for model training and serving
- Implement VPC networking and security groups
- Set up monitoring with CloudWatch
- Configure autoscaling for inference workloads
- Implement cost optimization strategies
- Build CI/CD pipeline for automated deployments

## Prerequisites

- Completed exercises 01-05 in this module
- All Cloud Platform lectures
- AWS account (free tier works)
- AWS CLI configured
- Terraform installed
- Basic ML and Docker knowledge

## Time Required

- Estimated: 180-240 minutes
- Difficulty: Advanced

---

## Part 1: AWS Account Setup

### Task 1.1: Create AWS Account and Configure CLI

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output: json

# Verify configuration
aws sts get-caller-identity
```

### Task 1.2: Install Terraform

```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Verify installation
terraform version
```

---

## Part 2: Infrastructure as Code (Terraform)

### Task 2.1: Create Project Structure

```bash
mkdir ml-infrastructure-aws
cd ml-infrastructure-aws

# Create Terraform structure
mkdir -p terraform/{modules,environments/{dev,prod}}
mkdir -p terraform/modules/{networking,compute,storage,security}

# Create files
touch terraform/main.tf
touch terraform/variables.tf
touch terraform/outputs.tf
touch terraform/terraform.tfvars
```

### Task 2.2: Define Networking Module

**terraform/modules/networking/main.tf:**
```hcl
# VPC
resource "aws_vpc" "ml_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project_name}-vpc"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.ml_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.ml_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.ml_vpc.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.ml_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
```

**terraform/modules/networking/variables.tf:**
```hcl
variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment (dev/prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}
```

**terraform/modules/networking/outputs.tf:**
```hcl
output "vpc_id" {
  value = aws_vpc.ml_vpc.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}
```

### Task 2.3: Define Storage Module (S3)

**terraform/modules/storage/main.tf:**
```hcl
# S3 bucket for models
resource "aws_s3_bucket" "ml_models" {
  bucket = "${var.project_name}-models-${var.environment}"

  tags = {
    Name        = "${var.project_name}-models"
    Environment = var.environment
  }
}

# Enable versioning
resource "aws_s3_bucket_versioning" "ml_models_versioning" {
  bucket = aws_s3_bucket.ml_models.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_models_encryption" {
  bucket = aws_s3_bucket.ml_models.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "ml_models_public_access" {
  bucket = aws_s3_bucket.ml_models.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket for training data
resource "aws_s3_bucket" "training_data" {
  bucket = "${var.project_name}-data-${var.environment}"

  tags = {
    Name        = "${var.project_name}-training-data"
    Environment = var.environment
  }
}

# Lifecycle policy to move old data to Glacier
resource "aws_s3_bucket_lifecycle_configuration" "training_data_lifecycle" {
  bucket = aws_s3_bucket.training_data.id

  rule {
    id     = "move-to-glacier"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 365
    }
  }
}
```

### Task 2.4: Main Terraform Configuration

**terraform/main.tf:**
```hcl
terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "my-terraform-state-bucket"
    key    = "ml-infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Networking
module "networking" {
  source = "./modules/networking"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
}

# Storage
module "storage" {
  source = "./modules/storage"

  project_name = var.project_name
  environment  = var.environment
}

# Security Groups
resource "aws_security_group" "ml_inference" {
  name        = "${var.project_name}-inference-sg"
  description = "Security group for ML inference service"
  vpc_id      = module.networking.vpc_id

  ingress {
    from_port   = 8000
    to_port     = 8000
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
    Name = "${var.project_name}-inference-sg"
  }
}

# ECS Cluster for inference
resource "aws_ecs_cluster" "ml_cluster" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# IAM Role for ECS tasks
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ml_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
}
```

**terraform/variables.tf:**
```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ml-platform"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default     = "10.0.0.0/16"
}
```

**terraform/outputs.tf:**
```hcl
output "vpc_id" {
  value = module.networking.vpc_id
}

output "models_bucket" {
  value = module.storage.models_bucket_name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.ml_cluster.name
}
```

---

## Part 3: Deploy Infrastructure

### Task 3.1: Initialize and Apply Terraform

```bash
cd terraform

# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Plan deployment
terraform plan

# Apply (create infrastructure)
terraform apply

# Save outputs
terraform output > ../outputs.txt
```

### Task 3.2: Verify Infrastructure

```bash
# List S3 buckets
aws s3 ls

# Describe VPC
aws ec2 describe-vpcs --filters "Name=tag:Name,Values=ml-platform-vpc"

# List ECS clusters
aws ecs list-clusters
```

---

## Part 4: Deploy ML Application to ECS

### Task 4.1: Create ECS Task Definition

```json
{
  "family": "ml-inference-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ml-platform-ecs-task-execution-role",
  "containerDefinitions": [
    {
      "name": "ml-api",
      "image": "YOUR_ECR_REPO/ml-inference:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MODEL_PATH",
          "value": "s3://ml-platform-models-dev/model.onnx"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ml-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ml-api"
        }
      }
    }
  ]
}
```

### Task 4.2: Create ECS Service

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster ml-platform-cluster \
  --service-name ml-inference-service \
  --task-definition ml-inference-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

---

## Part 5: Cost Optimization

### Task 5.1: Implement Auto-Scaling

**autoscaling.tf:**
```hcl
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = 10
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.ml_cluster.name}/${aws_ecs_service.ml_inference.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_policy_cpu" {
  name               = "cpu-autoscaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70.0

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}
```

### Task 5.2: Cost Monitoring

```bash
# Get cost estimate
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# Set budget alert
aws budgets create-budget \
  --account-id YOUR_ACCOUNT_ID \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

---

## Part 6: Cleanup

### Task 6.1: Destroy Infrastructure

```bash
# Destroy all Terraform-managed resources
terraform destroy

# Verify S3 buckets are empty before destroying
aws s3 rm s3://ml-platform-models-dev --recursive
aws s3 rm s3://ml-platform-data-dev --recursive
```

---

## Deliverables

Submit the following:

1. **Terraform Code**:
   - Complete IaC for VPC, S3, ECS
   - Modular structure
   - Variables and outputs

2. **Deployment Evidence**:
   - Screenshots of AWS Console showing resources
   - Terraform apply output
   - Cost estimate

3. **Documentation**:
   - Architecture diagram
   - Deployment guide
   - Cost breakdown

4. **Cleanup Evidence**:
   - Terraform destroy output
   - Confirmation all resources deleted

---

## Challenge Questions

1. **High Availability**: How would you deploy across multiple regions?

2. **Cost**: Estimate monthly cost for 1M predictions/day

3. **Security**: What additional security measures should you implement?

4. **Disaster Recovery**: Design a backup and recovery strategy

5. **Monitoring**: What CloudWatch alarms would you configure?

---

## Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Congratulations!** You've deployed a complete production ML infrastructure on AWS using Infrastructure as Code!
