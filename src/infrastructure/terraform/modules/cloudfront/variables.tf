variable "project_name" {
  description = "Project name for naming and tags"
  type        = string
}

variable "bucket_id" {
  description = "ID of the S3 bucket (origin)"
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket (for bucket policy)"
  type        = string
}

variable "bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket for the origin"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the ALB, used as origin for /api/* paths"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the CloudFront distribution"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the ACM certificate for the CloudFront distribution"
  type        = string
}

variable "route53_zone_id" {
  description = "Route53 Hosted Zone ID for the domain, used for Alias record"
  type        = string
  
}
