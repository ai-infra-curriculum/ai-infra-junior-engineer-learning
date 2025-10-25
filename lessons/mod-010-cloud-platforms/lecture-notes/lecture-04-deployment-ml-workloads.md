# Lecture 04: Deployment Patterns & ML Workloads on AWS

**Module**: Cloud Platforms
**Level**: Junior AI Infrastructure Engineer
**Duration**: 90 minutes
**Prerequisites**: Lectures 01-03 (Cloud Fundamentals, AWS Core Services, Networking & Security)

---

## Learning Objectives

By the end of this lecture, you will be able to:
1. Use Infrastructure as Code (IaC) with Terraform to provision AWS resources
2. Deploy containerized ML applications using ECS and EKS
3. Implement serverless ML inference with AWS Lambda
4. Utilize AWS SageMaker for managed ML workflows
5. Apply cost optimization strategies for ML workloads
6. Design production-ready deployment architectures

---

## 1. Infrastructure as Code (IaC) with Terraform

### 1.1 Why Infrastructure as Code?

**Manual Infrastructure Problems**:
- **Inconsistency**: Different configurations across environments (dev, staging, prod)
- **No Version Control**: Can't track changes or rollback
- **Hard to Reproduce**: Difficult to recreate infrastructure if disaster occurs
- **Slow**: Clicking through AWS Console is time-consuming
- **No Collaboration**: Hard for teams to work together on infrastructure

**IaC Benefits**:
- **Version Controlled**: Infrastructure changes tracked in Git
- **Reproducible**: Same code → same infrastructure every time
- **Fast**: Provision complex infrastructure in minutes
- **Collaborative**: Teams can review infrastructure changes like code
- **Self-Documenting**: Code describes what infrastructure exists

### 1.2 Terraform Basics

**Terraform Workflow**:
```
Write Code → Plan Changes → Apply Changes → Infrastructure Created
```

**Terraform Architecture**:
```
┌──────────────────┐
│  Terraform Code  │ (.tf files)
│  (HCL Language)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Terraform CLI   │ (terraform plan/apply)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   AWS Provider   │ (Translates to AWS API calls)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   AWS Resources  │ (EC2, S3, VPC, etc.)
└──────────────────┘
```

### 1.3 Terraform Installation & Configuration

**Install Terraform** (Ubuntu/Debian):
```bash
# Download and install Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify installation
terraform --version
# Output: Terraform v1.6.0
```

**Configure AWS Provider**:
```hcl
# provider.tf
terraform {
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

    # Enable state locking to prevent concurrent modifications
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ML-Infrastructure"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
```

**Why S3 Backend?**
- **Remote State**: Team members can share Terraform state
- **State Locking**: DynamoDB prevents multiple people from modifying infrastructure simultaneously
- **Encryption**: State file contains sensitive data (IP addresses, resource IDs)

### 1.4 Terraform Example: ML Inference Infrastructure

**Variables** (`variables.tf`):
```hcl
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  description = "EC2 instance type for ML inference"
  type        = string
  default     = "t3.medium"
}

variable "min_instances" {
  description = "Minimum number of instances in ASG"
  type        = number
  default     = 2
}

variable "max_instances" {
  description = "Maximum number of instances in ASG"
  type        = number
  default     = 10
}
```

**VPC and Networking** (`network.tf`):
```hcl
# VPC
resource "aws_vpc" "ml_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "ml-inference-vpc-${var.environment}"
  }
}

# Public Subnets (for ALB)
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.ml_vpc.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "ml-public-subnet-${count.index + 1}-${var.environment}"
    Tier = "Public"
  }
}

# Private Subnets (for EC2 instances)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.ml_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "ml-private-subnet-${count.index + 1}-${var.environment}"
    Tier = "Private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.ml_vpc.id

  tags = {
    Name = "ml-igw-${var.environment}"
  }
}

# NAT Gateway (for private subnets to access internet)
resource "aws_eip" "nat" {
  count  = 2
  domain = "vpc"

  tags = {
    Name = "ml-nat-eip-${count.index + 1}-${var.environment}"
  }
}

resource "aws_nat_gateway" "main" {
  count         = 2
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "ml-nat-gateway-${count.index + 1}-${var.environment}"
  }
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.ml_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "ml-public-rt-${var.environment}"
  }
}

resource "aws_route_table" "private" {
  count  = 2
  vpc_id = aws_vpc.ml_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "ml-private-rt-${count.index + 1}-${var.environment}"
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

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}
```

