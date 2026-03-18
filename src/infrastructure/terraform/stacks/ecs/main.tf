locals {
  services = {
    for svc, url in data.terraform_remote_state.ecr.outputs.repository_urls :
    svc => {
      repository_url   = url
      container_port   = 8000
      target_group_arn = data.terraform_remote_state.alb.outputs.target_group_arns[svc]
    }
  }
}

module "ecs" {
  source = "../../modules/ecs"

  project_name      = var.project_name
  region            = var.region
  owner             = var.owner
  subnet_ids        = data.terraform_remote_state.network.outputs.public_subnet_ids
  security_group_id = data.terraform_remote_state.network.outputs.ecs_security_group_id
  shared_secret_arn = data.terraform_remote_state.rds.outputs.shared_secret_arn
  services          = local.services
}
