locals {
  # Asigna prioridad según posición en el mapa (10, 20, 30, ...)
  services_with_priority = {
    for idx, svc in keys(var.services) : svc => (idx + 1) * 10
  }
}

# ===============================
# Security Group
# ===============================

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Allow HTTP traffic to ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
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
# Application Load Balancer
# ===============================

resource "aws_lb" "this" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.subnet_ids

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# Target Groups (uno por servicio)
# ===============================

resource "aws_lb_target_group" "ecs" {
  for_each = var.services

  name        = "${var.project_name}-${each.key}-tg"
  port        = var.target_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = var.health_check_path
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

# ===============================
# Listener HTTP (default: 404)
# ===============================

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "application/json"
      message_body = "{\"error\": \"not found\"}"
      status_code  = "404"
    }
  }
}

# ===============================
# Listener Rules (path-based por prefijo de router)
# ===============================

resource "aws_lb_listener_rule" "service" {
  for_each = local.services_with_priority

  listener_arn = aws_lb_listener.http.arn
  priority     = each.value

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs[each.key].arn
  }

  condition {
    path_pattern {
      # var.services[each.key] es el prefijo del router (ej. "auth" para auth)
      values = ["/${var.services[each.key]}", "/${var.services[each.key]}/*"]
    }
  }
}
