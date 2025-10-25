# Exercise 04: Deploy Containerized ML Inference Service

**Module**: Cloud Platforms
**Difficulty**: Intermediate-Advanced
**Estimated Time**: 5-6 hours
**Prerequisites**: Exercises 01-03, Lecture 04 (Deployment & ML Workloads)

---

## Learning Objectives

By completing this exercise, you will:
1. Build and containerize an ML inference application with Docker
2. Push Docker images to Amazon ECR (Elastic Container Registry)
3. Deploy containers using ECS Fargate with Application Load Balancer
4. Configure auto-scaling based on CPU and request count
5. Implement blue/green deployment for zero-downtime updates
6. Deploy the same application on EKS (Kubernetes) for comparison
7. Set up CloudWatch monitoring and alarms for containerized workloads
8. Implement cost optimization strategies for container deployments

---

## Overview

This exercise deploys a production-ready containerized ML inference service using the VPC from Exercise 03. You'll containerize a PyTorch image classification API and deploy it with both ECS and EKS to understand the differences.

**Real-World Scenario**: Your team built an image classification model (ResNet50). You need to deploy it as a scalable, highly available API that can handle 1000+ requests/second with auto-scaling and zero-downtime deployments.

**Architecture**:
```
Internet
    │
    ▼
┌─────────────────┐
│  Route 53 DNS   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   ALB    │  (Public subnets)
    └────┬─────┘
         │
    ┌────▼──────────────────────┐
    │   ECS Service / EKS       │  (Private subnets)
    │   3 tasks/pods            │
    │   ┌────┐ ┌────┐ ┌────┐   │
    │   │Task│ │Task│ │Task│   │
    │   └────┘ └────┘ └────┘   │
    └───────────┬───────────────┘
                │
         ┌──────▼──────┐
         │     RDS     │  (Database subnets)
         └─────────────┘
```

---

## Part 1: Build ML Inference Application

### Task 1.1: Create Flask API for Image Classification

**Project Structure**:
```bash
mkdir ml-inference-app && cd ml-inference-app

# Create directory structure
mkdir -p src models tests

# Create application
cat > src/app.py <<'EOF'
from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import io
import os
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('ml_inference_requests_total', 'Total inference requests')
REQUEST_LATENCY = Histogram('ml_inference_latency_seconds', 'Inference latency')
ERROR_COUNT = Counter('ml_inference_errors_total', 'Total errors')

# Load model
MODEL_PATH = os.environ.get('MODEL_PATH', '/models/resnet50.pth')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

logger.info(f"Loading model from {MODEL_PATH}")
model = models.resnet50(pretrained=True)
model.eval()
model.to(DEVICE)
logger.info(f"Model loaded successfully on {DEVICE}")

# Image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# ImageNet classes (top 10 for demo)
CLASSES = {
    281: 'tabby cat',
    282: 'tiger cat',
    283: 'Persian cat',
    284: 'Siamese cat',
    285: 'Egyptian cat',
    207: 'golden retriever',
    208: 'Labrador retriever',
    209: 'German shepherd',
    210: 'beagle',
    211: 'bloodhound'
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'resnet50',
        'device': str(DEVICE)
    }), 200

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness check endpoint"""
    try:
        # Test model inference
        dummy_input = torch.randn(1, 3, 224, 224).to(DEVICE)
        with torch.no_grad():
            _ = model(dummy_input)
        return jsonify({'status': 'ready'}), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({'status': 'not ready', 'error': str(e)}), 503

@app.route('/predict', methods=['POST'])
def predict():
    """Image classification endpoint"""
    REQUEST_COUNT.inc()
    start_time = time.time()

    try:
        # Validate request
        if 'file' not in request.files:
            ERROR_COUNT.inc()
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            ERROR_COUNT.inc()
            return jsonify({'error': 'Empty filename'}), 400

        # Load and preprocess image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        input_tensor = preprocess(image).unsqueeze(0).to(DEVICE)

        # Inference
        with torch.no_grad():
            output = model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

        # Get top 5 predictions
        top5_prob, top5_idx = torch.topk(probabilities, 5)

        predictions = []
        for i in range(5):
            idx = top5_idx[i].item()
            prob = top5_prob[i].item()
            class_name = CLASSES.get(idx, f'class_{idx}')
            predictions.append({
                'class': class_name,
                'confidence': round(prob, 4),
                'class_id': idx
            })

        # Record latency
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)

        logger.info(f"Prediction completed in {latency:.3f}s - Top class: {predictions[0]['class']}")

        return jsonify({
            'predictions': predictions,
            'latency_seconds': round(latency, 3),
            'model_version': '1.0'
        }), 200

    except Exception as e:
        ERROR_COUNT.inc()
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

# Create requirements.txt
cat > requirements.txt <<EOF
flask==3.0.0
torch==2.1.0
torchvision==0.16.0
Pillow==10.1.0
prometheus-client==0.19.0
gunicorn==21.2.0
boto3==1.34.0
EOF

# Create test script
cat > tests/test_api.py <<'EOF'
import requests
import io
from PIL import Image

def test_health():
    response = requests.get('http://localhost:5000/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

def test_predict():
    # Create a dummy image
    img = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    response = requests.post(
        'http://localhost:5000/predict',
        files={'file': ('test.jpg', img_bytes, 'image/jpeg')}
    )

    assert response.status_code == 200
    data = response.json()
    assert 'predictions' in data
    assert len(data['predictions']) == 5
    assert 'latency_seconds' in data

if __name__ == '__main__':
    test_health()
    print("✓ Health check passed")
    test_predict()
    print("✓ Prediction test passed")
EOF
```

