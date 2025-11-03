# Exercise 09: FinOps and Cost Optimization for ML Infrastructure

## Overview
Implement FinOps (Financial Operations) practices to optimize cloud costs for ML infrastructure. Learn to track spending, identify waste, implement cost allocation, and achieve 30%+ cost reduction while maintaining performance and reliability.

**Duration:** 3-4 hours
**Difficulty:** Advanced

## Learning Objectives
By completing this exercise, you will:
- Implement cloud cost visibility and tracking
- Create cost allocation tags for ML workloads
- Identify and eliminate cloud waste
- Optimize compute, storage, and network costs
- Implement automated cost controls
- Design chargebacks/showbacks for teams
- Balance cost optimization with performance

## Prerequisites
- AWS account with billing access (or Cost Explorer demo)
- Understanding of cloud pricing models
- Completed previous cloud exercises
- Basic knowledge of Kubernetes and autoscaling

## Scenario
Your **ML Platform** cloud bill has grown from $10K/month to $80K/month over 12 months. Leadership is concerned:
- No visibility into which teams/projects drive costs
- Unknown if costs are justified
- Suspicion of waste (idle resources, over-provisioning)
- No budget accountability

You're tasked with:
1. **Visibility**: Understand what drives costs
2. **Allocation**: Track costs by team/project
3. **Optimization**: Reduce waste by 30%
4. **Governance**: Implement controls to prevent overruns

## Tasks

### Task 1: Cost Visibility and Analysis

**TODO 1.1:** Analyze current spending patterns

```python
# analyze_costs.py
"""
Analyze AWS Cost Explorer data to understand spending.
"""

import boto3
from datetime import datetime, timedelta

def get_monthly_costs(start_date: str, end_date: str):
    """Get monthly costs from AWS Cost Explorer."""
    ce = boto3.client('ce')

    response = ce.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        GroupBy=[
            {'Type': 'DIMENSION', 'Key': 'SERVICE'},
        ]
    )

    # Parse results
    costs_by_service = {}
    for result in response['ResultsByTime']:
        month = result['TimePeriod']['Start']
        for group in result['Groups']:
            service = group['Keys'][0]
            cost = float(group['Metrics']['UnblendedCost']['Amount'])

            if service not in costs_by_service:
                costs_by_service[service] = {}
            costs_by_service[service][month] = cost

    return costs_by_service

def print_top_services(costs_by_service: dict, top_n: int = 10):
    """Print top N services by cost."""
    # Calculate total cost per service
    service_totals = {}
    for service, monthly_costs in costs_by_service.items():
        service_totals[service] = sum(monthly_costs.values())

    # Sort by total cost
    sorted_services = sorted(
        service_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    print(f"=== Top {top_n} Services by Cost ===\n")
    total_cost = sum(service_totals.values())

    for i, (service, cost) in enumerate(sorted_services[:top_n], 1):
        percentage = (cost / total_cost) * 100
        print(f"{i}. {service}")
        print(f"   Cost: ${cost:,.2f} ({percentage:.1f}%)\n")

# TODO: Run analysis
start = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
end = datetime.now().strftime('%Y-%m-%d')

costs = get_monthly_costs(start, end)
print_top_services(costs)
```

**TODO 1.2:** Identify cost anomalies and trends

