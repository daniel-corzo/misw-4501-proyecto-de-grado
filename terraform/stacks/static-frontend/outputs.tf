output "bucket_id" {
  description = "ID of the static frontend S3 bucket"
  value       = module.static_frontend.bucket_id
}

output "bucket_arn" {
  description = "ARN of the static frontend S3 bucket"
  value       = module.static_frontend.bucket_arn
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the bucket (for CloudFront)"
  value       = module.static_frontend.bucket_regional_domain_name
}
