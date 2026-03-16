output "distribution_id" {
  description = "ID of the CloudFront distribution"
  value       = aws_cloudfront_distribution.this.id
}

output "distribution_arn" {
  description = "ARN of the CloudFront distribution"
  value       = aws_cloudfront_distribution.this.arn
}

output "domain_name" {
  description = "Domain name of the CloudFront distribution"
  value       = aws_cloudfront_distribution.this.domain_name
}

output "hosted_zone_id" {
  description = "Hosted zone ID of the CloudFront distribution (for Route 53 alias)"
  value       = aws_cloudfront_distribution.this.hosted_zone_id
}

output "url" {
  description = "URL of the CloudFront distribution"
  value       = "https://${aws_cloudfront_distribution.this.domain_name}"
}
