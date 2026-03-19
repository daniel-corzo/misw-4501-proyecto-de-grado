output "blue_target_group_arns" {
  description = "Mapa de nombre de servicio a ARN del target group BLUE"
  value       = { for svc, tg in aws_lb_target_group.blue : svc => tg.arn }
}

output "green_target_group_arns" {
  description = "Mapa de nombre de servicio a ARN del target group GREEN"
  value       = { for svc, tg in aws_lb_target_group.green : svc => tg.arn }
}

output "blue_target_group_names" {
  value = { for svc, tg in aws_lb_target_group.blue : svc => tg.name }
}

output "green_target_group_names" {
  value = { for svc, tg in aws_lb_target_group.green : svc => tg.name }
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

output "http_listener_arn" {
  value = aws_lb_listener.http.arn
}
