variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "services" {
  description = "Mapa de servicios con su cluster_name, service_name, listener_arn, blue_tg_name, green_tg_name"
  type = map(object({
    cluster_name      = string
    service_name      = string
    listener_arn      = string
    blue_target_group_name  = string
    green_target_group_name = string
  }))
}
