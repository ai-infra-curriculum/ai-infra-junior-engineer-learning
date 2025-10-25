# Lecture 05: Multi-Cloud Strategies and Cost Optimization

## Table of Contents
1. [Introduction](#introduction)
2. [Multi-Cloud Architecture](#multi-cloud-architecture)
3. [Cloud Cost Fundamentals](#cloud-cost-fundamentals)
4. [Cost Optimization for ML Workloads](#cost-optimization-for-ml-workloads)
5. [FinOps for AI Infrastructure](#finops-for-ai-infrastructure)
6. [Disaster Recovery and Business Continuity](#disaster-recovery-and-business-continuity)
7. [Cloud Migration Strategies](#cloud-migration-strategies)
8. [Summary and Key Takeaways](#summary-and-key-takeaways)

## Introduction

Cloud costs for ML workloads can spiral out of control without proper planning. A single large GPU instance running 24/7 can cost $25,000/year. Multiply that across training, inference, and experimentation, and costs can easily reach six or seven figures.

This lecture covers strategies to optimize cloud spending, architect multi-cloud solutions, and ensure business continuity for ML infrastructure.

### Learning Objectives

By the end of this lecture, you will:
- Understand multi-cloud architecture patterns and trade-offs
- Identify and optimize major cost drivers in ML workloads
- Implement FinOps practices for AI infrastructure
- Design disaster recovery strategies for ML systems
- Plan and execute cloud migrations
- Apply rightsizing, scheduling, and purchasing strategies

### Prerequisites
- Lectures 01-04 in this module (Cloud fundamentals, AWS services)
- Understanding of ML workflows (training, inference, data storage)
- Basic knowledge of cloud pricing models

**Duration**: 90 minutes
**Difficulty**: Intermediate

---

## 1. Multi-Cloud Architecture

### Why Multi-Cloud?

```
Single Cloud Risks:
┌────────────────────────────────────┐
│ All ML infrastructure on AWS      │
│                                    │
│ Risks:                             │
│ ✗ Vendor lock-in                   │
│ ✗ Single point of failure          │
│ ✗ Price increases (no leverage)    │
│ ✗ Limited by one vendor's features │
│ ✗ Regional outage = total downtime │
└────────────────────────────────────┘

Multi-Cloud Benefits:
┌────────────────────────────────────┐
│ ML infrastructure across AWS/GCP   │
│                                    │
│ Benefits:                          │
│ ✓ Best-of-breed services           │
│ ✓ Negotiating leverage             │
│ ✓ Disaster recovery                │
│ ✓ Regulatory compliance (data     │
│   residency across regions)        │
└────────────────────────────────────┘
```

### Multi-Cloud Strategies

#### 1. Best-of-Breed (Use Each Cloud's Strengths)

```
Architecture:
┌─────────────────────────────────────┐
│ AWS                                 │
│ ├── S3: Data lake storage          │
│ ├── EKS: Model serving (Kubernetes)│
│ └── RDS: Metadata database         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ GCP                                 │
│ ├── Vertex AI: Model training      │
│ ├── BigQuery: Data warehouse       │
│ └── TPUs: Large model training     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Azure                               │
│ ├── Azure ML: AutoML experiments   │
│ └── Cognitive Services: Pre-trained │
│     models                          │
└─────────────────────────────────────┘
```

**Example rationale:**
- AWS: Strong ecosystem, mature Kubernetes (EKS), best S3 pricing
- GCP: Best for data analytics (BigQuery), TPUs for transformers
- Azure: Enterprise integration (Active Directory), hybrid cloud

#### 2. Active-Passive Disaster Recovery

```
Primary: AWS (active)
├── All production traffic
├── 100% of inference requests
└── All model training

Secondary: GCP (passive/warm standby)
├── Data replicated continuously
├── Infrastructure ready (scaled to 0)
└── Activated only during AWS outage
```

#### 3. Active-Active for High Availability

```
Both clouds handle production traffic:

AWS (60% traffic)          GCP (40% traffic)
├── US-East users          ├── US-West users
├── EU users               ├── Asia-Pacific users
└── Shared data via        └── Shared data via
    cross-cloud sync            cross-cloud sync

Benefits:
✓ Higher availability
✓ Lower latency (geo-distribution)
✗ Complex (data consistency, sync)
✗ Higher cost (run both simultaneously)
```

### Multi-Cloud Challenges

1. **Data Synchronization**
   ```python
   # Replicate data from AWS S3 to GCS
   from google.cloud import storage as gcs_storage
   import boto3

   s3_client = boto3.client('s3')
   gcs_client = gcs_storage.Client()

   # List AWS S3 objects
   objects = s3_client.list_objects_v2(Bucket='ml-models-aws')

   for obj in objects.get('Contents', []):
       # Download from S3
       s3_obj = s3_client.get_object(
           Bucket='ml-models-aws',
           Key=obj['Key']
       )

       # Upload to GCS
       bucket = gcs_client.bucket('ml-models-gcp')
       blob = bucket.blob(obj['Key'])
       blob.upload_from_string(s3_obj['Body'].read())

   print(f"Synced {len(objects)} objects from AWS to GCP")
   ```

2. **Identity and Access Management (IAM)**
   - AWS IAM ≠ GCP IAM ≠ Azure RBAC
   - Use centralized identity provider (Okta, Azure AD)
   - Implement SAML/OIDC for SSO

3. **Networking**
   ```
   Connect AWS VPC to GCP VPC:
   ┌─────────────┐         ┌─────────────┐
   │ AWS VPC     │         │ GCP VPC     │
   │ 10.0.0.0/16 │◄───────►│ 10.1.0.0/16 │
   └─────────────┘         └─────────────┘
        VPN or Direct Connect / Cloud Interconnect
   ```

4. **Monitoring**
   - Use cloud-agnostic tools: Prometheus, Grafana, Datadog
   - Aggregate logs: ELK stack, Loki, Splunk

### Multi-Cloud Decision Framework

| Use Multi-Cloud If: | Avoid Multi-Cloud If: |
|---------------------|------------------------|
| Critical uptime requirements (99.99%+) | Team is small (<10 engineers) |
| Regulatory needs (data residency) | Cost is more important than availability |
| Leverage best services from each | Complexity outweighs benefits |
| Large enough to negotiate pricing | Already locked into one cloud |

---

## 2. Cloud Cost Fundamentals

### Cloud Pricing Models

#### On-Demand Instances

**Pros**: Flexibility, no commitment
**Cons**: Most expensive (baseline)

```
AWS EC2 p3.2xlarge (1x V100 GPU):
- On-demand: $3.06/hour
- Cost per month (24/7): $2,203/month
- Cost per year: $26,438/year
```

#### Reserved Instances (1-3 year commitment)

**Savings**: 30-70% vs on-demand

```
AWS EC2 p3.2xlarge:
- On-demand: $3.06/hour
- 1-year reserved: $1.84/hour (40% savings)
- 3-year reserved: $1.10/hour (64% savings)

Annual cost (3-year reserved):
$1.10 × 24 × 365 = $9,636 vs $26,438 on-demand
Savings: $16,802/year (64%)
```

**Use for**: Baseline, predictable workloads (production inference)

#### Spot Instances (Spare capacity, can be interrupted)

**Savings**: 50-90% vs on-demand

```
AWS EC2 p3.2xlarge spot:
- On-demand: $3.06/hour
- Spot (avg): $0.92/hour (70% savings)

But: Can be interrupted with 2-minute notice!
```

**Use for**: Fault-tolerant workloads (training with checkpointing)

#### Savings Plans (Flexible commitment)

**AWS Compute Savings Plans**: Commit to $/hour for 1-3 years

```
Commit to $1/hour for 3 years:
- AWS applies discount to any compute usage
- More flexible than reserved instances
- 17-60% savings depending on commitment
```

---

## 3. Cost Optimization for ML Workloads

### Major Cost Drivers in ML

```
Typical ML Infrastructure Costs:
┌────────────────────────────────────┐
│ GPU Compute:          60%  $60k/yr │
│ Storage (data/models): 20%  $20k/yr │
│ Networking:           10%  $10k/yr │
│ Managed Services:      7%   $7k/yr │
│ Data Transfer:         3%   $3k/yr │
│ Total:               100% $100k/yr │
└────────────────────────────────────┘
```

### Optimization Strategy 1: Right-Sizing

**Problem**: Over-provisioned instances waste money

```python
# Analyze actual usage
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client('cloudwatch')

# Get CPU utilization for last 30 days
response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId', 'Value': 'i-1234567890'}],
    StartTime=datetime.now() - timedelta(days=30),
    EndTime=datetime.now(),
    Period=3600,  # 1 hour
    Statistics=['Average', 'Maximum']
)

avg_cpu = sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints'])
print(f"Average CPU: {avg_cpu:.1f}%")

# If avg_cpu < 20%, instance is over-provisioned!
```

**Action**: Downsize instance type

```
Current: ml.p3.8xlarge (4 GPUs) @ $12.24/hour
Average GPU utilization: 30%

Rightsize to: ml.p3.2xlarge (1 GPU) @ $3.06/hour
Savings: $9.18/hour × 720 hours/month = $6,610/month
```

### Optimization Strategy 2: Auto-Scaling

**Problem**: Fixed capacity wastes money during low-demand periods

```python
# Auto-scaling inference endpoints
import boto3

autoscaling = boto3.client('application-autoscaling')

# Register scalable target
autoscaling.register_scalable_target(
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/ml-inference-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    MinCapacity=1,  # Scale down to 1 instance during low traffic
    MaxCapacity=10  # Scale up to 10 during peak
)

# Configure scaling policy (target 70% CPU)
autoscaling.put_scaling_policy(
    PolicyName='cpu-scaling-policy',
    ServiceNamespace='sagemaker',
    ResourceId='endpoint/ml-inference-endpoint/variant/AllTraffic',
    ScalableDimension='sagemaker:variant:DesiredInstanceCount',
    PolicyType='TargetTrackingScaling',
    TargetTrackingScalingPolicyConfiguration={
        'TargetValue': 70.0,  # Target 70% CPU utilization
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'SageMakerVariantInvocationsPerInstance'
        },
        'ScaleInCooldown': 300,   # Wait 5 min before scaling down
        'ScaleOutCooldown': 60    # Wait 1 min before scaling up
    }
)
```

**Savings**:
```
Without auto-scaling: 10 instances × 24/7 = 7,200 instance-hours/month
With auto-scaling: Avg 4 instances = 2,880 instance-hours/month
Savings: 60% reduction = $13,220/month saved
```

### Optimization Strategy 3: Scheduled Scaling

**Problem**: Dev/test environments run 24/7 unnecessarily

```python
# Stop instances outside business hours
import boto3
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    current_hour = datetime.now().hour

    # Business hours: 9 AM - 6 PM PST
    if 9 <= current_hour < 18:
        # Start dev instances
        ec2.start_instances(InstanceIds=['i-dev-12345'])
    else:
        # Stop dev instances
        ec2.stop_instances(InstanceIds=['i-dev-12345'])
```

**Savings**:
```
Without scheduling: 24 hours/day × 30 days = 720 hours/month
With scheduling (9 AM - 6 PM): 9 hours/day × 22 workdays = 198 hours/month
Savings: 72% reduction = $1,590/month per instance
```

### Optimization Strategy 4: Spot Instances for Training

```python
# Train with spot instances (AWS SageMaker)
import sagemaker

estimator = sagemaker.estimator.Estimator(
    image_uri='my-training-image',
    role='SageMakerRole',
    instance_count=4,
    instance_type='ml.p3.2xlarge',
    use_spot_instances=True,  # Use spot!
    max_run=3600,  # Max 1 hour
    max_wait=7200,  # Wait up to 2 hours for spot capacity
    checkpoint_s3_uri='s3://my-bucket/checkpoints/'  # Save checkpoints
)

estimator.fit({'training': 's3://my-bucket/data'})
```

**Savings**:
```
Training job: 4 × p3.2xlarge × 8 hours
On-demand: $3.06/hour × 4 × 8 = $97.92
Spot: $0.92/hour × 4 × 8 = $29.44
Savings: $68.48 (70%)
```

### Optimization Strategy 5: Storage Tiering

**Problem**: All data stored in expensive hot storage

```python
# Move old models to cheaper storage
import boto3
from datetime import datetime, timedelta

s3 = boto3.client('s3')

# List models in S3
response = s3.list_objects_v2(Bucket='ml-models')

for obj in response.get('Contents', []):
    last_modified = obj['LastModified'].replace(tzinfo=None)
    age_days = (datetime.now() - last_modified).days

    # Move models older than 90 days to Glacier
    if age_days > 90:
        s3.copy_object(
            Bucket='ml-models',
            Key=obj['Key'],
            CopySource={'Bucket': 'ml-models', 'Key': obj['Key']},
            StorageClass='GLACIER'
        )
        print(f"Moved {obj['Key']} to Glacier (age: {age_days} days)")
```

**Storage Cost Comparison**:
```
S3 Standard: $0.023/GB/month
S3 Infrequent Access: $0.0125/GB/month (46% savings)
S3 Glacier: $0.004/GB/month (83% savings)

1TB of old models:
Standard: $23.60/month
Glacier: $4.10/month
Savings: $19.50/month ($234/year)
```

---

## 4. FinOps for AI Infrastructure

### What is FinOps?

**FinOps** (Financial Operations) brings financial accountability to cloud spending.

**Principles**:
1. **Teams collaborate** (engineering, finance, business)
2. **Everyone owns their usage**
3. **Centralized team drives FinOps**
4. **Visibility** into spending
5. **Decisions are driven by business value**

### Cost Allocation and Tagging

```python
# Tag all resources for cost tracking
import boto3

ec2 = boto3.client('ec2')

# Tag instances
ec2.create_tags(
    Resources=['i-1234567890'],
    Tags=[
        {'Key': 'Project', 'Value': 'recommendation-system'},
        {'Key': 'Environment', 'Value': 'production'},
        {'Key': 'Team', 'Value': 'ml-platform'},
        {'Key': 'CostCenter', 'Value': '12345'},
        {'Key': 'Owner', 'Value': 'alice@company.com'}
    ]
)
```

**Cost Dashboard by Tag**:
```
Cost by Project (Last 30 days):
├── recommendation-system: $45,234 (45%)
├── fraud-detection: $32,890 (33%)
├── search-ranking: $15,432 (15%)
└── experimentation: $7,123 (7%)

Cost by Environment:
├── production: $75,234 (75%)
├── staging: $15,432 (15%)
└── dev: $10,023 (10%)
```

### Budgets and Alerts

```python
# Set budget with alerts
import boto3

budgets = boto3.client('budgets')

budgets.create_budget(
    AccountId='123456789012',
    Budget={
        'BudgetName': 'ML-Platform-Monthly',
        'BudgetLimit': {
            'Amount': '100000',  # $100k/month
            'Unit': 'USD'
        },
        'TimeUnit': 'MONTHLY',
        'BudgetType': 'COST'
    },
    NotificationsWithSubscribers=[
        {
            'Notification': {
                'NotificationType': 'ACTUAL',
                'ComparisonOperator': 'GREATER_THAN',
                'Threshold': 80,  # Alert at 80% of budget
                'ThresholdType': 'PERCENTAGE'
            },
            'Subscribers': [
                {
                    'SubscriptionType': 'EMAIL',
                    'Address': 'ml-team@company.com'
                }
            ]
        },
        {
            'Notification': {
                'NotificationType': 'FORECASTED',
                'ComparisonOperator': 'GREATER_THAN',
                'Threshold': 100,  # Forecast alert at 100%
                'ThresholdType': 'PERCENTAGE'
            },
            'Subscribers': [
                {
                    'SubscriptionType': 'EMAIL',
                    'Address': 'finance@company.com'
                }
            ]
        }
    ]
)
```

---

## 5. Disaster Recovery and Business Continuity

### RPO and RTO Targets

```
RPO (Recovery Point Objective):
How much data can you afford to lose?
├── RPO = 1 hour → Lose max 1 hour of data
└── Requires: Continuous replication or hourly backups

RTO (Recovery Time Objective):
How quickly must systems be back online?
├── RTO = 4 hours → System back within 4 hours
└── Requires: Warm standby or faster
```

### DR Strategies for ML

#### Strategy 1: Backup and Restore (Lowest cost, highest RTO)

```
RPO: Hours to days
RTO: Hours to days
Cost: Low ($$$)

Implementation:
1. Daily model backups to S3
2. Database backups to S3
3. Infrastructure as Code in Git
4. In disaster: Recreate from backups

Best for: Non-critical systems
```

#### Strategy 2: Pilot Light (Low cost, medium RTO)

```
RPO: Minutes
RTO: Hours
Cost: Low-Medium ($$$$)

Implementation:
Primary AWS:
├── Full production environment
└── All traffic

Secondary GCP (minimal):
├── Database replica (live)
├── S3 → GCS replication (live)
└── Infrastructure code ready (not running)

In disaster:
1. Scale up GCP infrastructure
2. Point DNS to GCP
3. Resume operations (1-4 hours)

Best for: Important systems with moderate uptime needs
```

#### Strategy 3: Warm Standby (Medium cost, low RTO)

```
RPO: Seconds
RTO: Minutes
Cost: Medium ($$$$$$)

Implementation:
Primary AWS:
├── Full production (100% traffic)

Secondary GCP:
├── Scaled-down replicas (running at 20% capacity)
├── Live data replication
└── Ready to scale up instantly

In disaster:
1. Scale up GCP to 100%
2. Redirect traffic via DNS/load balancer
3. Operational in <15 minutes

Best for: Business-critical ML services
```

#### Strategy 4: Multi-Region Active-Active (Highest cost, lowest RTO)

```
RPO: Near-zero
RTO: Seconds (automatic failover)
Cost: High ($$$$$$$$)

Implementation:
Both regions handle traffic simultaneously:
AWS US-East:          AWS US-West:
├── 50% traffic       ├── 50% traffic
├── Live data sync ←→ └── Live data sync

In disaster (US-East fails):
- US-West automatically handles 100% traffic
- No manual intervention needed
- Users may not notice outage

Best for: Mission-critical systems
```

---

## 6. Summary and Key Takeaways

### Core Concepts

1. **Multi-cloud** offers redundancy and flexibility
   - Best-of-breed: Use each cloud's strengths
   - Active-passive: Disaster recovery
   - Consider complexity vs benefits

2. **Cost optimization** is critical for ML
   - Right-size instances (analyze actual usage)
   - Auto-scale inference endpoints
   - Use spot instances for training
   - Schedule dev/test environments
   - Tier storage (S3 Standard → Glacier)

3. **FinOps** brings accountability
   - Tag all resources for cost allocation
   - Set budgets and alerts
   - Regular cost reviews with teams

4. **Disaster recovery** ensures business continuity
   - Define RPO/RTO targets
   - Choose DR strategy based on criticality
   - Test DR plan regularly

### Practical Skills Gained

✅ Design multi-cloud architectures
✅ Optimize ML workload costs (60-70% savings achievable)
✅ Implement FinOps practices (tagging, budgets)
✅ Plan disaster recovery strategies
✅ Right-size, auto-scale, and schedule resources

### Common Pitfalls to Avoid

❌ Running dev/test 24/7 (use scheduling)
❌ Over-provisioning "just in case" (right-size)
❌ Not using spot instances for training
❌ Storing all data in hot storage
❌ No cost tagging (can't track spending)
❌ No disaster recovery plan

### Next Steps

- **Analyze**: Review current cloud spending, identify top costs
- **Optimize**: Implement auto-scaling and scheduling
- **Tag**: Tag all resources for cost tracking
- **Test**: Run DR drill to validate recovery procedures

### Additional Resources

- [AWS Cost Optimization Best Practices](https://aws.amazon.com/pricing/cost-optimization/)
- [GCP Rightsizing Recommendations](https://cloud.google.com/compute/docs/instances/apply-sizing-recommendations-for-instances)
- [FinOps Foundation](https://www.finops.org/)
- [AWS Well-Architected Framework - Cost Optimization](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/)

---

**Congratulations!** You now understand how to build cost-effective, resilient multi-cloud ML infrastructure with proper financial governance and disaster recovery.

**Final Module Complete!**
