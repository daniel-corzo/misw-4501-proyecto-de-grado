output "route53_zone_id" {
  description = "The Hosted Zone ID (Used by ALB and CloudFront stacks for Alias records)"
  value       = module.dns.route53_zone_id
}

output "route53_name_servers" {
  description = "The 4 Name Servers to paste into GoDaddy"
  value       = module.dns.route53_name_servers
}

output "acm_certificate_arn" {
  description = "The ARN of the validated SSL certificate (Attach this to ALB and CloudFront)"
  value       = module.dns.acm_certificate_arn
}