output "repository_urls" {
  description = "URLs de los repositorios ECR por servicio"
  value       = { for svc, repo in aws_ecr_repository.repository : svc => repo.repository_url }
}
