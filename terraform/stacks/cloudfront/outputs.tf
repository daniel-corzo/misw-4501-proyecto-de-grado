output "distribution_id" {
  description = "CloudFront distribution ID"
  value       = module.cloudfront.distribution_id
}

output "domain_name" {
  description = "CloudFront distribution domain name"
  value       = module.cloudfront.domain_name
}

output "url" {
  description = "CloudFront URL for the static frontend"
  value       = module.cloudfront.url
}
