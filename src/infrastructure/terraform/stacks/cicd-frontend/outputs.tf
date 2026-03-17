output "pipeline_name" {
  value = module.pipeline.pipeline_name
}

output "connection_arn" {
  description = "Activa esta conexion en la consola AWS antes del primer push"
  value       = aws_codestarconnections_connection.github.arn
}
