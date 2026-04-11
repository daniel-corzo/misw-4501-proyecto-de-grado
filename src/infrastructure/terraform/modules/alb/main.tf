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
  description = "Allow HTTP/HTTPS traffic to ALB"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
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
# Target Groups Blue (producción activa)
# ===============================

resource "aws_lb_target_group" "blue" {
  for_each = var.services

  name        = "${var.project_name}-${each.key}-blue"
  port        = var.target_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = var.health_check_path
    matcher             = "200"
    interval            = 10
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
# Target Groups Green (nueva versión durante deploy)
# ===============================

resource "aws_lb_target_group" "green" {
  for_each = var.services

  name        = "${var.project_name}-${each.key}-green"
  port        = var.target_port
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    path                = var.health_check_path
    matcher             = "200"
    interval            = 10
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
# Listener HTTPS (default: 404)
# ===============================

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy       = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

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
# DNS Record en Route53 apuntando al ALB
# ===============================

resource "aws_route53_record" "backend_api" {
  zone_id = var.zone_id
  name    = var.full_domain
  type    = "A"

  alias {
    name                   = aws_lb.this.dns_name
    zone_id                = aws_lb.this.zone_id
    evaluate_target_health = true
  }
}

# ===============================
# Listener Rules (path-based, apuntan al TG blue)
# ===============================

resource "aws_lb_listener_rule" "service-http" {
  for_each = local.services_with_priority

  listener_arn = aws_lb_listener.http.arn
  priority     = each.value

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue[each.key].arn
  }

  condition {
    path_pattern {
      values = ["/${var.services[each.key]}", "/${var.services[each.key]}/*"]
    }
  }
}

resource "aws_lb_listener_rule" "service-https" {
  for_each = local.services_with_priority

  listener_arn = aws_lb_listener.https.arn
  priority     = each.value

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue[each.key].arn
  }

  condition {
    path_pattern {
      values = ["/${var.services[each.key]}", "/${var.services[each.key]}/*"]
    }
  }
}

# ===============================
# Listener Rules extra (alias de path -> servicio existente)
# Ejemplo: /auth/* -> target group de usuarios
# ===============================

locals {
  auth_rules_with_priority = {
    for idx, path in keys(var.auth_path_rules) : path => 100 + (idx + 1) * 10
  }
}

resource "aws_lb_listener_rule" "auth-http" {
  for_each = local.auth_rules_with_priority

  listener_arn = aws_lb_listener.http.arn
  priority     = each.value

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue[var.auth_path_rules[each.key]].arn
  }

  condition {
    path_pattern {
      values = ["/${each.key}", "/${each.key}/*"]
    }
  }
}

resource "aws_lb_listener_rule" "auth-https" {
  for_each = local.auth_rules_with_priority

  listener_arn = aws_lb_listener.https.arn
  priority     = each.value

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.blue[var.auth_path_rules[each.key]].arn
  }

  condition {
    path_pattern {
      values = ["/${each.key}", "/${each.key}/*"]
    }
  }
}
