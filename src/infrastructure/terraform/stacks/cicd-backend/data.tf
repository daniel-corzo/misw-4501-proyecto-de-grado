data "aws_caller_identity" "current" {}

# ALB — para obtener el listener ARN y los nombres de los target groups
data "aws_lb" "this" {
  name = "${var.project_name}-alb"
}

data "aws_lb_listener" "http" {
  load_balancer_arn = data.aws_lb.this.arn
  port              = 80
}
