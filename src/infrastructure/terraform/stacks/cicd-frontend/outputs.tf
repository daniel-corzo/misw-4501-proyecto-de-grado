output "pipeline_name" {
  value = module.pipeline.pipeline_name
}

output "connection_arn" {
  description = "ARN de la conexion CodeStar usada por los pipelines"
  value       = var.codestar_connection_arn
}
