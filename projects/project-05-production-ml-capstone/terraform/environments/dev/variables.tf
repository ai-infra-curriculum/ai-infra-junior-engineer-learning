variable "region" {
  type    = string
  default = "us-west-2"
}

variable "dev_access_cidrs" {
  type        = list(string)
  description = "Office / VPN CIDRs allowed to reach the EKS API server in dev."
  default     = []
}
