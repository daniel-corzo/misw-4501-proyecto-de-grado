variable "project_name" {
  description = "Project name"
  type        = string
}

variable "services" {
  description = "Lista de microservicios, se crea un repositorio ECR por cada uno"
  type        = set(string)
}
