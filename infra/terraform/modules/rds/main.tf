resource "aws_security_group" "rds" {
  name        = "${var.name}-rds-sg"
  description = "Allow Postgres from EKS nodes only"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, {
    Name = "${var.name}-rds-sg"
  })
}

resource "aws_db_subnet_group" "db" {
  name       = "${var.name}-db-subnets"
  subnet_ids = var.private_db_subnet_ids

  tags = merge(var.common_tags, {
    Name = "${var.name}-db-subnets"
  })
}

resource "aws_db_instance" "postgres" {
  identifier              = "${replace(var.name, "-", "")}-db"
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
  backup_retention_period = var.backup_retention_period
  deletion_protection     = false
  multi_az                = false

  tags = merge(var.common_tags, {
    Name = "${var.name}-postgres"
  })
}

resource "aws_secretsmanager_secret" "app" {
  name = "${var.name}/app-secrets"

  tags = var.common_tags
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY   = "replace-before-use"
    DATABASE_URL = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
  })
}
