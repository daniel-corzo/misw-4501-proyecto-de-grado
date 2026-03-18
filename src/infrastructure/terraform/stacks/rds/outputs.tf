output "db_address" {
  value = module.rds.db_address
}

output "shared_secret_arn" {
  value = module.rds.shared_secret_arn
}
