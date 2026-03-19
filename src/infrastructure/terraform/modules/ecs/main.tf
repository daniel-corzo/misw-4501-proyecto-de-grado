# ===============================
# ECS Cluster
# ===============================

resource "aws_ecs_cluster" "cluster" {
  name = "${var.project_name}-cluster"

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# ECS Task Definition (uno por servicio)
# ===============================

resource "aws_ecs_task_definition" "task" {
  for_each = var.services

  family                   = "${var.project_name}-${each.key}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-${each.key}"
      image     = "${each.value.repository_url}:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = each.value.container_port
          hostPort      = each.value.container_port
        }
      ]
      environment = [
        {
          name  = "PORT"
          value = tostring(each.value.container_port)
        },
        {
          name  = "ENVIRONMENT"
          value = "production"
        }
      ]
      secrets = [
        {
          name      = "DB_URL"
          valueFrom = "${var.shared_secret_arn}:db_url::"
        },
        {
          name      = "JWT_SECRET"
          valueFrom = "${var.shared_secret_arn}:jwt_secret::"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_logs.name
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = each.key
        }
      }
    }
  ])
}

# ===============================
# ECS Services (uno por servicio)
# ===============================

resource "aws_ecs_service" "service" {
  for_each = var.services

  name            = "${var.project_name}-${each.key}-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task[each.key].arn
  desired_count   = 1
  launch_type     = "FARGATE"

  dynamic "load_balancer" {
    for_each = each.value.target_group_arn != null ? [each.value.target_group_arn] : []
    content {
      target_group_arn = load_balancer.value
      container_name   = "${var.project_name}-${each.key}"
      container_port   = each.value.container_port
    }
  }

  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [var.security_group_id]
  }
}

# ===============================
# CloudWatch Logs
# ===============================

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7
}

# ===============================
# IAM Roles
# ===============================

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_secrets_policy" {
  name = "${var.project_name}-ecs-secrets-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "secretsmanager:GetSecretValue",
        "kms:Decrypt"
      ]
      Effect   = "Allow"
      Resource = [var.shared_secret_arn]
    }]
  })
}
