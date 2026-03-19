output "cluster_name" {
  value = module.ecs.cluster_name
}

output "cluster_id" {
  value = module.ecs.cluster_id
}

output "service_names" {
  value = module.ecs.service_names
}

output "codedeploy_application_names" {
  value = module.codedeploy.application_names
}

output "codedeploy_deployment_group_names" {
  value = module.codedeploy.deployment_group_names
}
