output "endpoint" {
  value = aws_db_instance.this.endpoint
}

output "port" {
  value = aws_db_instance.this.port
}

output "db_name" {
  value = aws_db_instance.this.db_name
}

output "master_password_ssm_param" {
  value       = "/${var.identifier}/master_password"
  description = "Store the random password into SSM Parameter Store via aws_ssm_parameter in the root module."
}

output "security_group_id" {
  value = aws_security_group.rds.id
}

output "master_password_secret" {
  value       = nonsensitive("set me via the root module")
  description = "Do not output the actual secret. Wire it into a Secret in EKS via external-secrets or AWS Secrets Manager."
}
