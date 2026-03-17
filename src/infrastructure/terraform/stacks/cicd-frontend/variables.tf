variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "github_repo" {
  description = "Repositorio GitHub en formato org/repo"
  type        = string
}

variable "github_branch" {
  type    = string
  default = "main"
}

variable "codestar_connection_arn" {
  description = "ARN de la conexion CodeStar existente con GitHub"
  type        = string
}
