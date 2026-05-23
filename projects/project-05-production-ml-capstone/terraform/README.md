# Terraform — Project 05 Capstone

This is the Infrastructure-as-Code layer for the Project 05 capstone. It provisions everything below the Kubernetes deployments: network, cluster, managed databases, IAM, secrets.

## Layout

```
terraform/
├── modules/                    # Reusable composable modules
│   ├── vpc/                    # VPC, subnets, route tables, NAT
│   ├── eks/                    # EKS cluster + managed node groups
│   ├── rds/                    # PostgreSQL for application data
│   └── iam/                    # IRSA roles, KMS keys
└── environments/               # One root module per environment
    ├── dev/
    ├── staging/
    └── prod/
```

Each environment is a separate Terraform state, isolated by an S3 backend and DynamoDB lock table.

## Why three environments

- **dev** — small, ephemeral. Single-AZ. No HA. Frequent destroy/recreate.
- **staging** — production-shaped. Multi-AZ. Real but scaled-down resources. Where releases land before prod.
- **prod** — full HA. Locked-down state file. Changes go through CODEOWNERS review.

## Module usage example

```hcl
# environments/prod/main.tf
module "vpc" {
  source             = "../../modules/vpc"
  name               = "ml-prod"
  cidr_block         = "10.20.0.0/16"
  availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]
  enable_nat_gateway = true
  single_nat_gateway = false
}

module "eks" {
  source             = "../../modules/eks"
  cluster_name       = "ml-prod"
  kubernetes_version = "1.30"
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids

  node_groups = {
    general = {
      instance_types = ["m6i.large"]
      desired_size   = 3
      min_size       = 3
      max_size       = 10
    }
    inference = {
      instance_types = ["c6i.xlarge"]
      desired_size   = 2
      min_size       = 2
      max_size       = 12
      labels         = { workload = "inference" }
      taints         = [{ key = "workload", value = "inference", effect = "NO_SCHEDULE" }]
    }
  }
}
```

## State backend

Use a per-environment S3 backend with DynamoDB locking. Never commit `*.tfstate`.

```hcl
terraform {
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "ml/prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}
```

## Standard flow

```bash
cd terraform/environments/dev
terraform init
terraform plan -out=plan.tfplan
terraform apply plan.tfplan
```

Never run `terraform apply` without first reviewing a `terraform plan`. CI should enforce plan-on-PR, apply-on-merge.

## Common gotchas

- **EKS cluster updates take 20+ minutes.** Don't block CI on `terraform apply`; run it on a longer-timeout pipeline.
- **Don't destroy state-bearing resources** (RDS, S3 buckets) from `terraform destroy`. Use `lifecycle { prevent_destroy = true }`.
- **Secrets in state.** The Terraform state file contains secret values. Encrypt at rest, restrict access by IAM, never download to local disk on a shared workstation.
