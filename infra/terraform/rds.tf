module "rds" {
  source = "./modules/rds"

  name                       = local.name
  common_tags                = local.common_tags
  vpc_id                     = module.network.vpc_id
  private_db_subnet_ids      = module.network.private_db_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id
  db_name                    = var.db_name
  db_username                = var.db_username
  db_password                = var.db_password
  db_engine_version          = var.db_engine_version
  backup_retention_period    = var.rds_backup_retention_period
}
