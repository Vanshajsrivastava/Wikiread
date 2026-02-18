output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "db_endpoint" {
  value = aws_db_instance.postgres.address
}

output "secrets_manager_secret_arn" {
  value = aws_secretsmanager_secret.app.arn
}

output "app_pipeline_name" {
  value = aws_codepipeline.app.name
}

output "infra_pipeline_name" {
  value = aws_codepipeline.infra.name
}
