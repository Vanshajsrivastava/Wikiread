variable "project" {
  type        = string
  description = "Project name"
  default     = "wikiread"
}

variable "environment" {
  type        = string
  description = "Environment name"
  default     = "prod"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "eu-west-2"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR"
  default     = "10.40.0.0/16"
}

variable "eks_version" {
  type        = string
  description = "EKS version"
  default     = "1.30"
}

variable "az_count" {
  type        = number
  description = "Number of AZs/subnets to create (2 or 3 recommended)"
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "az_count must be between 2 and 3."
  }
}

variable "nat_gateway_count" {
  type        = number
  description = "Number of NAT gateways. Use 1 for cost-optimized, or az_count for HA."
  default     = 1

  validation {
    condition     = var.nat_gateway_count >= 1
    error_message = "nat_gateway_count must be at least 1."
  }
}

variable "node_instance_types" {
  type        = list(string)
  description = "EKS managed node group instance types"
  default     = ["t3.medium"]
}

variable "node_group_min_size" {
  type        = number
  description = "Minimum EKS node group size"
  default     = 2
}

variable "node_group_max_size" {
  type        = number
  description = "Maximum EKS node group size"
  default     = 6

  validation {
    condition     = var.node_group_max_size >= 1
    error_message = "node_group_max_size must be at least 1."
  }
}

variable "node_group_desired_size" {
  type        = number
  description = "Desired EKS node group size"
  default     = 2

  validation {
    condition     = var.node_group_desired_size >= 0
    error_message = "node_group_desired_size must be at least 0."
  }
}

variable "repo_owner" {
  type        = string
  description = "GitHub repository owner"
}

variable "repo_name" {
  type        = string
  description = "GitHub repository name"
}

variable "repo_branch" {
  type        = string
  description = "GitHub repository branch"
  default     = "main"
}

variable "codestar_connection_arn" {
  type        = string
  description = "CodeStar connection ARN for GitHub"
}

variable "manager_email" {
  type        = string
  description = "Manager email for Terraform plan notifications and approval"
}

variable "db_name" {
  type        = string
  description = "RDS database name"
  default     = "wikiread"
}

variable "db_username" {
  type        = string
  description = "RDS master username"
  default     = "wiki_admin"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "RDS master password"
}

variable "db_engine_version" {
  type        = string
  description = "PostgreSQL engine version for RDS. Set null to let AWS pick a regional default."
  default     = null
}

variable "rds_backup_retention_period" {
  type        = number
  description = "RDS backup retention period in days. Use 0 for free-tier-restricted accounts."
  default     = 7

  validation {
    condition     = var.rds_backup_retention_period >= 0 && var.rds_backup_retention_period <= 35
    error_message = "rds_backup_retention_period must be between 0 and 35."
  }
}

variable "allowed_cidrs_for_eks_api" {
  type        = list(string)
  description = "CIDRs allowed to access EKS API endpoint"
  default     = ["0.0.0.0/0"]
}

variable "enable_metrics_server_addon" {
  type        = bool
  description = "Enable EKS managed metrics-server addon for HPA metrics."
  default     = true
}

variable "enable_cloudwatch_observability_addon" {
  type        = bool
  description = "Enable EKS CloudWatch observability addon (Container Insights)."
  default     = true
}
