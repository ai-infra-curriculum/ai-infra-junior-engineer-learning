terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "ml-capstone/prod/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "tfstate-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "ml-capstone"
      Environment = "prod"
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source             = "../../modules/vpc"
  name               = "ml-capstone-prod"
  cidr_block         = "10.20.0.0/16"
  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]
  enable_nat_gateway = true
  single_nat_gateway = false
}

module "eks" {
  source             = "../../modules/eks"
  cluster_name       = "ml-capstone-prod"
  kubernetes_version = "1.30"
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids

  endpoint_public_access = false

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
      taints = [{
        key    = "workload"
        value  = "inference"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

module "rds" {
  source                  = "../../modules/rds"
  identifier              = "ml-capstone-prod"
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.private_subnet_ids
  allowed_cidrs           = [module.vpc.vpc_cidr_block]
  instance_class          = "db.m6g.large"
  allocated_storage       = 200
  max_allocated_storage   = 1000
  multi_az                = true
  backup_retention_period = 14
  deletion_protection     = true
}
