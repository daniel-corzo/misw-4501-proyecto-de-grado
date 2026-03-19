locals {
  services = {
    for svc, url in data.terraform_remote_state.ecr.outputs.repository_urls :
    svc => {
      repository_url   = url
      container_port   = 8000
      target_group_arn = data.terraform_remote_state.alb.outputs.blue_target_group_arns[svc]
    }
  }

  codedeploy_services = {
    for svc, _ in local.services :
    svc => {
      cluster_name            = module.ecs.cluster_name
      service_name            = module.ecs.service_names[svc]
      listener_arn            = data.terraform_remote_state.alb.outputs.http_listener_arn
      blue_target_group_name  = data.terraform_remote_state.alb.outputs.blue_target_group_names[svc]
      green_target_group_name = data.terraform_remote_state.alb.outputs.green_target_group_names[svc]
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

module "codedeploy" {
  source = "../../modules/codedeploy"

  project_name = var.project_name
  region       = var.region
  services     = local.codedeploy_services
}
