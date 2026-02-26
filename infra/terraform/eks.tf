module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = local.name
  cluster_version = var.eks_version

  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.allowed_cidrs_for_eks_api
  cluster_endpoint_private_access      = true

  vpc_id     = module.network.vpc_id
  subnet_ids = module.network.private_app_subnet_ids

  # Avoid caller-identity drift between local runs and CodeBuild runs.
  # We manage access explicitly via access_entries below.
  enable_cluster_creator_admin_permissions = false

  eks_managed_node_groups = {
    default = {
      min_size       = var.node_group_min_size
      max_size       = var.node_group_max_size
      desired_size   = var.node_group_desired_size
      instance_types = var.node_instance_types
      subnet_ids     = module.network.private_app_subnet_ids
      capacity_type  = "ON_DEMAND"
    }
  }

  access_entries = {
    codebuild_deploy = {
      principal_arn = aws_iam_role.codebuild_service_role.arn

      policy_associations = {
        admin = {
          policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
          access_scope = {
            type = "cluster"
          }
        }
      }
    }
  }

  tags = local.common_tags
}
