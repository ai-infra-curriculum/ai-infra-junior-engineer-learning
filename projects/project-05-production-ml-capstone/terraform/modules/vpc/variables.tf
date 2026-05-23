variable "name" {
  type        = string
  description = "VPC name (also tagged as Project)."
}

variable "cidr_block" {
  type        = string
  description = "CIDR block for the VPC, e.g. 10.20.0.0/16."
}

variable "availability_zones" {
  type        = list(string)
  description = "AZs to span. Each AZ gets one public and one private subnet."
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Whether private subnets should have egress via NAT Gateway."
  default     = true
}

variable "single_nat_gateway" {
  type        = bool
  description = "Use one NAT for all AZs. Cheaper for dev; not recommended for prod."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Extra tags merged into every resource."
  default     = {}
}
