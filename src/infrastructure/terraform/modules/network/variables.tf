variable "project_name" {
  description = "Project name prefix"
  type        = string
}

variable "domain_name" {
  description = "Domain name for Route53"
  type        = string
  default     = "travel-hub.online"
  
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
}