```python
# detect_anomalies.py
"""
Detect cost anomalies and unusual spending patterns.
"""

def detect_cost_spikes(daily_costs: dict, threshold: float = 1.5):
    """
    Detect days with unusually high costs.

    Args:
        daily_costs: Dict of {date: cost}
        threshold: Spike detection threshold (1.5 = 50% above average)
    """
    costs = list(daily_costs.values())
    avg_cost = sum(costs) / len(costs)

    spikes = []
    for date, cost in daily_costs.items():
        if cost > (avg_cost * threshold):
            spike_percentage = ((cost / avg_cost) - 1) * 100
            spikes.append({
                "date": date,
                "cost": cost,
                "avg_cost": avg_cost,
                "spike_percentage": spike_percentage
            })

    return spikes

def analyze_growth_rate(monthly_costs: list):
    """Calculate month-over-month growth rate."""
    if len(monthly_costs) < 2:
        return None

    growth_rates = []
    for i in range(1, len(monthly_costs)):
        prev_month = monthly_costs[i-1]
        curr_month = monthly_costs[i]

        growth = ((curr_month - prev_month) / prev_month) * 100
        growth_rates.append(growth)

    avg_growth = sum(growth_rates) / len(growth_rates)

    return {
        "average_growth_rate": avg_growth,
        "max_growth": max(growth_rates),
        "min_growth": min(growth_rates),
        "months_analyzed": len(growth_rates)
    }

# TODO: Example usage
daily_costs_example = {
    "2024-01-01": 2500,
    "2024-01-02": 2600,
    "2024-01-03": 4500,  # Spike
    "2024-01-04": 2400,
    "2024-01-05": 2700
}

spikes = detect_cost_spikes(daily_costs_example)
print("=== Cost Spikes Detected ===\n")
for spike in spikes:
    print(f"Date: {spike['date']}")
    print(f"Cost: ${spike['cost']:,.2f}")
    print(f"Average: ${spike['avg_cost']:,.2f}")
    print(f"Spike: +{spike['spike_percentage']:.1f}%\n")
```

### Task 2: Cost Allocation and Tagging

**TODO 2.1:** Design tagging strategy for ML workloads

```yaml
# tagging-strategy.yaml
tagging_strategy:
  purpose: "Enable cost allocation and chargeback"

  required_tags:
    environment:
      values: ["prod", "staging", "dev", "research"]
      purpose: "Separate production from non-production costs"

    team:
      values: ["ml-platform", "data-science", "ml-research", "ml-ops"]
      purpose: "Chargeback to teams"

    project:
      values: ["fraud-detection", "recommendations", "image-classifier"]
      purpose: "Track costs by ML project"

    cost_center:
      values: ["cc-1001", "cc-1002", "cc-1003"]
      purpose: "Map to finance cost centers"

    owner:
      values: ["email@company.com"]
      purpose: "Contact for cost inquiries"

  optional_tags:
    workload_type:
      values: ["training", "inference", "batch", "feature-store"]
      purpose: "Understand cost drivers by workload"

    model:
      values: ["fraud-detector-v2", "recommender-v3"]
      purpose: "Track costs per model version"

    experiment_id:
      values: ["exp-12345"]
      purpose: "Track training experiment costs"

  enforcement:
    method: "AWS Config Rules + Lambda"
    action: "Block untagged resource creation"
    grace_period: "24 hours to add tags"
```

**TODO 2.2:** Implement tagging automation

```python
# tag_resources.py
"""
Automated tagging for ML infrastructure.
"""

import boto3

def tag_ec2_instances(filters: dict, tags: dict):
    """
    Tag EC2 instances matching filters.

    Args:
        filters: Dict of filter criteria
        tags: Dict of tags to apply
    """
    ec2 = boto3.client('ec2')

    # Find instances
    response = ec2.describe_instances(Filters=filters)

    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    if not instance_ids:
        print("No instances found matching filters")
        return

    # Apply tags
    ec2.create_tags(
        Resources=instance_ids,
        Tags=[{'Key': k, 'Value': v} for k, v in tags.items()]
    )

    print(f"✓ Tagged {len(instance_ids)} instances")
    for iid in instance_ids:
        print(f"  - {iid}")

def enforce_tagging_policy():
    """
    Check for untagged resources and send alerts.
    """
    ec2 = boto3.client('ec2')
    required_tags = ['environment', 'team', 'project', 'owner']

    # Find instances
    response = ec2.describe_instances()

    untagged = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

            missing_tags = [tag for tag in required_tags if tag not in tags]
            if missing_tags:
                untagged.append({
                    'instance_id': instance_id,
                    'missing_tags': missing_tags
                })

    if untagged:
        print(f"⚠️  Found {len(untagged)} instances with missing tags:\n")
        for item in untagged:
            print(f"Instance: {item['instance_id']}")
            print(f"Missing: {', '.join(item['missing_tags'])}\n")

        # TODO: Send alert to Slack/email
        # send_alert(untagged)
    else:
        print("✓ All instances properly tagged")

# TODO: Example usage
tag_ec2_instances(
    filters=[
        {'Name': 'tag:project', 'Values': ['fraud-detection']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ],
    tags={
        'environment': 'prod',
        'team': 'ml-platform',
        'cost_center': 'cc-1001',
        'owner': 'ml-team@company.com'
    }
)

enforce_tagging_policy()
```

