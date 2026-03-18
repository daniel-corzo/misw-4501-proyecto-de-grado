output "cluster_name" {
  value = aws_ecs_cluster.cluster.name
}

output "cluster_id" {
  value = aws_ecs_cluster.cluster.id
}

output "service_names" {
  description = "Mapa de nombre de servicio a nombre del ECS service"
  value       = { for k, v in aws_ecs_service.service : k => v.name }
}
