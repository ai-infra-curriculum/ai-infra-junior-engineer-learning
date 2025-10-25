# Exercise 05: SageMaker ML Platform & Cost Optimization

**Module**: Cloud Platforms
**Difficulty**: Advanced
**Estimated Time**: 5-6 hours
**Prerequisites**: Exercises 01-04, All Module 010 Lectures

---

## Learning Objectives

By completing this exercise, you will:
1. Train ML models using Amazon SageMaker with built-in algorithms
2. Deploy SageMaker endpoints with auto-scaling
3. Implement hyperparameter tuning for model optimization
4. Use SageMaker Pipelines for ML workflow orchestration
5. Implement comprehensive cost optimization strategies
6. Create cost allocation tags and budgets
7. Analyze AWS Cost Explorer for cost breakdown
8. Build a complete end-to-end ML platform on AWS

---

## Overview

This capstone exercise integrates everything from Modules 001-010. You'll build a complete ML platform using SageMaker, implement cost controls, and optimize your entire AWS infrastructure.

**Real-World Scenario**: Your company wants to scale ML model training and deployment. You'll migrate from manual training to SageMaker, implement cost governance, and create a production ML platform.

**Complete Architecture**:
```
┌──────────────────────────────────────────────────────────────┐
│                    ML Platform on AWS                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Data Ingestion        Model Training        Inference       │
│  ┌──────────┐         ┌──────────┐         ┌──────────┐    │
│  │    S3    │────────▶│SageMaker │────────▶│SageMaker │    │
│  │ Training │         │ Training │         │ Endpoint │    │
│  │   Data   │         │   Job    │         │          │    │
│  └──────────┘         └──────────┘         └────┬─────┘    │
│       │                     │                    │          │
│       │              ┌──────▼─────┐             │          │
│       │              │  Model     │             │          │
│       │              │ Registry   │             │          │
│       │              │   (S3)     │             │          │
│       │              └────────────┘             │          │
│       │                                         │          │
│  ┌────▼──────────────────────────────────────────▼────┐   │
│  │          CloudWatch Monitoring & Logging           │   │
│  └────────────────────────────────────────────────────┘   │
│  ┌────────────────────────────────────────────────────┐   │
│  │     Cost Management (Budgets, Cost Explorer)       │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## Part 1: SageMaker Training Job

### Task 1.1: Prepare Training Data

**Create Training Dataset**:
```bash
# Create directory structure
mkdir sagemaker-ml-platform && cd sagemaker-ml-platform

# Create synthetic training data (MNIST-style)
cat > prepare_data.py <<'EOF'
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
import boto3
import os

# Generate synthetic binary classification data
X, y = make_classification(
    n_samples=10000,
    n_features=20,
    n_informative=15,
    n_redundant=5,
    n_classes=2,
    random_state=42
)

# Split into train/validation/test
train_size = 7000
val_size = 1500
test_size = 1500

X_train, X_val, X_test = X[:train_size], X[train_size:train_size+val_size], X[train_size+val_size:]
y_train, y_val, y_test = y[:train_size], y[train_size:train_size+val_size], y[train_size+val_size:]

# Create DataFrames (SageMaker built-in algorithms require CSV without header)
train_data = np.column_stack([y_train, X_train])
val_data = np.column_stack([y_val, X_val])
test_data = np.column_stack([y_test, X_test])

# Save to CSV
np.savetxt('train.csv', train_data, delimiter=',', fmt='%.6f')
np.savetxt('validation.csv', val_data, delimiter=',', fmt='%.6f')
np.savetxt('test.csv', test_data, delimiter=',', fmt='%.6f')

print("Training data prepared:")
print(f"  Train: {len(train_data)} samples")
print(f"  Validation: {len(val_data)} samples")
print(f"  Test: {len(test_data)} samples")

# Upload to S3
s3 = boto3.client('s3')
bucket_name = os.environ.get('BUCKET_NAME')

if bucket_name:
    s3.upload_file('train.csv', bucket_name, 'sagemaker/training-data/train.csv')
    s3.upload_file('validation.csv', bucket_name, 'sagemaker/training-data/validation.csv')
    s3.upload_file('test.csv', bucket_name, 'sagemaker/training-data/test.csv')
    print(f"\nData uploaded to s3://{bucket_name}/sagemaker/training-data/")
else:
    print("\nSet BUCKET_NAME environment variable to upload to S3")
