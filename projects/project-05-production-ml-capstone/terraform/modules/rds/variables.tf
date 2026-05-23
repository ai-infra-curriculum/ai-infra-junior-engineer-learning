variable "identifier" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs. Must span at least two AZs for multi_az."
}

variable "allowed_cidrs" {
  type        = list(string)
  description = "CIDRs allowed to reach the database on 5432 (typically EKS pod CIDR)."
}

variable "engine_version" {
  type    = string
  default = "15.5"
}

variable "instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "allocated_storage" {
  type    = number
  default = 100
}

variable "max_allocated_storage" {
  type    = number
  default = 500
}

variable "db_name" {
  type    = string
  default = "ml"
}

variable "master_username" {
  type    = string
  default = "ml_admin"
}

variable "multi_az" {
  type    = bool
  default = true
}

variable "backup_retention_period" {
  type    = number
  default = 14
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
