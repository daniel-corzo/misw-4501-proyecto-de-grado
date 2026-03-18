module "apigw" {
  source = "../../modules/apigw"

  project_name = var.project_name
  owner        = var.owner
  alb_dns_name = data.terraform_remote_state.alb.outputs.load_balancer_dns
}