### Task 3: Identify and Eliminate Waste

**TODO 3.1:** Find idle and underutilized resources

```python
# find_waste.py
"""
Identify wasted cloud resources.
"""

import boto3
from datetime import datetime, timedelta

def find_idle_ec2_instances(threshold_cpu: float = 5.0, days: int = 7):
    """
    Find EC2 instances with low CPU utilization.

    Args:
        threshold_cpu: Max average CPU % to consider idle
        days: Days to analyze
    """
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')

    # Get all running instances
    response = ec2.describe_instances(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    )

    idle_instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']

            # Get CPU metrics
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,  # 1 hour
                Statistics=['Average']
            )

            if not metrics['Datapoints']:
                continue

            avg_cpu = sum(d['Average'] for d in metrics['Datapoints']) / len(metrics['Datapoints'])

            if avg_cpu < threshold_cpu:
                # Calculate monthly cost
                cost_per_hour = {
                    't3.medium': 0.0416,
                    't3.large': 0.0832,
                    'm5.xlarge': 0.192,
                    'p3.2xlarge': 3.06
                }.get(instance_type, 0.10)

                monthly_cost = cost_per_hour * 24 * 30

                idle_instances.append({
                    'instance_id': instance_id,
                    'instance_type': instance_type,
                    'avg_cpu': avg_cpu,
                    'monthly_cost': monthly_cost,
                    'potential_savings': monthly_cost
                })

    return idle_instances

def find_unattached_ebs_volumes():
    """Find EBS volumes not attached to any instance."""
    ec2 = boto3.client('ec2')

    response = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )

    unattached = []
    for volume in response['Volumes']:
        size = volume['Size']
        volume_type = volume['VolumeType']

        # Cost per GB-month
        cost_per_gb = {
            'gp2': 0.10,
            'gp3': 0.08,
            'io1': 0.125,
            'io2': 0.125,
            'st1': 0.045,
            'sc1': 0.015
        }.get(volume_type, 0.10)

        monthly_cost = size * cost_per_gb

        unattached.append({
            'volume_id': volume['VolumeId'],
            'size_gb': size,
            'volume_type': volume_type,
            'monthly_cost': monthly_cost,
            'potential_savings': monthly_cost
        })

    return unattached

# TODO: Run waste detection
print("=== Waste Detection Report ===\n")

print("[1] Idle EC2 Instances:")
idle = find_idle_ec2_instances()
if idle:
    total_savings = sum(i['potential_savings'] for i in idle)
    print(f"Found {len(idle)} idle instances")
    print(f"Potential monthly savings: ${total_savings:,.2f}\n")

    for instance in idle[:5]:  # Show top 5
        print(f"  {instance['instance_id']} ({instance['instance_type']})")
        print(f"  Avg CPU: {instance['avg_cpu']:.1f}%")
        print(f"  Monthly cost: ${instance['monthly_cost']:.2f}\n")
else:
    print("No idle instances found\n")

print("[2] Unattached EBS Volumes:")
unattached = find_unattached_ebs_volumes()
if unattached:
    total_savings = sum(v['potential_savings'] for v in unattached)
    print(f"Found {len(unattached)} unattached volumes")
    print(f"Potential monthly savings: ${total_savings:,.2f}\n")
else:
    print("No unattached volumes found\n")
```

**TODO 3.2:** Optimize storage costs