**Security Groups** (`security.tf`):
```hcl
# ALB Security Group (allow HTTP/HTTPS from internet)
resource "aws_security_group" "alb" {
  name        = "ml-alb-sg-${var.environment}"
  description = "Security group for ML inference ALB"
  vpc_id      = aws_vpc.ml_vpc.id

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ml-alb-sg-${var.environment}"
  }
}

# Application Security Group (allow traffic only from ALB)
resource "aws_security_group" "app" {
  name        = "ml-app-sg-${var.environment}"
  description = "Security group for ML inference application"
  vpc_id      = aws_vpc.ml_vpc.id

  ingress {
    description     = "Application traffic from ALB"
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ml-app-sg-${var.environment}"
  }
}
```

**Auto Scaling Group with Launch Template** (`compute.tf`):
```hcl
# IAM Role for EC2 instances
resource "aws_iam_role" "ec2_role" {
  name = "ml-inference-ec2-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_s3_access" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ml-inference-ec2-profile-${var.environment}"
  role = aws_iam_role.ec2_role.name
}

# Launch Template
resource "aws_launch_template" "ml_app" {
  name_prefix   = "ml-inference-${var.environment}-"
  image_id      = data.aws_ami.ubuntu.id
  instance_type = var.instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.ec2_profile.name
  }

  vpc_security_group_ids = [aws_security_group.app.id]

  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    model_bucket = aws_s3_bucket.models.bucket
    environment  = var.environment
  }))

  monitoring {
    enabled = true
  }

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "ml-inference-${var.environment}"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "ml_app" {
  name                = "ml-inference-asg-${var.environment}"
  vpc_zone_identifier = aws_subnet.private[*].id
  target_group_arns   = [aws_lb_target_group.ml_app.arn]
  health_check_type   = "ELB"
  health_check_grace_period = 300

  min_size         = var.min_instances
  max_size         = var.max_instances
  desired_capacity = var.min_instances

  launch_template {
    id      = aws_launch_template.ml_app.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "ml-inference-instance-${var.environment}"
    propagate_at_launch = true
  }
}

# Auto Scaling Policies
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "ml-scale-up-${var.environment}"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.ml_app.name
}

resource "aws_autoscaling_policy" "scale_down" {
  name                   = "ml-scale-down-${var.environment}"
  scaling_adjustment     = -1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.ml_app.name
}

# CloudWatch Alarms for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "ml-high-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "70"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.ml_app.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_up.arn]
}

resource "aws_cloudwatch_metric_alarm" "low_cpu" {
  alarm_name          = "ml-low-cpu-${var.environment}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "120"
  statistic           = "Average"
  threshold           = "30"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.ml_app.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_down.arn]
}

# Data source for latest Ubuntu AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]  # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}
```

**Load Balancer** (`load-balancer.tf`):
```hcl
# Application Load Balancer
resource "aws_lb" "ml_app" {
  name               = "ml-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = var.environment == "prod" ? true : false

  tags = {
    Name = "ml-alb-${var.environment}"
  }
}

# Target Group
resource "aws_lb_target_group" "ml_app" {
  name     = "ml-tg-${var.environment}"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.ml_vpc.id

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name = "ml-tg-${var.environment}"
  }
}

# Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.ml_app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ml_app.arn
  }
}
```

**S3 Bucket for Models** (`storage.tf`):
```hcl
resource "aws_s3_bucket" "models" {
  bucket = "ml-models-${var.environment}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "ml-models-${var.environment}"
  }
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "models" {
  bucket = aws_s3_bucket.models.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

data "aws_caller_identity" "current" {}
```

**Outputs** (`outputs.tf`):
```hcl
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.ml_app.dns_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.ml_vpc.id
}

output "model_bucket_name" {
  description = "S3 bucket for ML models"
  value       = aws_s3_bucket.models.bucket
}

output "autoscaling_group_name" {
  description = "Auto Scaling Group name"
  value       = aws_autoscaling_group.ml_app.name
}
```

### 1.5 Terraform Workflow Commands

**Initialize Terraform** (download providers and modules):
```bash
terraform init
```

**Format Code** (standardize formatting):
```bash
terraform fmt -recursive
```

