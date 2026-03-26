module "dns" {
  source = "../../modules/dns"

  domain_name = var.domain_name
  aws_region  = var.region
}
