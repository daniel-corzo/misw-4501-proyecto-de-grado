# ===============================
# Contraseña aleatoria
# ===============================

resource "random_password" "db" {
  length  = 16
  special = false
}

resource "random_password" "jwt_secret" {
  length  = 32
  special = false
}

# ===============================
# Security Group para RDS
# ===============================

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL access from ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# Subnet Group
# ===============================

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# RDS PostgreSQL
# ===============================

resource "aws_db_instance" "main" {
  identifier        = "${var.project_name}-postgres"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = var.instance_class
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false
  skip_final_snapshot = true

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# Secrets Manager — secret compartido
# ===============================

resource "aws_secretsmanager_secret" "shared" {
  name                    = "${var.project_name}/shared-config"
  recovery_window_in_days = 0

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

resource "aws_secretsmanager_secret_version" "shared" {
  secret_id = aws_secretsmanager_secret.shared.id
  secret_string = jsonencode({
    db_url     = "postgresql+asyncpg://${var.db_username}:${random_password.db.result}@${aws_db_instance.main.address}:5432/${var.db_name}"
    jwt_secret = random_password.jwt_secret.result
  })
}