### Task 1.2: Create Dockerfile

**Multi-stage Dockerfile** (for smaller image size):
```bash
cat > Dockerfile <<'EOF'
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# Create models directory
RUN mkdir -p /models

# Set PATH to include user-installed packages
ENV PATH=/root/.local/bin:$PATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "60", "src.app:app"]
EOF

# Create .dockerignore
cat > .dockerignore <<EOF
__pycache__
*.pyc
*.pyo
*.pyd
.git
.gitignore
README.md
tests/
.pytest_cache
*.egg-info
EOF
```

### Task 1.3: Build and Test Locally

**Build Docker Image**:
```bash
# Build image
docker build -t ml-inference:v1.0 .

# Check image size
docker images ml-inference:v1.0

# Run container locally
docker run -d -p 5000:5000 --name ml-inference-test ml-inference:v1.0

# Wait for container to be healthy
sleep 10

# Test health endpoint
curl http://localhost:5000/health

# Test prediction with a sample image
# Download a test image
curl -o cat.jpg https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/220px-Cat03.jpg

# Make prediction
curl -X POST -F "file=@cat.jpg" http://localhost:5000/predict

# Check logs
docker logs ml-inference-test

# Check metrics
curl http://localhost:5000/metrics

# Stop and remove container
docker stop ml-inference-test
docker rm ml-inference-test
```

---

## Part 2: Push to Amazon ECR

### Task 2.1: Create ECR Repository

**Create ECR Repository**:
```bash
# Create repository
REPO_URI=$(aws ecr create-repository \
  --repository-name ml-inference \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256 \
  --tags Key=Project,Value=ml-infrastructure \
  --query 'repository.repositoryUri' \
  --output text)

echo "ECR Repository: $REPO_URI"

# Set lifecycle policy (delete old images after 30 days)
cat > lifecycle-policy.json <<EOF
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Delete untagged images after 7 days",
      "selection": {
        "tagStatus": "untagged",
        "countType": "sinceImagePushed",
        "countUnit": "days",
        "countNumber": 7
      },
      "action": {
        "type": "expire"
      }
    },
    {
      "rulePriority": 2,
      "description": "Keep only last 10 tagged images",
      "selection": {
        "tagStatus": "tagged",
        "tagPrefixList": ["v"],
        "countType": "imageCountMoreThan",
        "countNumber": 10
      },
      "action": {
        "type": "expire"
      }
    }
  ]
}
EOF

aws ecr put-lifecycle-policy \
  --repository-name ml-inference \
  --lifecycle-policy-text file://lifecycle-policy.json
```

### Task 2.2: Push Docker Image to ECR

**Authenticate and Push**:
```bash
# Get AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Tag image for ECR
docker tag ml-inference:v1.0 ${REPO_URI}:v1.0
docker tag ml-inference:v1.0 ${REPO_URI}:latest

# Push to ECR
docker push ${REPO_URI}:v1.0
docker push ${REPO_URI}:latest

# Verify push
aws ecr describe-images --repository-name ml-inference
```

---

## Part 3: Deploy with ECS Fargate

### Task 3.1: Create ECS Cluster

