variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "services" {
  description = "Lista de microservicios para crear repositorios ECR"
  type        = set(string)
}