```python
# optimize_storage.py
"""
Storage cost optimization strategies.
"""

def recommend_s3_lifecycle_policies(bucket_usage: dict):
    """
    Recommend S3 lifecycle policies based on access patterns.

    Args:
        bucket_usage: Dict with bucket access statistics
    """
    recommendations = []

    for prefix, stats in bucket_usage.items():
        days_since_access = stats['days_since_last_access']
        size_gb = stats['size_gb']

        # Standard -> Intelligent-Tiering
        if days_since_access > 30:
            savings_per_gb = 0.023 - 0.0125  # Standard to IA
            potential_savings = size_gb * savings_per_gb

            recommendations.append({
                'prefix': prefix,
                'action': 'Move to S3 Intelligent-Tiering',
                'reason': f'Not accessed in {days_since_access} days',
                'monthly_savings': potential_savings
            })

        # Move to Glacier for archives
        if days_since_access > 180:
            savings_per_gb = 0.023 - 0.004  # Standard to Glacier
            potential_savings = size_gb * savings_per_gb

            recommendations.append({
                'prefix': prefix,
                'action': 'Move to S3 Glacier',
                'reason': f'Not accessed in {days_since_access} days (archive)',
                'monthly_savings': potential_savings
            })

    return recommendations

# TODO: Example usage
bucket_usage = {
    'ml-models/production/': {
        'days_since_last_access': 5,
        'size_gb': 1000
    },
    'ml-datasets/raw/': {
        'days_since_last_access': 90,
        'size_gb': 5000
    },
    'ml-experiments/old/': {
        'days_since_last_access': 365,
        'size_gb': 10000
    }
}

recs = recommend_s3_lifecycle_policies(bucket_usage)
print("=== S3 Storage Optimization ===\n")

total_savings = sum(r['monthly_savings'] for r in recs)
for rec in recs:
    print(f"Prefix: {rec['prefix']}")
    print(f"Action: {rec['action']}")
    print(f"Reason: {rec['reason']}")
    print(f"Savings: ${rec['monthly_savings']:,.2f}/month\n")

print(f"Total potential savings: ${total_savings:,.2f}/month")
```

### Task 4: Right-Sizing and Reserved Capacity

**TODO 4.1:** Right-size EC2 instances

```python
# rightsize_instances.py
"""
Recommend right-sized instances based on actual usage.
"""

def recommend_instance_size(current_type: str, avg_cpu: float, avg_memory: float):
    """
    Recommend smaller instance if overprovisioned.

    Args:
        current_type: Current instance type
        avg_cpu: Average CPU utilization %
        avg_memory: Average memory utilization %

    Returns:
        Dict with recommendation
    """
    # Instance family mappings
    instance_families = {
        't3': ['nano', 'micro', 'small', 'medium', 'large', 'xlarge', '2xlarge'],
        'm5': ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge'],
        'c5': ['large', 'xlarge', '2xlarge', '4xlarge', '9xlarge'],
        'r5': ['large', 'xlarge', '2xlarge', '4xlarge', '8xlarge']
    }

    family = current_type.split('.')[0]
    size = current_type.split('.')[1]

    # If both CPU and memory below 30%, recommend downsizing
    if avg_cpu < 30 and avg_memory < 30:
        sizes = instance_families.get(family, [])
        current_idx = sizes.index(size) if size in sizes else -1

        if current_idx > 0:  # Not already smallest
            recommended_size = sizes[current_idx - 1]
            recommended_type = f"{family}.{recommended_size}"

            # Calculate savings (rough estimate)
            size_multiplier = {
                'nano': 0.5, 'micro': 1, 'small': 2, 'medium': 4,
                'large': 8, 'xlarge': 16, '2xlarge': 32, '4xlarge': 64
            }

            current_cost = size_multiplier.get(size, 16) * 0.05  # $0.05/unit
            recommended_cost = size_multiplier.get(recommended_size, 8) * 0.05
            monthly_savings = (current_cost - recommended_cost) * 24 * 30

            return {
                'action': 'downsize',
                'current': current_type,
                'recommended': recommended_type,
                'reason': f'Low utilization (CPU: {avg_cpu:.1f}%, Mem: {avg_memory:.1f}%)',
                'monthly_savings': monthly_savings
            }

    return {'action': 'no_change', 'current': current_type}

# TODO: Example usage
instances_to_check = [
    {'type': 't3.2xlarge', 'avg_cpu': 15, 'avg_memory': 20},
    {'type': 'm5.xlarge', 'avg_cpu': 8, 'avg_memory': 12},
    {'type': 'c5.4xlarge', 'avg_cpu': 65, 'avg_memory': 55}
]

print("=== Instance Right-Sizing Recommendations ===\n")
total_savings = 0

for instance in instances_to_check:
    rec = recommend_instance_size(
        instance['type'],
        instance['avg_cpu'],
        instance['avg_memory']
    )

    if rec['action'] == 'downsize':
        print(f"Current: {rec['current']}")
        print(f"Recommended: {rec['recommended']}")
        print(f"Reason: {rec['reason']}")
        print(f"Savings: ${rec['monthly_savings']:.2f}/month\n")
        total_savings += rec['monthly_savings']

print(f"Total potential savings: ${total_savings:,.2f}/month")
```

