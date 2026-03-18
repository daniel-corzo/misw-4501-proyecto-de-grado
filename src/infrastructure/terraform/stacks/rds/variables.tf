variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}
