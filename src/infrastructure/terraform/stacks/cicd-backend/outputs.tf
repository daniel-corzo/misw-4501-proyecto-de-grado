output "codedeploy_application_names" {
  description = "Mapa de servicio a nombre de la CodeDeploy Application"
  value       = module.codedeploy.application_names
}

output "codedeploy_deployment_group_names" {
  description = "Mapa de servicio a nombre del Deployment Group"
  value       = module.codedeploy.deployment_group_names
}
