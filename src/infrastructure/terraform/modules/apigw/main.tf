# ===============================
# API Gateway HTTP API
# ===============================

resource "aws_apigatewayv2_api" "this" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allow_headers = ["*"]
  }

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true
}

# ===============================
# Integración única — proxy transparente al ALB
# ===============================

resource "aws_apigatewayv2_integration" "alb" {
  api_id             = aws_apigatewayv2_api.this.id
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri    = "http://${var.alb_dns_name}/{proxy}"
}

# ===============================
# Ruta catch-all
# ===============================

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.alb.id}"
}
