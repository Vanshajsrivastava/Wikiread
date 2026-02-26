resource "aws_codebuild_project" "app_build" {
  name         = "${local.name}-app-build"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = true

    environment_variable {
      name  = "ECR_REPOSITORY_URL"
      value = aws_ecr_repository.app.repository_url
    }

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "ci/buildspec.app-build.yml"
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "app_deploy" {
  name         = "${local.name}-app-deploy"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "EKS_CLUSTER_NAME"
      value = module.eks.cluster_name
    }

    environment_variable {
      name  = "APP_SECRET_ARN"
      value = module.rds.secrets_manager_secret_arn
    }

    environment_variable {
      name  = "GIT_REPO_URL"
      value = "https://github.com/${var.repo_owner}/${var.repo_name}.git"
    }

    environment_variable {
      name  = "GIT_TARGET_REVISION"
      value = var.repo_branch
    }

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "ci/buildspec.app-deploy.yml"
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "infra_plan" {
  name         = "${local.name}-infra-plan"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "TF_PLAN_BUCKET"
      value = aws_s3_bucket.tf_plan_bucket.bucket
    }

    environment_variable {
      name  = "APPROVAL_SNS_TOPIC_ARN"
      value = aws_sns_topic.infra_approvals.arn
    }

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "TF_VAR_repo_owner"
      value = var.repo_owner
    }

    environment_variable {
      name  = "TF_VAR_repo_name"
      value = var.repo_name
    }

    environment_variable {
      name  = "TF_VAR_repo_branch"
      value = var.repo_branch
    }

    environment_variable {
      name  = "TF_VAR_codestar_connection_arn"
      value = var.codestar_connection_arn
    }

    environment_variable {
      name  = "TF_VAR_manager_email"
      value = var.manager_email
    }

    environment_variable {
      name  = "TF_VAR_db_password"
      value = var.db_password
    }

    environment_variable {
      name  = "TF_VAR_az_count"
      value = tostring(var.az_count)
    }

    environment_variable {
      name  = "TF_VAR_nat_gateway_count"
      value = tostring(var.nat_gateway_count)
    }

    environment_variable {
      name  = "TF_VAR_node_instance_types"
      value = jsonencode(var.node_instance_types)
    }

    environment_variable {
      name  = "TF_VAR_node_group_min_size"
      value = tostring(var.node_group_min_size)
    }

    environment_variable {
      name  = "TF_VAR_node_group_desired_size"
      value = tostring(var.node_group_desired_size)
    }

    environment_variable {
      name  = "TF_VAR_node_group_max_size"
      value = tostring(var.node_group_max_size)
    }

    environment_variable {
      name  = "TF_VAR_db_engine_version"
      value = var.db_engine_version == null ? "" : var.db_engine_version
    }

    environment_variable {
      name  = "TF_VAR_rds_backup_retention_period"
      value = tostring(var.rds_backup_retention_period)
    }

    environment_variable {
      name  = "TF_VAR_enable_metrics_server_addon"
      value = tostring(var.enable_metrics_server_addon)
    }

    environment_variable {
      name  = "TF_VAR_enable_cloudwatch_observability_addon"
      value = tostring(var.enable_cloudwatch_observability_addon)
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "ci/buildspec.infra-plan.yml"
  }

  tags = local.common_tags
}

resource "aws_codebuild_project" "infra_apply" {
  name         = "${local.name}-infra-apply"
  service_role = aws_iam_role.codebuild_service_role.arn

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_MEDIUM"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "TF_VAR_repo_owner"
      value = var.repo_owner
    }

    environment_variable {
      name  = "TF_VAR_repo_name"
      value = var.repo_name
    }

    environment_variable {
      name  = "TF_VAR_repo_branch"
      value = var.repo_branch
    }

    environment_variable {
      name  = "TF_VAR_codestar_connection_arn"
      value = var.codestar_connection_arn
    }

    environment_variable {
      name  = "TF_VAR_manager_email"
      value = var.manager_email
    }

    environment_variable {
      name  = "TF_VAR_db_password"
      value = var.db_password
    }

    environment_variable {
      name  = "TF_VAR_az_count"
      value = tostring(var.az_count)
    }

    environment_variable {
      name  = "TF_VAR_nat_gateway_count"
      value = tostring(var.nat_gateway_count)
    }

    environment_variable {
      name  = "TF_VAR_node_instance_types"
      value = jsonencode(var.node_instance_types)
    }

    environment_variable {
      name  = "TF_VAR_node_group_min_size"
      value = tostring(var.node_group_min_size)
    }

    environment_variable {
      name  = "TF_VAR_node_group_desired_size"
      value = tostring(var.node_group_desired_size)
    }

    environment_variable {
      name  = "TF_VAR_node_group_max_size"
      value = tostring(var.node_group_max_size)
    }

    environment_variable {
      name  = "TF_VAR_db_engine_version"
      value = var.db_engine_version == null ? "" : var.db_engine_version
    }

    environment_variable {
      name  = "TF_VAR_rds_backup_retention_period"
      value = tostring(var.rds_backup_retention_period)
    }

    environment_variable {
      name  = "TF_VAR_enable_metrics_server_addon"
      value = tostring(var.enable_metrics_server_addon)
    }

    environment_variable {
      name  = "TF_VAR_enable_cloudwatch_observability_addon"
      value = tostring(var.enable_cloudwatch_observability_addon)
    }
  }

  source {
    type      = "CODEPIPELINE"
    buildspec = "ci/buildspec.infra-apply.yml"
  }

  tags = local.common_tags
}
