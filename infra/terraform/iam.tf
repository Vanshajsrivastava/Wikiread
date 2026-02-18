resource "aws_s3_bucket" "pipeline_artifacts" {
  bucket = "${local.name}-${data.aws_caller_identity.current.account_id}-pipeline-artifacts"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "pipeline_artifacts" {
  bucket = aws_s3_bucket.pipeline_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "tf_plan_bucket" {
  bucket = "${local.name}-${data.aws_caller_identity.current.account_id}-tf-plans"

  tags = local.common_tags
}

resource "aws_s3_bucket_versioning" "tf_plan_bucket" {
  bucket = aws_s3_bucket.tf_plan_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tf_plan_bucket" {
  bucket = aws_s3_bucket.tf_plan_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tf_plan_bucket" {
  bucket = aws_s3_bucket.tf_plan_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_sns_topic" "infra_approvals" {
  name = "${local.name}-infra-approvals"

  tags = local.common_tags
}

resource "aws_sns_topic_subscription" "manager_email" {
  topic_arn = aws_sns_topic.infra_approvals.arn
  protocol  = "email"
  endpoint  = var.manager_email
}

resource "aws_iam_role" "codepipeline_role" {
  name = "${local.name}-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "codepipeline.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "${local.name}-codepipeline-policy"
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild",
          "codestar-connections:UseConnection",
          "sns:Publish"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role" "codebuild_service_role" {
  name = "${local.name}-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "codebuild.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "codebuild_admin" {
  role       = aws_iam_role.codebuild_service_role.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