EOF

# Install dependencies and run
pip install numpy pandas scikit-learn boto3
python prepare_data.py
```

**Upload to S3**:
```bash
# Create S3 bucket for SageMaker
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="sagemaker-ml-platform-${ACCOUNT_ID}"

aws s3 mb s3://$BUCKET_NAME --region us-east-1

# Upload data
BUCKET_NAME=$BUCKET_NAME python prepare_data.py

# Verify upload
aws s3 ls s3://$BUCKET_NAME/sagemaker/training-data/
```

### Task 1.2: Create SageMaker Training Script

**Custom Training Script** (PyTorch):
```bash
mkdir -p src

cat > src/train.py <<'EOF'
import argparse
import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Custom dataset
class CSVDataset(Dataset):
    def __init__(self, file_path):
        data = np.loadtxt(file_path, delimiter=',')
        self.X = torch.FloatTensor(data[:, 1:])  # Features
        self.y = torch.FloatTensor(data[:, 0])   # Labels

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Simple neural network
class BinaryClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(BinaryClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

def train(args):
    # Load data
    train_dataset = CSVDataset(os.path.join(args.train, 'train.csv'))
    val_dataset = CSVDataset(os.path.join(args.validation, 'validation.csv'))

    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size)

    # Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = BinaryClassifier(input_dim=20, hidden_dim=args.hidden_dim).to(device)

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)

    # Training loop
    best_val_loss = float('inf')
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)

            optimizer.zero_grad()
            outputs = model(X_batch).squeeze()
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                outputs = model(X_batch).squeeze()
                loss = criterion(outputs, y_batch)
                val_loss += loss.item()

                predicted = (outputs > 0.5).float()
                total += y_batch.size(0)
                correct += (predicted == y_batch).sum().item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        accuracy = 100 * correct / total

        print(f"Epoch {epoch+1}/{args.epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, Accuracy: {accuracy:.2f}%")

        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(args.model_dir, 'model.pth'))

    # Save model metadata
    metadata = {
        'hidden_dim': args.hidden_dim,
        'learning_rate': args.learning_rate,
        'best_val_loss': best_val_loss,
        'accuracy': accuracy
    }
    with open(os.path.join(args.model_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f)

    print(f"Training complete! Best validation loss: {best_val_loss:.4f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Hyperparameters
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=64)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    parser.add_argument('--hidden-dim', type=int, default=128)

    # SageMaker environment variables
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAINING'))
    parser.add_argument('--validation', type=str, default=os.environ.get('SM_CHANNEL_VALIDATION'))

    args = parser.parse_args()
    train(args)
EOF

# Create requirements.txt
cat > requirements.txt <<EOF
torch==2.1.0
numpy==1.24.3
pandas==2.0.3
EOF
```

### Task 1.3: Run SageMaker Training Job

**Launch Training Job**:
```python
cat > train_sagemaker.py <<'EOF'
import sagemaker
from sagemaker.pytorch import PyTorch
from sagemaker import get_execution_role
import boto3

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
role = get_execution_role()  # Or create IAM role manually
bucket = sagemaker_session.default_bucket()

# Training data S3 paths
train_input = f's3://{bucket}/sagemaker/training-data/train.csv'
val_input = f's3://{bucket}/sagemaker/training-data/validation.csv'

# Create PyTorch estimator
estimator = PyTorch(
    entry_point='train.py',
    source_dir='src',
    role=role,
    instance_type='ml.m5.xlarge',
    instance_count=1,
    framework_version='2.1.0',
    py_version='py310',
    hyperparameters={
        'epochs': 20,
        'batch-size': 64,
        'learning-rate': 0.001,
        'hidden-dim': 128
    },
    use_spot_instances=True,  # Use Spot for 70% savings
    max_run=3600,
    max_wait=7200,
    checkpoint_s3_uri=f's3://{bucket}/sagemaker/checkpoints/',
    tags=[
        {'Key': 'Project', 'Value': 'ml-infrastructure'},
        {'Key': 'Environment', 'Value': 'dev'},
        {'Key': 'CostCenter', 'Value': 'engineering'}
    ]
)

# Start training
estimator.fit({
    'training': train_input,
    'validation': val_input
})

print(f"Training job completed!")
print(f"Model artifact: {estimator.model_data}")
EOF

# Run training
python train_sagemaker.py
```

**Or use AWS CLI**:
```bash
# Create IAM role for SageMaker
cat > sagemaker-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "sagemaker.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam create-role \
  --role-name SageMakerExecutionRole \
  --assume-role-policy-document file://sagemaker-trust-policy.json

aws iam attach-role-policy \
  --role-name SageMakerExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/SageMakerExecutionRole"

# Create training job
aws sagemaker create-training-job \
  --training-job-name ml-training-$(date +%Y%m%d%H%M%S) \
  --algorithm-specification TrainingImage=763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-training:2.1.0-cpu-py310,TrainingInputMode=File \
  --role-arn $ROLE_ARN \
  --input-data-config '[
    {
      "ChannelName": "training",
      "DataSource": {
        "S3DataSource": {
          "S3DataType": "S3Prefix",
          "S3Uri": "s3://'$BUCKET_NAME'/sagemaker/training-data/train.csv",
          "S3DataDistributionType": "FullyReplicated"
        }
      }
    }
  ]' \
  --output-data-config S3OutputPath=s3://$BUCKET_NAME/sagemaker/models \
  --resource-config InstanceType=ml.m5.xlarge,InstanceCount=1,VolumeSizeInGB=10 \
  --stopping-condition MaxRuntimeInSeconds=3600 \
  --enable-managed-spot-training \
  --checkpoint-config S3Uri=s3://$BUCKET_NAME/sagemaker/checkpoints

