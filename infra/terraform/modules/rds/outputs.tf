output "db_endpoint" {
  value = aws_db_instance.postgres.address
}

output "secrets_manager_secret_arn" {
  value = aws_secretsmanager_secret.app.arn
}
