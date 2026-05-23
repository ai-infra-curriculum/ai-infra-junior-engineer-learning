variable "role_name" {
  type = string
}

variable "oidc_provider_arn" {
  type        = string
  description = "ARN of the cluster's IAM OIDC provider (created separately, once per cluster)."
}

variable "oidc_issuer_url" {
  type        = string
  description = "Issuer URL from aws_eks_cluster.identity[0].oidc[0].issuer."
}

variable "namespace" {
  type = string
}

variable "service_account_name" {
  type = string
}

variable "managed_policy_arns" {
  type    = list(string)
  default = []
}

variable "inline_policy_json" {
  type        = string
  default     = ""
  description = "Optional inline policy. Pass jsonencode(...) result."
}

variable "tags" {
  type    = map(string)
  default = {}
}
