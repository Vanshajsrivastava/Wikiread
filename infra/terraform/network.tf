module "network" {
  source = "./modules/network"

  name              = local.name
  common_tags       = local.common_tags
  vpc_cidr          = var.vpc_cidr
  az_count          = var.az_count
  nat_gateway_count = var.nat_gateway_count
}
