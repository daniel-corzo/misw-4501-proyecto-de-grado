variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "services" {
  description = "Mapa de servicios con la info necesaria para cada deployment group"
  type = map(object({
    cluster_name            = string
    service_name            = string
    listener_arn            = string
    blue_target_group_name  = string
    green_target_group_name = string
  }))
}
