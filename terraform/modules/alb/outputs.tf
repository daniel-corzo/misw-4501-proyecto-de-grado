output "target_group_arn" {
  value = aws_lb_target_group.ecs.arn
}

output "load_balancer_dns" {
  value = aws_lb.this.dns_name
}

output "load_balancer_arn" {
  value = aws_lb.this.arn
}

output "alb_security_group_id" {
  value = aws_security_group.alb.id
}
