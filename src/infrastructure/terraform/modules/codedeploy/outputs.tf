output "application_names" {
  description = "Mapa de servicio a nombre de la CodeDeploy Application"
  value       = { for k, v in aws_codedeploy_app.this : k => v.name }
}

output "deployment_group_names" {
  description = "Mapa de servicio a nombre del Deployment Group"
  value       = { for k, v in aws_codedeploy_deployment_group.this : k => v.deployment_group_name }
}
