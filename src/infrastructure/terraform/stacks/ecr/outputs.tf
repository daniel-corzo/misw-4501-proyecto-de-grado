output "repository_urls" {
  description = "URLs de los repositorios ECR por servicio"
  value       = module.ecr.repository_urls
}
