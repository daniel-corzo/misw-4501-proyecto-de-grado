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
# ECS Log Group (compartido)
# ===============================

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name = "/ecs/${var.project_name}"

  retention_in_days = 7
}

# ===============================
# ECS Task Execution Role (compartido)
# ===============================

resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
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
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.shared_secret_arn]
    }]
  })
}

# ===============================
# ECS Task Definitions (uno por servicio)
# ===============================

resource "aws_ecs_task_definition" "task" {
  for_each = var.services

  family                   = "${var.project_name}-${each.key}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "${var.project_name}-${each.key}"
      image = "${each.value.repository_url}:latest"

      portMappings = [
        {
          containerPort = each.value.container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "SERVICE_NAME", value = each.key },
        { name = "AWS_REGION", value = var.region },
      ]

      secrets = [
        { name = "DB_URL",     valueFrom = "${var.shared_secret_arn}:db_url::" },
        { name = "JWT_SECRET", valueFrom = "${var.shared_secret_arn}:jwt_secret::" },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.region
          awslogs-stream-prefix = each.key
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

  deployment_controller {
    type = "CODE_DEPLOY"
  }

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

  lifecycle {
    ignore_changes = [
      task_definition,
      load_balancer
    ]
  }
}
