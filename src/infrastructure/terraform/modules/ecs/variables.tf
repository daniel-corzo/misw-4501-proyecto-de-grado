variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "repository_url" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}
