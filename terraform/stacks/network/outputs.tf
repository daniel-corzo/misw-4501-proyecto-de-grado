output "vpc_id" {
  value = module.network.vpc_id
}

output "public_subnet_ids" {
  value = module.network.public_subnet_ids
}

output "ecs_security_group_id" {
  value = module.network.ecs_security_group_id
}
