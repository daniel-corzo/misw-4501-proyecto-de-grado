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
  description = "Mapa de nombre de servicio a lista de prefijos de ruta HTTP (sin barra inicial). Ej. usuarios puede incluir [\"auth\", \"usuarios\"] para el mismo target group. El orden de las claves determina la prioridad de las reglas del listener."
  type        = map(list(string))
}
