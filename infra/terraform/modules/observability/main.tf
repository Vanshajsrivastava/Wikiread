resource "aws_iam_role" "cloudwatch_observability" {
  count = var.enable_cloudwatch_observability_addon ? 1 : 0

  name = "${var.name}-cw-observability-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${trimprefix(var.cluster_oidc_issuer_url, "https://")}:sub" = "system:serviceaccount:amazon-cloudwatch:cloudwatch-agent"
            "${trimprefix(var.cluster_oidc_issuer_url, "https://")}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy_attachment" "cloudwatch_observability" {
  count = var.enable_cloudwatch_observability_addon ? 1 : 0

  role       = aws_iam_role.cloudwatch_observability[0].name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_eks_addon" "metrics_server" {
  count = var.enable_metrics_server_addon ? 1 : 0

  cluster_name                = var.cluster_name
  addon_name                  = "metrics-server"
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  tags = var.common_tags
}

resource "aws_eks_addon" "cloudwatch_observability" {
  count = var.enable_cloudwatch_observability_addon ? 1 : 0

  cluster_name                = var.cluster_name
  addon_name                  = "amazon-cloudwatch-observability"
  service_account_role_arn    = aws_iam_role.cloudwatch_observability[0].arn
  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [aws_iam_role_policy_attachment.cloudwatch_observability]

  tags = var.common_tags
}