**Validate Configuration** (check for errors):
```bash
terraform validate
```

**Plan Changes** (preview what will be created):
```bash
terraform plan -var="environment=dev" -out=tfplan
```

**Apply Changes** (create infrastructure):
```bash
terraform apply tfplan
```

**Show Current State**:
```bash
terraform show
```

**Destroy Infrastructure** (delete all resources):
```bash
terraform destroy -var="environment=dev"
```

**Terraform State Management**:
```bash
# List all resources in state
terraform state list

# Show details of a specific resource
terraform state show aws_lb.ml_app

# Remove a resource from state (doesn't delete actual resource)
terraform state rm aws_lb.ml_app
```

---

## 2. Container Orchestration: ECS and EKS

### 2.1 Amazon ECS (Elastic Container Service)

**ECS Architecture**:
```
┌─────────────────────────────────────────────┐
│         Application Load Balancer           │
└────────────────┬────────────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼─────┐         ┌─────▼─────┐
│  ECS Task │         │  ECS Task │
│ Container │         │ Container │
│  Port 5000│         │  Port 5000│
└───────────┘         └───────────┘
      │                     │
┌─────▼──────────────────────▼─────┐
│        ECS Service               │
│  (Desired count: 3 tasks)        │
└──────────────┬───────────────────┘
               │
┌──────────────▼───────────────────┐
│        ECS Cluster               │
│  (EC2 or Fargate launch type)    │
└──────────────────────────────────┘
```

**ECS Concepts**:
- **Task Definition**: Blueprint for your application (like a Dockerfile)
- **Task**: Running instance of a task definition
- **Service**: Manages desired number of tasks, integrates with load balancer
- **Cluster**: Logical grouping of tasks or services

### 2.2 ECS Task Definition Example

**Create Task Definition JSON** (`task-definition.json`):
```json
{
  "family": "ml-inference-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ml-inference-task-role",
  "containerDefinitions": [
    {
      "name": "ml-inference-container",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-inference:v1.0",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "MODEL_PATH",
          "value": "/models/resnet50.pth"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:ml-api-key-abc123"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ml-inference",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:5000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

**Register Task Definition**:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### 2.3 Create ECS Service

**Create ECS Cluster** (Fargate launch type):
```bash
aws ecs create-cluster --cluster-name ml-inference-cluster
```

**Create ECS Service with ALB Integration**:
```bash
aws ecs create-service \
  --cluster ml-inference-cluster \
  --service-name ml-inference-service \
  --task-definition ml-inference-task:1 \
  --desired-count 3 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-0abc123,subnet-0def456],
    securityGroups=[sg-0ghi789],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/ml-tg/abc123,containerName=ml-inference-container,containerPort=5000" \
  --health-check-grace-period-seconds 60
```

**Enable Auto Scaling for ECS Service**:
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/ml-inference-cluster/ml-inference-service \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy based on CPU utilization
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/ml-inference-cluster/ml-inference-service \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### 2.4 Amazon EKS (Elastic Kubernetes Service)

**Why EKS over ECS?**
- **Portability**: Run on any Kubernetes cluster (GCP GKE, Azure AKS, on-prem)
- **Ecosystem**: Vast ecosystem of tools (Helm, Istio, ArgoCD)
- **Flexibility**: More control over networking, storage, scheduling
- **Multi-Cloud**: Easier to adopt multi-cloud strategy

**EKS Architecture**:
```
┌────────────────────────────────────────┐
│         EKS Control Plane              │
│  (Managed by AWS - API Server, etcd)   │
└────────────────┬───────────────────────┘
                 │
      ┌──────────┴──────────┐
      │                     │
┌─────▼─────┐         ┌─────▼─────┐
│  Worker   │         │  Worker   │
│  Node 1   │         │  Node 2   │
│  (EC2)    │         │  (EC2)    │
└───────────┘         └───────────┘
      │                     │
   ┌──▼──┐               ┌──▼──┐
   │ Pod │               │ Pod │
   └─────┘               └─────┘
```

### 2.5 Create EKS Cluster with eksctl

**Install eksctl**:
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Verify installation
eksctl version
```

**Create EKS Cluster** (this takes ~15-20 minutes):
```bash
eksctl create cluster \
  --name ml-inference-cluster \
  --region us-east-1 \
  --nodegroup-name ml-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed \
  --version 1.28
```

