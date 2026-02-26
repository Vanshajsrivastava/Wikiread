module "observability" {
  source = "./modules/observability"

  name                                  = local.name
  common_tags                           = local.common_tags
  cluster_name                          = module.eks.cluster_name
  oidc_provider_arn                     = module.eks.oidc_provider_arn
  cluster_oidc_issuer_url               = module.eks.cluster_oidc_issuer_url
  enable_metrics_server_addon           = var.enable_metrics_server_addon
  enable_cloudwatch_observability_addon = var.enable_cloudwatch_observability_addon
}
