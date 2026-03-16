output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "ecs_security_group_id" {
  description = "ECS security group ID"
  value = aws_security_group.ecs.id
}
