output "pipeline_names" {
  description = "Nombre de cada pipeline creado (uno por microservicio)"
  value       = { for svc, p in module.pipeline : svc => p.pipeline_name }
}

output "connection_arn" {
  description = "ARN de la conexion CodeStar usada por los pipelines"
  value       = var.codestar_connection_arn
}
