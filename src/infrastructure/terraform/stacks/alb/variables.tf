variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "full_domain" {
  type        = string
  default     = "api.travel-hub.online"
}

variable "target_port" {
  type = number
}

variable "health_check_path" {
  type = string
}
