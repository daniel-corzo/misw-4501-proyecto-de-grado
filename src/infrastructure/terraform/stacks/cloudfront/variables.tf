variable "project_name" {
  type = string
}

variable "region" {
  type = string
}

variable "owner" {
  type = string
}

variable "domain_name" {
  description = "Domain name for CloudFront distribution"
  type        = string
}