# Monitor training job
aws sagemaker describe-training-job --training-job-name <job-name>
```

---

## Part 2: Hyperparameter Tuning

### Task 2.1: Create Hyperparameter Tuning Job

**Define Tuning Ranges**:
```python
cat > tune_hyperparameters.py <<'EOF'
import sagemaker
from sagemaker.pytorch import PyTorch
from sagemaker.tuner import HyperparameterTuner, IntegerParameter, ContinuousParameter
from sagemaker import get_execution_role

sagemaker_session = sagemaker.Session()
role = get_execution_role()
bucket = sagemaker_session.default_bucket()

# Base estimator
estimator = PyTorch(
    entry_point='train.py',
    source_dir='src',
    role=role,
    instance_type='ml.m5.xlarge',
    instance_count=1,
    framework_version='2.1.0',
    py_version='py310',
    use_spot_instances=True,
    max_run=1800,
    max_wait=3600
)

# Hyperparameter ranges
hyperparameter_ranges = {
    'learning-rate': ContinuousParameter(0.0001, 0.01),
    'hidden-dim': IntegerParameter(64, 256),
    'batch-size': IntegerParameter(32, 128)
}

# Objective metric
objective_metric_name = 'validation:loss'
objective_type = 'Minimize'

# Create tuner
tuner = HyperparameterTuner(
    estimator,
    objective_metric_name,
    hyperparameter_ranges,
    metric_definitions=[
        {'Name': 'validation:loss', 'Regex': 'Val Loss: ([0-9\\.]+)'}
    ],
    max_jobs=20,
    max_parallel_jobs=2,
    objective_type=objective_type,
    strategy='Bayesian'  # More efficient than Random search
)

# Start tuning
tuner.fit({
    'training': f's3://{bucket}/sagemaker/training-data/train.csv',
    'validation': f's3://{bucket}/sagemaker/training-data/validation.csv'
})

# Get best training job
print(f"Best training job: {tuner.best_training_job()}")
print(f"Best hyperparameters: {tuner.best_estimator().hyperparameters()}")
EOF

python tune_hyperparameters.py
```

---

## Part 3: Deploy SageMaker Endpoint

### Task 3.1: Create Model and Endpoint

**Deploy Model**:
```python
cat > deploy_endpoint.py <<'EOF'
import sagemaker
from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role

role = get_execution_role()

# Model artifact from training job
model_data = 's3://sagemaker-ml-platform-.../output/model.tar.gz'

# Create model
pytorch_model = PyTorchModel(
    model_data=model_data,
    role=role,
    framework_version='2.1.0',
    py_version='py310',
    entry_point='inference.py',
    source_dir='src'
)

# Deploy endpoint
predictor = pytorch_model.deploy(
    instance_type='ml.t2.medium',
    initial_instance_count=2,
    endpoint_name='ml-inference-endpoint'
)

print(f"Endpoint deployed: {predictor.endpoint_name}")
EOF

