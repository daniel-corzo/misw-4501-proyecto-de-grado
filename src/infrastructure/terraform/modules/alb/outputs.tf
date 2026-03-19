output "target_group_arns" {
  description = "Mapa de nombre de servicio a ARN del target group"
  value       = { for svc, tg in aws_lb_target_group.ecs : svc => tg.arn }
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