**TODO 4.2:** Reserved Instance and Savings Plan analysis

```python
# reserved_capacity.py
"""
Analyze Reserved Instance and Savings Plan opportunities.
"""

def calculate_ri_savings(on_demand_hours: float, instance_type: str):
    """
    Calculate savings from Reserved Instances vs On-Demand.

    Args:
        on_demand_hours: Hours per month instance runs
        instance_type: EC2 instance type

    Returns:
        Dict with savings analysis
    """
    # Example pricing (actual varies by region)
    pricing = {
        'm5.xlarge': {
            'on_demand': 0.192,
            'ri_1yr_no_upfront': 0.123,
            'ri_1yr_all_upfront': 0.116,
            'ri_3yr_all_upfront': 0.077
        },
        'p3.2xlarge': {
            'on_demand': 3.06,
            'ri_1yr_no_upfront': 1.96,
            'ri_1yr_all_upfront': 1.87,
            'ri_3yr_all_upfront': 1.24
        }
    }

    if instance_type not in pricing:
        return None

    prices = pricing[instance_type]
    monthly_hours = on_demand_hours

    on_demand_monthly = monthly_hours * prices['on_demand']
    ri_1yr_monthly = monthly_hours * prices['ri_1yr_no_upfront']
    ri_3yr_monthly = monthly_hours * prices['ri_3yr_all_upfront']

    return {
        'instance_type': instance_type,
        'monthly_hours': monthly_hours,
        'on_demand_monthly': on_demand_monthly,
        'ri_1yr_monthly': ri_1yr_monthly,
        'ri_3yr_monthly': ri_3yr_monthly,
        'savings_1yr': on_demand_monthly - ri_1yr_monthly,
        'savings_3yr': on_demand_monthly - ri_3yr_monthly,
        'savings_pct_1yr': ((on_demand_monthly - ri_1yr_monthly) / on_demand_monthly) * 100,
        'savings_pct_3yr': ((on_demand_monthly - ri_3yr_monthly) / on_demand_monthly) * 100
    }

# TODO: Analyze workloads
print("=== Reserved Instance Analysis ===\n")

# Example: 10 m5.xlarge instances running 24/7
workload = {
    'instance_type': 'm5.xlarge',
    'num_instances': 10,
    'hours_per_month': 730  # 24*365/12
}

analysis = calculate_ri_savings(
    workload['hours_per_month'],
    workload['instance_type']
)

print(f"Workload: {workload['num_instances']}x {workload['instance_type']}")
print(f"Usage: {workload['hours_per_month']} hours/month\n")

print(f"On-Demand Cost: ${analysis['on_demand_monthly'] * workload['num_instances']:,.2f}/month")
print(f"1-Year RI Cost: ${analysis['ri_1yr_monthly'] * workload['num_instances']:,.2f}/month")
print(f"3-Year RI Cost: ${analysis['ri_3yr_monthly'] * workload['num_instances']:,.2f}/month\n")

print(f"1-Year Savings: ${analysis['savings_1yr'] * workload['num_instances']:,.2f}/month ({analysis['savings_pct_1yr']:.1f}%)")
print(f"3-Year Savings: ${analysis['savings_3yr'] * workload['num_instances']:,.2f}/month ({analysis['savings_pct_3yr']:.1f}%)")
```

### Task 5: Automated Cost Controls

**TODO 5.1:** Implement budget alerts

