output "db_address" {
  value = aws_db_instance.main.address
}

output "shared_secret_arn" {
  description = "ARN del secret compartido con db_url y jwt_secret"
  value       = aws_secretsmanager_secret.shared.arn
}
