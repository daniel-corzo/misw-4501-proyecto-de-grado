variable "project_name" {
  type = string
}

variable "owner" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "certificate_arn" {
  type = string
}

variable "zone_id" {
  type = string
}

variable "full_domain" {
  description = "Domain name for the ALB (e.g. alb.travel-hub.online)"
  type        = string
}

variable "target_port" {
  type = number
}

variable "health_check_path" {
  type = string
}

variable "services" {
  description = "Mapa de nombre de servicio a prefijo del router (ej. usuarios = /usuarios). El orden en el mapa determina la prioridad."
  type        = map(string)
}

variable "auth_path_rules" {
  description = "Reglas extra de path -> servicio existente (ej. auth -> usuarios). No crea target groups nuevos."
  type        = map(string)
  default     = {}
}
