output "target_group_arns" {
  description = "Mapa de servicio a ARN del target group blue (compatibilidad con stack ECS)"
  value       = { for svc, tg in aws_lb_target_group.blue : svc => tg.arn }
}

output "target_group_names_blue" {
  description = "Mapa de servicio a nombre del target group blue (para CodeDeploy)"
  value       = { for svc, tg in aws_lb_target_group.blue : svc => tg.name }
}

output "target_group_names_green" {
  description = "Mapa de servicio a nombre del target group green (para CodeDeploy)"
  value       = { for svc, tg in aws_lb_target_group.green : svc => tg.name }
}

output "listener_arn" {
  description = "ARN del listener HTTP del ALB (para CodeDeploy deployment group)"
  value       = aws_lb_listener.http.arn
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
