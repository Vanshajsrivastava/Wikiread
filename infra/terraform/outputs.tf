output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "db_endpoint" {
  value = module.rds.db_endpoint
}

output "secrets_manager_secret_arn" {
  value = module.rds.secrets_manager_secret_arn
}

output "app_pipeline_name" {
  value = aws_codepipeline.app.name
}

output "infra_pipeline_name" {
  value = aws_codepipeline.infra.name
}