**Configure kubectl**:
```bash
aws eks update-kubeconfig --region us-east-1 --name ml-inference-cluster

# Verify connection
kubectl get nodes
```

### 2.6 Deploy ML Application on EKS

**Deployment YAML** (`ml-deployment.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-inference
  labels:
    app: ml-inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-inference
  template:
    metadata:
      labels:
        app: ml-inference
    spec:
      containers:
      - name: ml-inference
        image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-inference:v1.0
        ports:
        - containerPort: 5000
        env:
        - name: MODEL_PATH
          value: "/models/resnet50.pth"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ml-inference-service
spec:
  type: LoadBalancer
  selector:
    app: ml-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-inference-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Deploy to EKS**:
```bash
# Apply deployment
kubectl apply -f ml-deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get svc ml-inference-service

# Get load balancer URL
kubectl get svc ml-inference-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Test inference endpoint
curl http://<load-balancer-url>/predict -X POST -H "Content-Type: application/json" -d '{"image_url": "https://example.com/cat.jpg"}'
```

**View Logs**:
```bash
# Get pod names
kubectl get pods -l app=ml-inference

# View logs for a specific pod
kubectl logs <pod-name>

# Follow logs in real-time
kubectl logs -f <pod-name>
```

### 2.7 ECS vs EKS Decision Matrix

| Factor | ECS | EKS |
|--------|-----|-----|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Simple, AWS-native | ⭐⭐⭐ Steeper learning curve |
| **Cost** | ⭐⭐⭐⭐ No control plane cost | ⭐⭐⭐ $0.10/hour for control plane |
| **Portability** | ⭐⭐ AWS-only | ⭐⭐⭐⭐⭐ Runs anywhere |
| **Ecosystem** | ⭐⭐⭐ Growing | ⭐⭐⭐⭐⭐ Vast Kubernetes ecosystem |
| **Integration** | ⭐⭐⭐⭐⭐ Deep AWS integration | ⭐⭐⭐⭐ Good AWS integration |
| **Flexibility** | ⭐⭐⭐ Limited customization | ⭐⭐⭐⭐⭐ Highly customizable |

**Recommendation for Junior Engineers**:
- **Start with ECS Fargate** for simplicity
- **Learn Kubernetes** concepts with EKS once comfortable with containers
- **Use EKS for production ML** if multi-cloud or portability is important

---

## 3. Serverless ML Inference with AWS Lambda

### 3.1 When to Use Serverless for ML?

**Good Fit for Lambda**:
- ✅ **Infrequent Predictions**: Sporadic traffic (< 1000 req/hour)
- ✅ **Small Models**: Model size < 250MB (uncompressed)
- ✅ **Fast Inference**: Prediction time < 15 minutes
- ✅ **Variable Load**: Traffic spikes unpredictably
- ✅ **Cost Optimization**: Pay only when running

**Not Good for Lambda**:
- ❌ **Large Models**: Deep learning models > 250MB
- ❌ **Long Inference**: Predictions taking > 15 minutes
- ❌ **High Throughput**: Sustained high traffic (better with ECS/EKS)
- ❌ **GPU Required**: Lambda doesn't support GPU

### 3.2 Lambda Inference Example

**Lambda Function** (`lambda_function.py`):
```python
import json
import boto3
import pickle
import numpy as np

# Initialize S3 client
s3 = boto3.client('s3')

# Global variable to cache model (persists across invocations)
model = None
MODEL_BUCKET = 'ml-models-prod'
MODEL_KEY = 'sklearn_model.pkl'

def load_model():
    """Load model from S3 (cached after first invocation)"""
    global model
    if model is None:
        print("Loading model from S3...")
        obj = s3.get_object(Bucket=MODEL_BUCKET, Key=MODEL_KEY)
        model = pickle.loads(obj['Body'].read())
        print("Model loaded successfully")
    return model

def lambda_handler(event, context):
    """
    Lambda handler for ML inference

    Event format:
    {
        "features": [1.2, 3.4, 5.6, 7.8]
    }
    """
    try:
        # Parse input
        body = json.loads(event['body']) if 'body' in event else event
        features = np.array(body['features']).reshape(1, -1)

        # Load model (cached after first call)
        model = load_model()

        # Make prediction
        prediction = model.predict(features)
        probability = model.predict_proba(features)

        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'prediction': int(prediction[0]),
                'probability': float(probability[0][1]),
                'model_version': '1.0'
            })
        }

    except Exception as e:
        print(f"Error during inference: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
```

**Package Lambda Function**:
```bash
# Create deployment package directory
mkdir lambda-package
cd lambda-package

# Install dependencies
pip install numpy scikit-learn -t .

# Copy function code
cp ../lambda_function.py .

# Create ZIP file
zip -r lambda-package.zip .

# Upload to S3
aws s3 cp lambda-package.zip s3://my-lambda-code-bucket/
```

**Create Lambda Function**:
```bash
# Create IAM role for Lambda
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name ml-lambda-execution-role \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name ml-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name ml-lambda-execution-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create Lambda function
aws lambda create-function \
  --function-name ml-inference-lambda \
  --runtime python3.11 \
  --role arn:aws:iam::123456789012:role/ml-lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --code S3Bucket=my-lambda-code-bucket,S3Key=lambda-package.zip \
  --timeout 30 \
  --memory-size 1024 \
  --environment Variables={MODEL_BUCKET=ml-models-prod,MODEL_KEY=sklearn_model.pkl}
```

### 3.3 API Gateway Integration

**Create REST API**:
```bash
# Create REST API
aws apigateway create-rest-api \
  --name "ML Inference API" \
  --description "Serverless ML inference API"

# Get API ID (from output above)
API_ID="abc123defg"

# Get root resource ID
aws apigateway get-resources --rest-api-id $API_ID

ROOT_ID="xyz789"

# Create /predict resource
aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part predict

PREDICT_RESOURCE_ID="pred123"

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $PREDICT_RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $PREDICT_RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:123456789012:function:ml-inference-lambda/invocations

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name ml-inference-lambda \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:123456789012:$API_ID/*/POST/predict"

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

**Test API**:
```bash
curl -X POST https://$API_ID.execute-api.us-east-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [1.2, 3.4, 5.6, 7.8]}'
```

---

## 4. AWS SageMaker for Managed ML

### 4.1 SageMaker Components

**SageMaker Platform**:
```
┌──────────────────────────────────────────────┐
│           SageMaker Studio                   │  (Jupyter-based IDE)
└──────────────────┬───────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐   ┌─────▼─────┐  ┌────▼─────┐
│Training│   │Processing │  │Inference │
│  Jobs  │   │   Jobs    │  │Endpoints │
└────────┘   └───────────┘  └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
         ┌─────────▼─────────┐
         │   Model Registry  │
         └───────────────────┘
```

**Key SageMaker Features**:
- **Built-in Algorithms**: XGBoost, Linear Learner, Image Classification
- **Managed Training**: Automatic provisioning and scaling
- **Hyperparameter Tuning**: Automated optimization
- **Model Registry**: Version control for models
- **Endpoints**: Managed inference with auto-scaling
- **SageMaker Pipelines**: MLOps workflow orchestration

### 4.2 SageMaker Training Job Example

**Train a Model Using SageMaker**:
```python
import sagemaker
from sagemaker import get_execution_role
from sagemaker.sklearn import SKLearn

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
role = get_execution_role()

# Define training script
# (Assumes you have train.py in local directory)
sklearn_estimator = SKLearn(
    entry_point='train.py',
    role=role,
    instance_type='ml.m5.large',
    framework_version='1.2-1',
    py_version='py3',
    hyperparameters={
        'n_estimators': 100,
        'max_depth': 10,
        'learning_rate': 0.1
    }
)

# Start training job
sklearn_estimator.fit({'training': 's3://my-bucket/training-data/'})
```

**Training Script** (`train.py`):
```python
import argparse
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)

    # SageMaker specific arguments
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))

    args = parser.parse_args()

    # Load training data
    train_data = pd.read_csv(os.path.join(args.train, 'train.csv'))
    X_train = train_data.drop('target', axis=1)
    y_train = train_data['target']

    # Train model
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
    model.fit(X_train, y_train)

    # Save model
    joblib.dump(model, os.path.join(args.model_dir, 'model.joblib'))
```

### 4.3 Deploy Model to SageMaker Endpoint

**Deploy Trained Model**:
```python
# Deploy model to endpoint
predictor = sklearn_estimator.deploy(
    initial_instance_count=2,
    instance_type='ml.t2.medium',
    endpoint_name='ml-inference-endpoint'
)

# Make predictions
import numpy as np
test_data = np.array([[1.2, 3.4, 5.6, 7.8]])
prediction = predictor.predict(test_data)
print(f"Prediction: {prediction}")
```

**Configure Auto Scaling**:
```python
import boto3

client = boto3.client('application-autoscaling')

# Register scalable target
client.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/ml-inference-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,
    MaxCapacity=5
)

# Create scaling policy
client.put_scaling_policy(
    PolicyName='ml-endpoint-scaling-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/ml-inference-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,
        'ScaleOutCooldown': 60
    }
)
```

### 4.4 SageMaker Pipelines (MLOps)

**Define ML Pipeline**:
```python
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.parameters import ParameterInteger

# Define pipeline parameters
instance_count = ParameterInteger(name="InstanceCount", default_value=1)

# Processing step
processing_step = ProcessingStep(
    name="PreprocessData",
    # ... processing configuration
)

# Training step
training_step = TrainingStep(
    name="TrainModel",
    estimator=sklearn_estimator,
    inputs={
        'training': processing_step.properties.ProcessingOutputConfig.Outputs['train'].S3Output.S3Uri
    }
)

# Create pipeline
pipeline = Pipeline(
    name="ml-training-pipeline",
    parameters=[instance_count],
    steps=[processing_step, training_step]
)

# Create/update pipeline
pipeline.upsert(role_arn=role)

# Start pipeline execution
execution = pipeline.start()
```

---

## 5. Cost Optimization for ML Workloads

### 5.1 Compute Cost Optimization

**EC2 Pricing Models**:
| Model | Cost Savings | Use Case |
|-------|--------------|----------|
| **On-Demand** | Baseline (1x) | Production inference (unpredictable load) |
| **Reserved Instances** | 30-40% | Steady-state workloads (1-3 year commitment) |
| **Spot Instances** | 50-90% | Batch training (fault-tolerant) |
| **Savings Plans** | 25-35% | Flexible commitment (any instance family) |

**Use Spot Instances for Training**:
```bash
# Launch training job with Spot instances
aws sagemaker create-training-job \
  --training-job-name ml-training-spot \
  --algorithm-specification TrainingImage=<image-uri>,TrainingInputMode=File \
  --role-arn arn:aws:iam::123456789012:role/SageMakerRole \
  --input-data-config file://input-data-config.json \
  --output-data-config S3OutputPath=s3://my-bucket/output \
  --resource-config InstanceType=ml.p3.2xlarge,InstanceCount=1,VolumeSizeInGB=50 \
  --stopping-condition MaxRuntimeInSeconds=86400 \
  --enable-managed-spot-training \
  --checkpoint-config S3Uri=s3://my-bucket/checkpoints
```

**Spot Instance Best Practices**:
- ✅ **Use for Training**: Models can resume from checkpoints
- ✅ **Enable Checkpointing**: Save progress frequently
- ✅ **Use Multiple Instance Types**: Increase spot availability
- ❌ **Don't Use for Inference**: Interruptions affect user requests

### 5.2 Storage Cost Optimization

**S3 Storage Classes**:
| Class | Cost | Access Time | Use Case |
|-------|------|-------------|----------|
| **S3 Standard** | $0.023/GB | Instant | Active models |
| **S3 Intelligent-Tiering** | $0.0025-0.023/GB | Instant | Unknown access patterns |
| **S3 Glacier Instant Retrieval** | $0.004/GB | Instant | Archived models (accessed quarterly) |
| **S3 Glacier Deep Archive** | $0.00099/GB | 12 hours | Long-term archives |

**Lifecycle Policy Example**:
```json
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
          "Days": 90,
          "StorageClass": "GLACIER_IR"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
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
    }
  ]
}
```

**Apply Lifecycle Policy**:
```bash
aws s3api put-bucket-lifecycle-configuration \
  --bucket ml-models-bucket \
  --lifecycle-configuration file://lifecycle-policy.json
```

### 5.3 Right-Sizing Instances

**Monitor Resource Utilization**:
```bash
# Get CloudWatch metrics for EC2 CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --start-time 2025-10-01T00:00:00Z \
  --end-time 2025-10-23T23:59:59Z \
  --period 3600 \
  --statistics Average

# Analyze memory utilization (requires CloudWatch agent)
aws cloudwatch get-metric-statistics \
  --namespace CWAgent \
  --metric-name mem_used_percent \
  --dimensions Name=InstanceId,Value=i-0abc123def456 \
  --start-time 2025-10-01T00:00:00Z \
  --end-time 2025-10-23T23:59:59Z \
  --period 3600 \
  --statistics Average
```

**Right-Sizing Decision Matrix**:
- **CPU < 30%**: Consider smaller instance type
- **CPU 30-70%**: Optimal utilization
- **CPU > 70%**: Consider larger instance or scaling out
- **Memory < 50%**: Over-provisioned memory
- **Memory > 80%**: Risk of OOM errors, increase memory

### 5.4 Cost Monitoring and Alerts

**Enable Cost Allocation Tags**:
```bash
aws ce create-cost-category-definition \
  --name "ML-Project-Costs" \
  --rules '[
    {
      "Value": "training",
      "Rule": {
        "Tags": {
          "Key": "Workload",
          "Values": ["training"]
        }
      }
    },
    {
      "Value": "inference",
      "Rule": {
        "Tags": {
          "Key": "Workload",
          "Values": ["inference"]
        }
      }
    }
  ]'
```

**Create Budget with Alert**:
```bash
cat > budget.json <<EOF
{
  "BudgetName": "ML-Monthly-Budget",
  "BudgetLimit": {
    "Amount": "500",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKeyValue": ["user:Project$ML-Infrastructure"]
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
        "Address": "ml-team@example.com"
      }
    ]
  }
]
EOF

aws budgets create-budget \
  --account-id 123456789012 \
  --budget file://budget.json \
  --notifications-with-subscribers file://notifications.json
```

### 5.5 Cost Optimization Checklist

**Infrastructure**:
- [ ] Use Spot instances for training jobs
- [ ] Enable auto-scaling for inference
- [ ] Right-size instances based on utilization
- [ ] Use Reserved Instances for steady workloads
- [ ] Delete unused resources (stopped EC2, old snapshots)

**Storage**:
- [ ] Implement S3 lifecycle policies
- [ ] Use S3 Intelligent-Tiering for unknown patterns
- [ ] Compress large datasets before storing
- [ ] Delete old CloudWatch Logs (> 30 days)
- [ ] Use EBS snapshots instead of keeping volumes

**Networking**:
- [ ] Use VPC endpoints to avoid NAT Gateway costs
- [ ] Minimize cross-region data transfer
- [ ] Use CloudFront for serving static assets
- [ ] Enable S3 Transfer Acceleration only if needed

**Monitoring**:
- [ ] Set up cost allocation tags
- [ ] Create budgets with alerts
- [ ] Review AWS Cost Explorer monthly
- [ ] Use AWS Trusted Advisor recommendations
- [ ] Enable AWS Compute Optimizer

---

## 6. Production-Ready Deployment Architecture

### 6.1 Complete ML Infrastructure Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Route 53 (DNS)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    CloudFront (CDN)                             │
│              (Cache predictions, DDoS protection)               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
        ┌────────▼────────┐     ┌────────▼────────┐
        │   VPC (us-east-1)│     │  VPC (us-west-2)│
        │                  │     │                  │
        │  ┌────────────┐  │     │  ┌────────────┐ │
        │  │    ALB     │  │     │  │    ALB     │ │
        │  └─────┬──────┘  │     │  └─────┬──────┘ │
        │        │         │     │        │        │
        │  ┌─────▼──────┐  │     │  ┌─────▼──────┐ │
        │  │  ECS/EKS   │  │     │  │  ECS/EKS   │ │
        │  │  (Fargate) │  │     │  │  (Fargate) │ │
        │  │  3 tasks   │  │     │  │  3 tasks   │ │
        │  └─────┬──────┘  │     │  └─────┬──────┘ │
        │        │         │     │        │        │
        │  ┌─────▼──────┐  │     │  ┌─────▼──────┐ │
        │  │    RDS     │  │     │  │ RDS Replica│ │
        │  │ Multi-AZ   │  │     │  │ (Read-only)│ │
        │  └────────────┘  │     │  └────────────┘ │
        └──────────────────┘     └──────────────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │  S3 (Models)    │
                    │  - Versioning   │
                    │  - Encryption   │
                    │  - Lifecycle    │
                    └─────────────────┘
                             │
                    ┌────────▼────────┐
                    │  CloudWatch     │
                    │  - Metrics      │
                    │  - Logs         │
                    │  - Alarms       │
                    └─────────────────┘
```

### 6.2 Deployment Strategy: Blue/Green Deployment

**Blue/Green with ECS**:
```bash
# Step 1: Deploy new version (Green) alongside existing (Blue)
aws ecs update-service \
  --cluster ml-inference-cluster \
  --service ml-inference-service \
  --task-definition ml-inference-task:2 \
  --desired-count 3 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100"

# Step 2: Wait for new tasks to be healthy
aws ecs wait services-stable \
  --cluster ml-inference-cluster \
  --services ml-inference-service

# Step 3: Monitor metrics (error rate, latency)
# If metrics are good, deployment is complete
# If metrics are bad, rollback:

aws ecs update-service \
  --cluster ml-inference-cluster \
  --service ml-inference-service \
  --task-definition ml-inference-task:1
```

**Canary Deployment** (gradual rollout):
```bash
# Route 10% of traffic to new version
aws elbv2 modify-listener \
  --listener-arn <listener-arn> \
  --default-actions Type=forward,ForwardConfig='{
    "TargetGroups": [
      {"TargetGroupArn": "<blue-tg>", "Weight": 90},
      {"TargetGroupArn": "<green-tg>", "Weight": 10}
    ]
  }'

# Monitor for 30 minutes, then increase to 50%
# If successful, switch 100% to green
```

---

## 7. Summary and Best Practices

### Key Takeaways

1. **Infrastructure as Code**:
   - Always use Terraform/CloudFormation for production
   - Version control all infrastructure changes
   - Use remote state with locking

2. **Container Orchestration**:
   - **ECS**: Simple, AWS-native, good for getting started
   - **EKS**: Portable, powerful, better for complex workloads
   - Always use Fargate for serverless containers

3. **Serverless ML**:
   - Great for low-traffic, small models
   - Use Lambda + API Gateway for cost optimization
   - Cache models globally to reduce cold starts

4. **SageMaker**:
   - Managed platform reduces operational overhead
   - Use for end-to-end ML lifecycle
   - Built-in monitoring and auto-scaling

5. **Cost Optimization**:
   - Use Spot instances for training (50-90% savings)
   - Implement auto-scaling for inference
   - Right-size instances based on actual usage
   - Use S3 lifecycle policies for storage

### Production Checklist

**Infrastructure**:
- [ ] Multi-AZ deployment for high availability
- [ ] Auto-scaling configured (CPU and request-based)
- [ ] Load balancer health checks enabled
- [ ] VPC with public and private subnets
- [ ] Security groups following least privilege

**Monitoring**:
- [ ] CloudWatch metrics for all resources
- [ ] CloudWatch Alarms for critical metrics
- [ ] Centralized logging (CloudWatch Logs or ELK)
- [ ] Cost monitoring and budgets
- [ ] Performance monitoring (latency, throughput)

**Security**:
- [ ] IAM roles with minimal permissions
- [ ] Secrets stored in Secrets Manager
- [ ] Encryption at rest and in transit
- [ ] Regular security audits
- [ ] VPC Flow Logs enabled

**Operations**:
- [ ] Blue/Green or Canary deployment strategy
- [ ] Automated rollback on failures
- [ ] Backup and disaster recovery plan
- [ ] Documentation for runbooks
- [ ] On-call rotation and incident response

---

## Next Steps

In the next module, you will:
- Complete hands-on exercises deploying ML infrastructure
- Build a complete production-ready ML platform
- Practice cost optimization techniques
- Implement monitoring and alerting from Module 009

**Recommended Reading**:
- AWS Well-Architected Framework (ML Lens)
- Terraform AWS Provider Documentation
- Kubernetes Documentation
- SageMaker Developer Guide

---

## Exercise Preview

**Module 010 Exercises**:
1. **Exercise 01**: AWS Account Setup & IAM Best Practices
2. **Exercise 02**: Provision EC2 and S3 with CLI
3. **Exercise 03**: Build Production VPC with Terraform
4. **Exercise 04**: Deploy Containerized ML Service (ECS/EKS)
5. **Exercise 05**: SageMaker Training + Cost Optimization

Get ready to apply everything you've learned across all 10 modules!
