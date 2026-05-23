terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "ml-capstone/dev/terraform.tfstate"
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
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}

# Dev is single-AZ, single-NAT, smaller instances.
module "vpc" {
  source             = "../../modules/vpc"
  name               = "ml-capstone-dev"
  cidr_block         = "10.10.0.0/16"
  availability_zones = ["${var.region}a", "${var.region}b"]
  enable_nat_gateway = true
  single_nat_gateway = true
}

module "eks" {
  source             = "../../modules/eks"
  cluster_name       = "ml-capstone-dev"
  kubernetes_version = "1.30"
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids

  endpoint_public_access = true
  public_access_cidrs    = var.dev_access_cidrs

  node_groups = {
    general = {
      instance_types = ["t3.large"]
      desired_size   = 2
      min_size       = 1
      max_size       = 4
    }
  }
}

module "rds" {
  source                = "../../modules/rds"
  identifier            = "ml-capstone-dev"
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_subnet_ids
  allowed_cidrs         = [module.vpc.vpc_cidr_block]
  instance_class        = "db.t4g.small"
  allocated_storage     = 20
  max_allocated_storage = 100
  multi_az              = false
  backup_retention_period = 1
  deletion_protection   = false
}
