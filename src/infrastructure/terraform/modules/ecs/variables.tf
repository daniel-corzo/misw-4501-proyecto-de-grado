variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string
}

variable "shared_secret_arn" {
  type        = string
  description = "ARN del secret compartido con db_url y jwt_secret"
}

variable "services" {
  description = "Mapa de servicios con su repository_url, container_port y target_group_arn opcional"
  type = map(object({
    repository_url   = string
    container_port   = number
    target_group_arn = optional(string)
  }))
}