**Create Cluster**:
```bash
# Create ECS cluster
CLUSTER_NAME="ml-inference-cluster"
aws ecs create-cluster \
  --cluster-name $CLUSTER_NAME \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=2 \
    capacityProvider=FARGATE_SPOT,weight=4 \
  --tags key=Project,value=ml-infrastructure

echo "ECS Cluster: $CLUSTER_NAME"
```

### Task 3.2: Create Task Definition

**Create IAM Roles** (if not exists):
```bash
# Task execution role (for pulling images, writing logs)
cat > task-execution-role-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file://task-execution-role-trust-policy.json \
  || true

aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Task role (for application to access AWS services)
cat > task-role-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name ml-inference-task-role \
  --assume-role-policy-document file://task-role-trust-policy.json \
  || true

aws iam attach-role-policy \
  --role-name ml-inference-task-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

**Create Task Definition**:
```bash
cat > task-definition.json <<EOF
{
  "family": "ml-inference-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::${ACCOUNT_ID}:role/ml-inference-task-role",
  "containerDefinitions": [
    {
      "name": "ml-inference",
      "image": "${REPO_URI}:v1.0",
      "essential": true,
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
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ml-inference",
          "awslogs-region": "${REGION}",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
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
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### Task 3.3: Create Application Load Balancer

**Note**: Use VPC and subnets from Exercise 03. If you don't have them, create a simple VPC:

```bash
# Get VPC ID (from Exercise 03 or default VPC)
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=ml-infrastructure-vpc" --query 'Vpcs[0].VpcId' --output text)

# Get public subnets
PUBLIC_SUBNET_1=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=ml-public-subnet-1a" --query 'Subnets[0].SubnetId' --output text)
PUBLIC_SUBNET_2=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=ml-public-subnet-1b" --query 'Subnets[0].SubnetId' --output text)

# Get private subnets
PRIVATE_SUBNET_1=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=ml-private-subnet-1a" --query 'Subnets[0].SubnetId' --output text)
PRIVATE_SUBNET_2=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=ml-private-subnet-1b" --query 'Subnets[0].SubnetId' --output text)

# Get security group IDs
ALB_SG=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=alb-sg" --query 'SecurityGroups[0].GroupId' --output text)
APP_SG=$(aws ec2 describe-security-groups --filters "Name=tag:Name,Values=app-server-sg" --query 'SecurityGroups[0].GroupId' --output text)
```

**Create ALB**:
```bash
# Create Application Load Balancer
ALB_ARN=$(aws elbv2 create-load-balancer \
  --name ml-inference-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Project,Value=ml-infrastructure \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

# Get ALB DNS name
ALB_DNS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns $ALB_ARN \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "ALB DNS: $ALB_DNS"

# Create target group
TG_ARN=$(aws elbv2 create-target-group \
  --name ml-inference-tg \
  --protocol HTTP \
  --port 5000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --deregistration-delay 30 \
  --tags Key=Project,Value=ml-infrastructure \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN

echo "Target Group: $TG_ARN"
```

### Task 3.4: Create ECS Service

**Create Service**:
```bash
# Create ECS service
aws ecs create-service \
  --cluster $CLUSTER_NAME \
  --service-name ml-inference-service \
  --task-definition ml-inference-task \
  --desired-count 3 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={
    subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],
    securityGroups=[$APP_SG],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=$TG_ARN,containerName=ml-inference,containerPort=5000" \
  --health-check-grace-period-seconds 60 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100" \
  --tags key=Project,value=ml-infrastructure

# Wait for service to be stable (may take 3-5 minutes)
echo "Waiting for service to stabilize..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services ml-inference-service

echo "Service deployed! Test at: http://$ALB_DNS/health"
```

### Task 3.5: Test ECS Deployment

**Test Endpoints**:
```bash
# Test health endpoint
curl http://$ALB_DNS/health

# Test prediction
curl -X POST -F "file=@cat.jpg" http://$ALB_DNS/predict

# Load test (requires apache-bench)
ab -n 1000 -c 10 http://$ALB_DNS/health
```

---

## Part 4: Auto-Scaling Configuration

### Task 4.1: Configure ECS Service Auto-Scaling

**Register Scalable Target**:
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/$CLUSTER_NAME/ml-inference-service \
  --min-capacity 2 \
  --max-capacity 10

# CPU-based scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/$CLUSTER_NAME/ml-inference-service \
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

# Request count-based scaling
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/$CLUSTER_NAME/ml-inference-service \
  --policy-name request-count-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "'$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].LoadBalancerArn' --output text | awk -F: '{print $6}')'/'$(aws elbv2 describe-target-groups --target-group-arns $TG_ARN --query 'TargetGroups[0].TargetGroupArn' --output text | awk -F: '{print $6}')'"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### Task 4.2: Test Auto-Scaling

**Generate Load**:
```bash
# Install hey (HTTP load generator)
# go install github.com/rakyll/hey@latest

# Or use docker
docker run --rm williamyeh/hey \
  -n 10000 -c 100 -q 10 \
  http://$ALB_DNS/health

# Watch task count increase
watch -n 5 "aws ecs describe-services --cluster $CLUSTER_NAME --services ml-inference-service --query 'services[0].{Desired:desiredCount,Running:runningCount}'"
```

---

## Part 5: Blue/Green Deployment

### Task 5.1: Update Application (v1.1)

**Make Code Change**:
```bash
# Update app.py (add version endpoint)
cat >> src/app.py <<'EOF'

@app.route('/version', methods=['GET'])
def version():
    return jsonify({'version': '1.1', 'features': ['version endpoint']}), 200
EOF

# Rebuild Docker image
docker build -t ml-inference:v1.1 .

# Push to ECR
docker tag ml-inference:v1.1 ${REPO_URI}:v1.1
docker push ${REPO_URI}:v1.1

# Register new task definition (update image tag to v1.1)
sed 's/:v1.0/:v1.1/g' task-definition.json > task-definition-v1.1.json
aws ecs register-task-definition --cli-input-json file://task-definition-v1.1.json
```

### Task 5.2: Blue/Green Deployment

**Update Service**:
```bash
# Update service to new task definition
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service ml-inference-service \
  --task-definition ml-inference-task:2 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100"

# Monitor deployment
aws ecs wait services-stable --cluster $CLUSTER_NAME --services ml-inference-service

# Test new version
curl http://$ALB_DNS/version
# Should return: {"version": "1.1", "features": ["version endpoint"]}

# If deployment fails, rollback:
# aws ecs update-service --cluster $CLUSTER_NAME --service ml-inference-service --task-definition ml-inference-task:1
```

---

## Part 6: Deploy on EKS (Kubernetes)

### Task 6.1: Create EKS Cluster

**Create Cluster with eksctl**:
```bash
# Create EKS cluster (takes 15-20 minutes)
eksctl create cluster \
  --name ml-inference-eks \
  --region us-east-1 \
  --vpc-public-subnets $PUBLIC_SUBNET_1,$PUBLIC_SUBNET_2 \
  --vpc-private-subnets $PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2 \
  --nodegroup-name ml-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 5 \
  --managed \
  --version 1.28

# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name ml-inference-eks

# Verify cluster
kubectl get nodes
```

### Task 6.2: Deploy Application on EKS

**Create Kubernetes Manifests**:
```bash
mkdir k8s && cd k8s

# Deployment
cat > deployment.yaml <<EOF
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
        image: ${REPO_URI}:v1.1
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
EOF

# Deploy
kubectl apply -f deployment.yaml

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get svc ml-inference-service

# Get load balancer URL (may take 2-3 minutes)
EKS_LB_URL=$(kubectl get svc ml-inference-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Test
curl http://$EKS_LB_URL/health
```

### Task 6.3: Compare ECS vs EKS

**Create Comparison Matrix**:
```bash
cat > ecs-vs-eks-comparison.md <<EOF
# ECS vs EKS Comparison

## Deployment Complexity

| Aspect | ECS Fargate | EKS |
|--------|-------------|-----|
| **Setup Time** | ~30 minutes | ~45 minutes (cluster creation takes longer) |
| **Configuration** | Task definition (JSON) | Kubernetes manifests (YAML) |
| **Learning Curve** | ⭐⭐ Easy | ⭐⭐⭐⭐ Steep |
| **AWS Integration** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐⭐ Good |

## Cost

| Component | ECS Fargate | EKS |
|-----------|-------------|-----|
| **Control Plane** | Free | \$0.10/hour (\$73/month) |
| **Compute (3 tasks/pods)** | ~\$35/month (1vCPU, 2GB) | ~\$35/month (t3.medium nodes) |
| **Total** | ~\$35/month | ~\$108/month |

## Features

| Feature | ECS | EKS |
|---------|-----|-----|
| **Portability** | AWS-only | Multi-cloud (GCP, Azure, on-prem) |
| **Ecosystem** | AWS services | Vast K8s ecosystem (Helm, Istio, etc.) |
| **Auto-scaling** | Built-in | HPA, VPA, Cluster Autoscaler |
| **Blue/Green** | Built-in | Requires Argo Rollouts / Flagger |
| **Observability** | CloudWatch | Prometheus, Grafana (self-managed) |

## Recommendation

- **Use ECS Fargate** if:
  - You're AWS-only
  - Want simplicity and fast iteration
  - Need tight AWS service integration
  - Team is small (<5 engineers)

- **Use EKS** if:
  - Multi-cloud or hybrid cloud strategy
  - Need Kubernetes ecosystem tools
  - Large team with K8s expertise
  - Complex orchestration requirements
EOF

cat ecs-vs-eks-comparison.md
```

---

## Part 7: Monitoring and Observability

### Task 7.1: CloudWatch Dashboards

**Create Dashboard**:
```bash
cat > cloudwatch-dashboard.json <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", {"stat": "Average", "label": "CPU %"}],
          [".", "MemoryUtilization", {"stat": "Average"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "ECS Resource Utilization"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "TargetResponseTime", {"stat": "Average"}],
          [".", "RequestCount", {"stat": "Sum"}]
        ],
        "period": 60,
        "region": "us-east-1",
        "title": "ALB Metrics"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ECS", "RunningTaskCount", {"stat": "Average"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "Task Count"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name ml-inference-dashboard \
  --dashboard-body file://cloudwatch-dashboard.json
```

### Task 7.2: Create CloudWatch Alarms

**High Latency Alarm**:
```bash
# Create SNS topic for alerts
TOPIC_ARN=$(aws sns create-topic --name ml-inference-alerts --query 'TopicArn' --output text)
aws sns subscribe --topic-arn $TOPIC_ARN --protocol email --notification-endpoint your-email@example.com

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ml-inference-high-latency \
  --alarm-description "Alert when response time > 1 second" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 1.0 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].LoadBalancerArn' --output text | awk -F: '{print $6}') \
  --alarm-actions $TOPIC_ARN

# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ml-inference-high-error-rate \
  --alarm-description "Alert when HTTP 5xx > 10" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=$(aws elbv2 describe-load-balancers --load-balancer-arns $ALB_ARN --query 'LoadBalancers[0].LoadBalancerArn' --output text | awk -F: '{print $6}') \
  --alarm-actions $TOPIC_ARN
```

---

## Part 8: Cost Optimization

### Task 8.1: Use Fargate Spot

**Update Service to Use Spot**:
```bash
# Update service capacity provider strategy
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service ml-inference-service \
  --capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=4

# Now 80% of tasks will run on Spot (70% cost savings)
```

### Task 8.2: Right-Size Tasks

**Analyze CloudWatch Metrics**:
```bash
# Get CPU utilization over last 7 days
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=ml-inference-service Name=ClusterName,Value=$CLUSTER_NAME \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --query 'Datapoints[].Average' | jq 'add/length'

# If average CPU < 30%, consider reducing to 512 CPU / 1024 memory
```

---

## Cleanup

**Delete ECS Resources**:
```bash
# Delete ECS service
aws ecs update-service --cluster $CLUSTER_NAME --service ml-inference-service --desired-count 0
aws ecs delete-service --cluster $CLUSTER_NAME --service ml-inference-service

# Delete ALB
aws elbv2 delete-load-balancer --load-balancer-arn $ALB_ARN
aws elbv2 delete-target-group --target-group-arn $TG_ARN

# Delete ECS cluster
aws ecs delete-cluster --cluster $CLUSTER_NAME

# Delete ECR repository
aws ecr delete-repository --repository-name ml-inference --force
```

**Delete EKS Resources**:
```bash
# Delete EKS cluster
eksctl delete cluster --name ml-inference-eks
```

---

## Deliverables

By the end of this exercise, you should have:

1. ✅ Containerized ML inference application
2. ✅ Docker image pushed to Amazon ECR
3. ✅ ECS Fargate deployment with ALB
4. ✅ Auto-scaling based on CPU and request count
5. ✅ Blue/green deployment strategy
6. ✅ EKS deployment for comparison
7. ✅ CloudWatch monitoring and alarms
8. ✅ Cost optimization with Fargate Spot

**Evidence**:
- Screenshots of running ECS tasks
- ALB health check results
- Auto-scaling test results
- ECS vs EKS comparison matrix

---

## Next Steps

- **Exercise 05**: SageMaker training, cost optimization, and final integration
- **Quiz**: 50 comprehensive questions on cloud platforms

Excellent work deploying production containerized ML infrastructure! 🎉