# Create inference script
cat > src/inference.py <<'EOF'
import torch
import torch.nn as nn
import json
import numpy as np

class BinaryClassifier(nn.Module):
    def __init__(self, input_dim=20, hidden_dim=128):
        super(BinaryClassifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc3 = nn.Linear(hidden_dim // 2, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.sigmoid(self.fc3(x))
        return x

def model_fn(model_dir):
    model = BinaryClassifier()
    model.load_state_dict(torch.load(f'{model_dir}/model.pth'))
    model.eval()
    return model

def predict_fn(input_data, model):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    with torch.no_grad():
        tensor = torch.FloatTensor(input_data).to(device)
        output = model(tensor)
        return output.cpu().numpy()

def input_fn(request_body, content_type='application/json'):
    if content_type == 'application/json':
        data = json.loads(request_body)
        return np.array(data['features'])
    raise ValueError(f"Unsupported content type: {content_type}")

def output_fn(prediction, accept='application/json'):
    if accept == 'application/json':
        return json.dumps({'predictions': prediction.tolist()})
    raise ValueError(f"Unsupported accept type: {accept}")
EOF

python deploy_endpoint.py
```

### Task 3.2: Configure Endpoint Auto-Scaling

**Enable Auto-Scaling**:
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace sagemaker \
  --resource-id endpoint/ml-inference-endpoint/variant/AllTraffic \
  --scalable-dimension sagemaker:variant:DesiredInstanceCount \
  --min-capacity 1 \
  --max-capacity 5

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace sagemaker \
  --resource-id endpoint/ml-inference-endpoint/variant/AllTraffic \
  --scalable-dimension sagemaker:variant:DesiredInstanceCount \
  --policy-name sagemaker-endpoint-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "SageMakerVariantInvocationsPerInstance"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

### Task 3.3: Test Endpoint

**Make Predictions**:
```python
cat > test_endpoint.py <<'EOF'
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

# Test data
test_features = [[0.5] * 20]  # 20 features

response = runtime.invoke_endpoint(
    EndpointName='ml-inference-endpoint',
    ContentType='application/json',
    Body=json.dumps({'features': test_features})
)

result = json.loads(response['Body'].read().decode())
print(f"Prediction: {result}")
EOF

python test_endpoint.py
```

---

## Part 4: Cost Optimization Strategies

### Task 4.1: Implement Cost Allocation Tags

**Tag All Resources**:
```bash
# Tag S3 buckets
aws s3api put-bucket-tagging \
  --bucket $BUCKET_NAME \
  --tagging 'TagSet=[
    {Key=Project,Value=ml-infrastructure},
    {Key=Environment,Value=dev},
    {Key=CostCenter,Value=engineering},
    {Key=Owner,Value=ml-team}
  ]'

# Tag SageMaker endpoints
aws sagemaker add-tags \
  --resource-arn arn:aws:sagemaker:us-east-1:$ACCOUNT_ID:endpoint/ml-inference-endpoint \
  --tags Key=Project,Value=ml-infrastructure Key=Environment,Value=dev

# Enable Cost Allocation Tags in Billing Console
aws ce update-cost-allocation-tags-status \
  --cost-allocation-tags-status '[
    {"TagKey": "Project", "Status": "Active"},
    {"TagKey": "Environment", "Status": "Active"},
    {"TagKey": "CostCenter", "Status": "Active"}
  ]'