```python
# budget_alerts.py
"""
Set up AWS Budgets with alerts.
"""

import boto3

def create_monthly_budget(
    budget_name: str,
    amount: float,
    email: str,
    alert_thresholds: list = [80, 100, 120]
):
    """
    Create AWS Budget with SNS alerts.

    Args:
        budget_name: Name for the budget
        amount: Monthly budget amount in USD
        email: Email for alerts
        alert_thresholds: List of % thresholds for alerts
    """
    budgets = boto3.client('budgets')
    account_id = boto3.client('sts').get_caller_identity()['Account']

    # Create budget
    budget = {
        'BudgetName': budget_name,
        'BudgetLimit': {
            'Amount': str(amount),
            'Unit': 'USD'
        },
        'TimeUnit': 'MONTHLY',
        'BudgetType': 'COST',
        'CostFilters': {}
    }

    # Create notifications
    notifications = []
    for threshold in alert_thresholds:
        notifications.append({
            'Notification': {
                'NotificationType': 'ACTUAL',
                'ComparisonOperator': 'GREATER_THAN',
                'Threshold': threshold,
                'ThresholdType': 'PERCENTAGE'
            },
            'Subscribers': [{
                'SubscriptionType': 'EMAIL',
                'Address': email
            }]
        })

    # Create budget
    response = budgets.create_budget(
        AccountId=account_id,
        Budget=budget,
        NotificationsWithSubscribers=notifications
    )

    print(f"✓ Created budget: {budget_name}")
    print(f"  Amount: ${amount}/month")
    print(f"  Alerts: {alert_thresholds}")

# TODO: Create budgets for teams
create_monthly_budget(
    budget_name='ml-platform-team-budget',
    amount=20000,
    email='ml-platform@company.com',
    alert_thresholds=[75, 90, 100, 110]
)

create_monthly_budget(
    budget_name='ml-research-team-budget',
    amount=15000,
    email='ml-research@company.com',
    alert_thresholds=[80, 100, 120]
)
```

**TODO 5.2:** Automated shutdown of non-production resources

```python
# auto_shutdown.py
"""
Automatically shut down non-production resources outside business hours.
"""

import boto3
from datetime import datetime

def should_shutdown_now():
    """Determine if resources should be shut down."""
    now = datetime.now()

    # Business hours: Mon-Fri, 8am-8pm
    is_weekday = now.weekday() < 5  # 0-4 = Mon-Fri
    is_business_hours = 8 <= now.hour < 20

    return not (is_weekday and is_business_hours)

def shutdown_dev_instances():
    """Shut down dev/staging instances during off-hours."""
    if not should_shutdown_now():
        print("✓ Business hours - no shutdown")
        return

    ec2 = boto3.client('ec2')

    # Find dev/staging instances
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:environment', 'Values': ['dev', 'staging']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )

    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    if not instance_ids:
        print("No dev/staging instances running")
        return

    # Stop instances
    ec2.stop_instances(InstanceIds=instance_ids)

    print(f"✓ Stopped {len(instance_ids)} dev/staging instances")
    for iid in instance_ids:
        print(f"  - {iid}")

# TODO: Schedule this to run hourly via Lambda + EventBridge
shutdown_dev_instances()
```

### Task 6: FinOps Reporting Dashboard

**TODO 6.1:** Create cost dashboard

