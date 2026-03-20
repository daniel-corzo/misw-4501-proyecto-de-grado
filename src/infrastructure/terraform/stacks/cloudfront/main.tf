module "cloudfront" {
  source = "../../modules/cloudfront"

  project_name                = var.project_name
  bucket_id                   = data.terraform_remote_state.static_frontend.outputs.bucket_id
  bucket_arn                  = data.terraform_remote_state.static_frontend.outputs.bucket_arn
  bucket_regional_domain_name = data.terraform_remote_state.static_frontend.outputs.bucket_regional_domain_name
  alb_dns_name                = data.terraform_remote_state.alb.outputs.load_balancer_dns
}