```

### Task 4.2: Create Cost Budget

**Monthly Budget with Alerts**:
```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > budget.json <<EOF
{
  "BudgetName": "ml-platform-monthly-budget",
  "BudgetLimit": {
    "Amount": "500",
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
        "Address": "ml-team@example.com"
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
        "Address": "ml-team@example.com"
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

### Task 4.3: Analyze Costs with Cost Explorer

**Query Costs by Service**:
```bash
# Get costs for last 30 days
aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter file://cost-filter.json

# Filter by Project tag
cat > cost-filter.json <<EOF
{
  "Tags": {
    "Key": "Project",
    "Values": ["ml-infrastructure"]
  }
}
EOF

aws ce get-cost-and-usage \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=TAG,Key=Project \
  --filter file://cost-filter.json
```

### Task 4.4: Cost Optimization Recommendations

**Create Cost Optimization Report**:
```bash
cat > cost-optimization-report.md <<'EOF'
# ML Platform Cost Optimization Report

## Current Monthly Costs (Estimated)

| Service | Cost | Optimization Opportunity |
|---------|------|--------------------------|
| **SageMaker Training** | $50 | Use Spot instances (70% savings) ✅ |
| **SageMaker Endpoints** | $85 | Right-size instances, use auto-scaling ✅ |
| **EC2 (ECS)** | $35 | Use Fargate Spot ✅ |
| **S3 Storage** | $5 | Lifecycle policies to Glacier ✅ |
| **NAT Gateway** | $66 | Use VPC endpoints for S3 ✅ |
| **Data Transfer** | $15 | Minimize cross-region transfers |
| **CloudWatch Logs** | $10 | Set retention to 7 days ✅ |
| **EKS Control Plane** | $73 | Use ECS instead (no control plane cost) |
| **Total** | **$339/month** | **Optimized: ~$180/month (47% savings)** |

## Optimization Actions Implemented

### 1. Compute Optimization
- ✅ SageMaker training with Spot instances (70% savings)
- ✅ SageMaker endpoints auto-scaling (scale to zero when idle)
- ✅ ECS Fargate Spot for inference (70% savings)
- ✅ Right-sized instance types based on CloudWatch metrics

### 2. Storage Optimization
- ✅ S3 lifecycle policies:
  - Standard → Standard-IA (30 days)
  - Standard-IA → Glacier IR (90 days)
  - Delete old training data (180 days)
- ✅ EBS snapshots lifecycle management
- ✅ CloudWatch Logs retention (7 days)

### 3. Network Optimization
- ✅ VPC endpoints for S3 (free vs $0.045/GB via NAT)
- ✅ Multi-AZ only for production (not dev/staging)
- ⚠️  Consider single NAT Gateway for dev (saves $33/month)

### 4. Cost Monitoring
- ✅ Cost allocation tags on all resources
- ✅ Monthly budget with 80% alert
- ✅ Daily cost reports to Slack
- ✅ Automated unused resource cleanup

## Additional Recommendations

### Short-term (Next 30 days)
1. **Stop dev resources after hours**
   - Schedule Lambda to stop SageMaker endpoints at 6pm
   - Save: ~$40/month

2. **Use Reserved Instances for production**
   - 1-year RI for production SageMaker endpoint
   - Save: 30-40% (~$25/month)

3. **Consolidate logging**
   - Use S3 for long-term log storage instead of CloudWatch
   - Save: ~$5/month

### Long-term (Next quarter)
1. **Migrate from EKS to ECS Fargate**
   - Eliminate $73/month control plane cost
   - Simpler operations for small team

2. **Implement model caching**
   - Use CloudFront + Lambda@Edge for frequent predictions
   - Reduce SageMaker endpoint invocations

3. **Use SageMaker Serverless Inference**
   - For low-traffic endpoints (<1000 req/day)
   - Pay per request vs constant endpoint cost

## Cost Governance Policies

1. **Require tagging**: All resources must have Project, Environment, Owner tags
2. **Auto-terminate**: Dev resources older than 7 days auto-terminated
3. **Approval required**: Production resources >$100/month require manager approval
4. **Monthly review**: Team reviews AWS Cost Explorer every month

## Estimated Total Savings

- **Current**: $339/month
- **After optimization**: $180/month
- **Annual savings**: $1,908
EOF

cat cost-optimization-report.md
```

---

## Part 5: Complete ML Platform Integration

### Task 5.1: Create End-to-End ML Pipeline

**SageMaker Pipelines**:
```python
cat > create_pipeline.py <<'EOF'
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep, CreateModelStep
from sagemaker.workflow.parameters import ParameterString, ParameterInteger
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.pytorch import PyTorch
from sagemaker import get_execution_role
import sagemaker

role = get_execution_role()
sagemaker_session = sagemaker.Session()

# Pipeline parameters
training_instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m5.xlarge")
inference_instance_type = ParameterString(name="InferenceInstanceType", default_value="ml.t2.medium")
model_approval_status = ParameterString(name="ModelApprovalStatus", default_value="PendingManualApproval")

# Step 1: Data preprocessing
sklearn_processor = SKLearnProcessor(
    framework_version='1.2-1',
    instance_type='ml.m5.large',
    instance_count=1,
    role=role
)

processing_step = ProcessingStep(
    name="PreprocessData",
    processor=sklearn_processor,
    code='preprocessing.py',
    # ... inputs/outputs
)

# Step 2: Model training
estimator = PyTorch(
    entry_point='train.py',
    source_dir='src',
    role=role,
    instance_type=training_instance_type,
    framework_version='2.1.0',
    py_version='py310'
)

training_step = TrainingStep(
    name="TrainModel",
    estimator=estimator,
    inputs={
        'training': processing_step.properties.ProcessingOutputConfig.Outputs['train'].S3Output.S3Uri
    }
)

# Step 3: Model evaluation
# ... (omitted for brevity)

# Step 4: Create model
create_model_step = CreateModelStep(
    name="CreateModel",
    model=training_step.properties.ModelArtifacts.S3ModelArtifacts,
    # ...
)

# Create pipeline
pipeline = Pipeline(
    name="ml-training-pipeline",
    parameters=[training_instance_type, inference_instance_type, model_approval_status],
    steps=[processing_step, training_step, create_model_step]
)

# Create/update pipeline
pipeline.upsert(role_arn=role)

# Start execution
execution = pipeline.start()
print(f"Pipeline execution started: {execution.arn}")
EOF
```

### Task 5.2: Monitoring Dashboard

**Create Comprehensive Dashboard**:
```bash
cat > create-dashboard.json <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/SageMaker", "ModelLatency", {"stat": "Average"}],
          [".", "Invocations", {"stat": "Sum", "yAxis": "right"}]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "SageMaker Endpoint Performance"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/SageMaker", "CPUUtilization"],
          [".", "MemoryUtilization"]
        ],
        "period": 300,
        "region": "us-east-1",
        "title": "SageMaker Endpoint Resource Usage"
      }
    },
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "TargetResponseTime"],
          [".", "RequestCount", {"yAxis": "right"}]
        ],
        "period": 60,
        "region": "us-east-1",
        "title": "ECS Inference Service"
      }
    },
    {
      "type": "log",
      "properties": {
        "query": "SOURCE '/ecs/ml-inference' | fields @timestamp, @message | filter @message like /ERROR/ | sort @timestamp desc | limit 20",
        "region": "us-east-1",
        "title": "Recent Errors"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name ml-platform-overview \
  --dashboard-body file://create-dashboard.json
```

---

## Part 6: Final Validation

### Task 6.1: Complete System Test

**End-to-End Test Script**:
```bash
cat > e2e-test.sh <<'EOF'
#!/bin/bash

echo "=== ML Platform End-to-End Test ==="
echo ""

# Test 1: SageMaker Endpoint
echo "Test 1: SageMaker Endpoint"
python test_endpoint.py && echo "✓ PASS" || echo "✗ FAIL"

# Test 2: ECS Inference Service
echo ""
echo "Test 2: ECS Inference Service"
curl -f http://$ALB_DNS/health && echo "✓ PASS" || echo "✗ FAIL"

# Test 3: Cost Budget Exists
echo ""
echo "Test 3: Cost Budget"
aws budgets describe-budgets --account-id $ACCOUNT_ID | grep -q "ml-platform-monthly-budget" && echo "✓ PASS" || echo "✗ FAIL"

# Test 4: CloudWatch Alarms
echo ""
echo "Test 4: CloudWatch Alarms"
ALARM_COUNT=$(aws cloudwatch describe-alarms --query 'MetricAlarms | length(@)')
echo "Active alarms: $ALARM_COUNT"
[[ $ALARM_COUNT -gt 0 ]] && echo "✓ PASS" || echo "✗ FAIL"

# Test 5: Cost Allocation Tags
echo ""
echo "Test 5: Cost Allocation Tags"
aws s3api get-bucket-tagging --bucket $BUCKET_NAME | grep -q "Project" && echo "✓ PASS" || echo "✗ FAIL"

echo ""
echo "=== All Tests Complete ==="
EOF

chmod +x e2e-test.sh
./e2e-test.sh
```

### Task 6.2: Generate Final Report

**Platform Summary**:
```bash
cat > platform-summary.md <<EOF
# ML Platform on AWS - Final Report

## Architecture Overview

- **VPC**: Multi-tier architecture (public, private, database subnets) across 2 AZs
- **Compute**: ECS Fargate + SageMaker (training & inference)
- **Storage**: S3 (models, data), EBS (logs), ECR (containers)
- **Networking**: ALB, NAT Gateway, VPC endpoints
- **Security**: IAM roles, Security Groups, NACLs, encryption at rest/transit
- **Monitoring**: CloudWatch (metrics, logs, alarms), dashboards
- **Cost Management**: Budgets, tags, Cost Explorer integration

## Resources Deployed

| Resource | Type | Purpose | Monthly Cost |
|----------|------|---------|--------------|
| VPC | Custom | Network isolation | $0 |
| NAT Gateway | 2x | Private subnet internet access | $66 |
| ALB | 1x | Load balancing | $16 |
| ECS Fargate | 3 tasks | Inference service | $35 |
| SageMaker Endpoint | ml.t2.medium (2x) | Model serving | $85 |
| S3 | 50GB | Data & models | $1.15 |
| ECR | 5GB | Container images | $0.50 |
| CloudWatch | Logs + Metrics | Monitoring | $10 |
| **Total** | | | **~$214/month** |

## Cost Optimizations Implemented

1. Fargate Spot (70% savings on compute)
2. SageMaker Spot training (70% savings)
3. S3 lifecycle policies (Glacier after 90 days)
4. VPC endpoints for S3 (eliminate NAT charges)
5. Auto-scaling (scale to min during low traffic)
6. Cost allocation tags (track spending by project)
7. Budgets with alerts (prevent overspending)

**Total Savings**: 47% compared to non-optimized architecture

## Security Measures

- ✅ IAM roles with least privilege
- ✅ MFA on root account
- ✅ Security Groups (stateful firewall)
- ✅ Network ACLs (stateless firewall)
- ✅ Encryption at rest (S3, EBS)
- ✅ Encryption in transit (HTTPS/TLS)
- ✅ VPC Flow Logs (network monitoring)
- ✅ CloudTrail (API audit logging)
- ✅ GuardDuty (threat detection)

## Monitoring & Alerting

- CPU utilization > 70% → Scale out
- Latency > 1s → Alert
- HTTP 5xx errors > 10 → Alert
- Cost forecast > budget → Alert
- CloudWatch dashboards for real-time visibility

## Next Steps

1. **Migrate to production**: Replicate architecture in prod AWS account
2. **Implement CI/CD**: Automate deployments with GitHub Actions
3. **Add A/B testing**: Deploy multiple model versions
4. **Implement feature store**: Centralize feature engineering
5. **Add data pipeline**: Automate data ingestion with Glue/Airflow

## Lessons Learned

- VPC endpoints save significant NAT Gateway costs
- Spot instances are reliable for training (with checkpointing)
- Tagging strategy is critical for cost allocation
- Auto-scaling prevents over-provisioning
- CloudWatch alarms catch issues before users notice

**Project Complete!** 🎉
EOF

cat platform-summary.md
```

---

## Cleanup

**Delete All Resources**:
```bash
# Delete SageMaker endpoint
aws sagemaker delete-endpoint --endpoint-name ml-inference-endpoint

# Delete SageMaker model
aws sagemaker delete-model --model-name <model-name>

# Empty and delete S3 bucket
aws s3 rm s3://$BUCKET_NAME --recursive
aws s3 rb s3://$BUCKET_NAME

# Delete ECS resources (from Exercise 04)
# Delete VPC resources (from Exercise 03)
# Delete budgets, alarms, etc.
```

---

## Deliverables

By the end of this exercise, you should have:

1. ✅ SageMaker training job with Spot instances
2. ✅ Hyperparameter tuning for model optimization
3. ✅ SageMaker endpoint with auto-scaling
4. ✅ Complete cost allocation tagging strategy
5. ✅ Cost budgets and alerts
6. ✅ Cost optimization report (47% savings)
7. ✅ End-to-end ML platform on AWS
8. ✅ Comprehensive monitoring and alerting

**Evidence**:
- SageMaker training job completion
- Deployed SageMaker endpoint
- Cost Explorer screenshots
- Platform architecture diagram
- Cost optimization report

---

## Congratulations!

You've built a complete, production-ready ML platform on AWS from scratch! You've mastered:

- **Modules 001-009**: Foundations, Python, Linux, ML, Docker, Kubernetes, APIs, Databases, Monitoring
- **Module 010**: Cloud Platforms (AWS)

**Next**: Take the Module 010 Quiz to test your knowledge!

🚀 **You're now ready for the AI Infrastructure Engineer role!**
