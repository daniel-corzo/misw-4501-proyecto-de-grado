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

variable "target_port" {
  type = number
}

variable "health_check_path" {
  type = string
}

variable "services" {
  description = "Lista ordenada de servicios. El índice determina la prioridad de la listener rule."
  type        = list(string)
}
