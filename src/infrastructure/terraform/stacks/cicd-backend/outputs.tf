output "pipeline_names" {
  description = "Nombre de cada pipeline creado (uno por microservicio)"
  value       = { for svc, p in module.pipeline : svc => p.pipeline_name }
}

output "connection_arn" {
  description = "Activa esta conexion en la consola AWS antes del primer push"
  value       = aws_codestarconnections_connection.github.arn
}
