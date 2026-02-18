resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "Allow Postgres from EKS nodes only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-rds-sg"
  })
}

resource "aws_db_subnet_group" "db" {
  name       = "${local.name}-db-subnets"
  subnet_ids = aws_subnet.private_db[*].id

  tags = merge(local.common_tags, {
    Name = "${local.name}-db-subnets"
  })
}

resource "aws_db_instance" "postgres" {
  identifier              = "${replace(local.name, "-", "")}-db"
  allocated_storage       = 50
  max_allocated_storage   = 200
  storage_type            = "gp3"
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = "db.t3.micro"
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.db.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  publicly_accessible     = false
  skip_final_snapshot     = true
  backup_retention_period = 7
  deletion_protection     = false
  multi_az                = false

  tags = merge(local.common_tags, {
    Name = "${local.name}-postgres"
  })
}

resource "aws_secretsmanager_secret" "app" {
  name = "${local.name}/app-secrets"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY   = "replace-before-use"
    DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
  })
}
