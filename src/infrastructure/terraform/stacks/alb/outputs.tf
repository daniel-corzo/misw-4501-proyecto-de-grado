output "target_group_arns" {
  description = "Mapa de nombre de servicio a ARN del target group"
  value       = module.alb.target_group_arns
}

output "load_balancer_dns" {
  value = module.alb.load_balancer_dns
}

output "load_balancer_arn" {
  value = module.alb.load_balancer_arn
}

output "alb_security_group_id" {
  value = module.alb.alb_security_group_id
}
