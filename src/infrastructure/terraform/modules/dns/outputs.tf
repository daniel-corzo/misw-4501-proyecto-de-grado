output "route53_zone_id" {
  description = "The Hosted Zone ID (Used by ALB and CloudFront stacks for Alias records)"
  value       = aws_route53_zone.main.zone_id
}

output "route53_name_servers" {
  description = "The 4 Name Servers to paste into GoDaddy"
  value       = aws_route53_zone.main.name_servers
}

output "acm_certificate_arn" {
  description = "The ARN of the validated SSL certificate (Attach this to ALB and CloudFront)"
  value       = aws_acm_certificate_validation.cert.certificate_arn
}