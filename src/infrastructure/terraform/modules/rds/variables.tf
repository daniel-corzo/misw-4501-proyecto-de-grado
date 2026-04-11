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
  type        = list(string)
  description = "Subnets donde se desplegará RDS (mínimo 2 AZs)"
}

variable "ecs_security_group_id" {
  type        = string
  description = "SG de los ECS tasks — se permite acceso al puerto 5432 desde este SG"
}

variable "db_name" {
  type    = string
  default = "travelhub"
}

variable "db_username" {
  type    = string
  default = "travelhub"
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "jwt_private_key" {
  type        = string
  sensitive   = true
  description = "JWT private key in PEM format"
}

variable "jwt_public_key" {
  type        = string
  sensitive   = true
  description = "JWT public key in PEM format"
}

