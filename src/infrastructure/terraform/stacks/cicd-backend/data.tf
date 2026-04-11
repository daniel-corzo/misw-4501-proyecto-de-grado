data "aws_lb" "this" {
  name = "${var.project_name}-alb"
}

data "aws_lb_listener" "http" {
  load_balancer_arn = data.aws_lb.this.arn
  port              = 80
}
