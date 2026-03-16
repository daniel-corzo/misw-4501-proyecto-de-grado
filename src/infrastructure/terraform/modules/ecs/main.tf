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
# ECS Log Group
# ===============================

resource "aws_cloudwatch_log_group" "ecs_logs" {
  name = "/ecs/${var.project_name}"

  retention_in_days = 7
}

# ===============================
# ECS Task Execution Role
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

# ===============================
# ECS Task Definition
# ===============================

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]

  network_mode = "awsvpc"

  cpu    = "256"
  memory = "512"

  execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name  = "${var.project_name}-container"
      image = "${var.repository_url}:latest"

      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.ecs_logs.name
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# ===============================
# ECS Service
# ===============================

resource "aws_ecs_service" "service" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn

  desired_count = 1
  launch_type   = "FARGATE"

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "${var.project_name}-container"
    container_port   = 3000
  }

  network_configuration {
    subnets          = var.subnet_ids
    assign_public_ip = true
    security_groups  = [var.security_group_id]
  }
}
