variable "project_name" {
  type = string
}

variable "role_arn" {
  description = "ARN del IAM role que CodeBuild asume (creado en el stack)"
  type        = string
}

variable "buildspec_path" {
  type = string
}

variable "privileged_mode" {
  type    = bool
  default = false
}

variable "environment_variables" {
  type    = map(string)
  default = {}
}
