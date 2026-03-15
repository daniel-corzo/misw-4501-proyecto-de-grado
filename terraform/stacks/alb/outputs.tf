output "target_group_arn" {
  value = module.alb.target_group_arn
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
