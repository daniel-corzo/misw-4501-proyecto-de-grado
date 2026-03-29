variable "domain_name" {
  description = "The primary domain name"
  type        = string
  default     = "travel-hub.online"
}

variable "aws_region" {
  description = "The AWS region to deploy the foundation resources"
  type        = string
  default     = "us-east-1"
}