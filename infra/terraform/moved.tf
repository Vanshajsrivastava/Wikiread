moved {
  from = aws_vpc.main
  to   = module.network.aws_vpc.main
}

moved {
  from = aws_internet_gateway.igw
  to   = module.network.aws_internet_gateway.igw
}

moved {
  from = aws_subnet.public
  to   = module.network.aws_subnet.public
}

moved {
  from = aws_subnet.private_app
  to   = module.network.aws_subnet.private_app
}

moved {
  from = aws_subnet.private_db
  to   = module.network.aws_subnet.private_db
}

moved {
  from = aws_eip.nat
  to   = module.network.aws_eip.nat
}

moved {
  from = aws_nat_gateway.nat
  to   = module.network.aws_nat_gateway.nat
}

moved {
  from = aws_route_table.public
  to   = module.network.aws_route_table.public
}

moved {
  from = aws_route_table.private
  to   = module.network.aws_route_table.private
}

moved {
  from = aws_route_table_association.public_assoc
  to   = module.network.aws_route_table_association.public_assoc
}

moved {
  from = aws_route_table_association.private_app_assoc
  to   = module.network.aws_route_table_association.private_app_assoc
}

moved {
  from = aws_route_table_association.private_db_assoc
  to   = module.network.aws_route_table_association.private_db_assoc
}

moved {
  from = aws_security_group.rds
  to   = module.rds.aws_security_group.rds
}

moved {
  from = aws_db_subnet_group.db
  to   = module.rds.aws_db_subnet_group.db
}

moved {
  from = aws_db_instance.postgres
  to   = module.rds.aws_db_instance.postgres
}

moved {
  from = aws_secretsmanager_secret.app
  to   = module.rds.aws_secretsmanager_secret.app
}

moved {
  from = aws_secretsmanager_secret_version.app
  to   = module.rds.aws_secretsmanager_secret_version.app
}

moved {
  from = aws_iam_role.cloudwatch_observability
  to   = module.observability.aws_iam_role.cloudwatch_observability
}

moved {
  from = aws_iam_role_policy_attachment.cloudwatch_observability
  to   = module.observability.aws_iam_role_policy_attachment.cloudwatch_observability
}

moved {
  from = aws_eks_addon.metrics_server
  to   = module.observability.aws_eks_addon.metrics_server
}

moved {
  from = aws_eks_addon.cloudwatch_observability
  to   = module.observability.aws_eks_addon.cloudwatch_observability
}
