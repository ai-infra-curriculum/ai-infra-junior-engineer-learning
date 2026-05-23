terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "ml-capstone/staging/terraform.tfstate"
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
      Environment = "staging"
      ManagedBy   = "Terraform"
    }
  }
}

# Staging mirrors prod's topology (multi-AZ, multi-NAT) at smaller scale.
module "vpc" {
  source             = "../../modules/vpc"
  name               = "ml-capstone-staging"
  cidr_block         = "10.15.0.0/16"
  availability_zones = ["${var.region}a", "${var.region}b", "${var.region}c"]
  enable_nat_gateway = true
  single_nat_gateway = false
}

module "eks" {
  source             = "../../modules/eks"
  cluster_name       = "ml-capstone-staging"
  kubernetes_version = "1.30"
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids

  endpoint_public_access = false

  node_groups = {
    general = {
      instance_types = ["m6i.large"]
      desired_size   = 2
      min_size       = 2
      max_size       = 6
    }
    inference = {
      instance_types = ["c6i.large"]
      desired_size   = 1
      min_size       = 1
      max_size       = 4
      labels         = { workload = "inference" }
    }
  }
}

module "rds" {
  source                  = "../../modules/rds"
  identifier              = "ml-capstone-staging"
  vpc_id                  = module.vpc.vpc_id
  subnet_ids              = module.vpc.private_subnet_ids
  allowed_cidrs           = [module.vpc.vpc_cidr_block]
  instance_class          = "db.t4g.medium"
  allocated_storage       = 50
  max_allocated_storage   = 200
  multi_az                = true
  backup_retention_period = 7
  deletion_protection     = true
}
