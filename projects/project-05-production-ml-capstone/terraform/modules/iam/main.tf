terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0" }
  }
}

# IRSA (IAM Role for Service Account) for the model-api workload.
#
# The OIDC provider for the EKS cluster must already exist. The role lets pods
# annotated with eks.amazonaws.com/role-arn = <role_arn> assume this role
# via a service account token, no long-lived AWS credentials in pods.

data "aws_iam_policy_document" "assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [var.oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_issuer_url, "https://", "")}:sub"
      values   = ["system:serviceaccount:${var.namespace}:${var.service_account_name}"]
    }
    condition {
      test     = "StringEquals"
      variable = "${replace(var.oidc_issuer_url, "https://", "")}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "workload" {
  name               = "${var.role_name}"
  assume_role_policy = data.aws_iam_policy_document.assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy" "workload" {
  count = length(var.inline_policy_json) > 0 ? 1 : 0
  name  = "${var.role_name}-inline"
  role  = aws_iam_role.workload.id
  policy = var.inline_policy_json
}

resource "aws_iam_role_policy_attachment" "workload" {
  for_each   = toset(var.managed_policy_arns)
  role       = aws_iam_role.workload.name
  policy_arn = each.value
}
