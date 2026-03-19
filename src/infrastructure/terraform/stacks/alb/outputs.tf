output "target_group_arns" {
  description = "Mapa de servicio a ARN del target group blue"
  value       = module.alb.target_group_arns
}

output "target_group_names_blue" {
  description = "Mapa de servicio a nombre del target group blue"
  value       = module.alb.target_group_names_blue
}

output "target_group_names_green" {
  description = "Mapa de servicio a nombre del target group green"
  value       = module.alb.target_group_names_green
}

output "listener_arn" {
  description = "ARN del listener HTTP del ALB"
  value       = module.alb.listener_arn
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