```python
# cost_dashboard.py
"""
Generate FinOps dashboard showing key metrics.
"""

import matplotlib.pyplot as plt
import pandas as pd

def create_finops_dashboard(monthly_data: dict):
    """
    Create visual FinOps dashboard.

    Args:
        monthly_data: Dict with monthly cost data
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('ML Platform FinOps Dashboard', fontsize=16)

    # 1. Monthly cost trend
    months = list(monthly_data['total_cost'].keys())
    costs = list(monthly_data['total_cost'].values())

    axes[0, 0].plot(months, costs, marker='o')
    axes[0, 0].set_title('Monthly Cost Trend')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Cost ($)')
    axes[0, 0].grid(True)

    # 2. Cost by service (pie chart)
    services = monthly_data['by_service']
    axes[0, 1].pie(services.values(), labels=services.keys(), autopct='%1.1f%%')
    axes[0, 1].set_title('Cost Distribution by Service')

    # 3. Cost by team (bar chart)
    teams = monthly_data['by_team']
    axes[1, 0].bar(teams.keys(), teams.values())
    axes[1, 0].set_title('Cost by Team')
    axes[1, 0].set_xlabel('Team')
    axes[1, 0].set_ylabel('Cost ($)')

    # 4. Savings from optimization
    savings = monthly_data['savings']
    categories = list(savings.keys())
    amounts = list(savings.values())

    axes[1, 1].barh(categories, amounts, color='green')
    axes[1, 1].set_title('Monthly Savings from Optimization')
    axes[1, 1].set_xlabel('Savings ($)')

    plt.tight_layout()
    plt.savefig('finops_dashboard.png')
    print("✓ Dashboard saved to finops_dashboard.png")

# TODO: Generate dashboard
monthly_data = {
    'total_cost': {
        'Jan': 65000,
        'Feb': 72000,
        'Mar': 68000,
        'Apr': 59000,  # After optimization
        'May': 57000,
        'Jun': 55000
    },
    'by_service': {
        'EC2': 28000,
        'S3': 8000,
        'SageMaker': 12000,
        'RDS': 4000,
        'Other': 3000
    },
    'by_team': {
        'ML Platform': 25000,
        'Data Science': 18000,
        'ML Research': 12000
    },
    'savings': {
        'Right-sizing': 5000,
        'Reserved capacity': 8000,
        'Auto-shutdown': 2000,
        'Storage optimization': 3000
    }
}

create_finops_dashboard(monthly_data)
```

## Deliverables

Submit a repository with:

1. **Cost Analysis Report** (`COST_ANALYSIS.md`)
   - Current spending breakdown
   - Cost trends and anomalies
   - Top cost drivers

2. **Tagging Strategy** (`TAGGING_STRATEGY.md`)
   - Required tags
   - Enforcement mechanism
   - Tag compliance report

3. **Optimization Plan** (`OPTIMIZATION_PLAN.md`)
   - Waste identification results
   - Right-sizing recommendations
   - Reserved capacity analysis
   - Projected savings (30%+ target)

4. **Python Scripts**
   - `analyze_costs.py` - Cost analysis
   - `find_waste.py` - Waste detection
   - `rightsize_instances.py` - Right-sizing
   - `budget_alerts.py` - Budget setup
   - `cost_dashboard.py` - Reporting

5. **FinOps Dashboard**
   - Grafana or custom dashboard
   - Key metrics tracked
   - Team cost attribution

## Success Criteria

- [ ] Complete cost visibility by service, team, project
- [ ] Tagging strategy documented and partially implemented
- [ ] Identified $20K+ in potential monthly savings
- [ ] Budget alerts configured for major cost centers
- [ ] Automated controls prevent runaway costs
- [ ] Right-sizing recommendations for 10+ instances
- [ ] Storage optimization plan with S3 lifecycle policies
- [ ] Reserved capacity analysis with ROI calculation
- [ ] FinOps dashboard showing cost trends
- [ ] Achieved or planned 30%+ cost reduction

## Bonus Challenges

1. **Spot Instance Strategy**: Implement fault-tolerant workloads on spot
2. **Chargeback System**: Build full chargeback/showback for teams
3. **Cost Forecasting**: ML model to predict next month's costs
4. **Automated Remediation**: Lambda functions that automatically fix waste
5. **Cross-Cloud Cost Comparison**: Compare costs if workloads moved to GCP/Azure
6. **Carbon Footprint**: Calculate and optimize carbon emissions

## Resources

- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)
- [FinOps Foundation](https://www.finops.org/)
- [Cloud Cost Optimization Best Practices](https://aws.amazon.com/economics/)
- [Kubecost for Kubernetes](https://www.kubecost.com/)

## Evaluation Rubric

| Criteria | Points |
|----------|--------|
| Cost analysis and visibility | 15 |
| Tagging strategy implementation | 15 |
| Waste identification | 20 |
| Right-sizing and reserved capacity | 20 |
| Automated controls | 15 |
| Documentation and reporting | 10 |
| Projected cost savings | 5 |

**Total: 100 points**
