locals {
  # Overrides por servicio: exclude_secrets y extra_environment
  service_overrides = {
    usuarios = {
      exclude_secrets   = []
      extra_environment = []
    }
    busquedas = {
      exclude_secrets   = ["jwt_private_key"]
      extra_environment = []
    }
    hoteles = {
      exclude_secrets = ["jwt_private_key"]
      extra_environment = [
        {
          name  = "BACKEND_API_URL"
          value = "http://${data.terraform_remote_state.alb.outputs.load_balancer_dns}"
        }
      ]
    }
    reservas = {
      exclude_secrets   = ["jwt_private_key"]
      extra_environment = []
    }
    notificaciones = {
      exclude_secrets   = ["jwt_private_key", "db_url"]
      extra_environment = []
    }
  }

  services = {
    for svc, url in data.terraform_remote_state.ecr.outputs.repository_urls :
    svc => {
      repository_url    = url
      container_port    = 8000
      target_group_arn  = data.terraform_remote_state.alb.outputs.target_group_arns[svc]
      exclude_secrets   = lookup(local.service_overrides, svc, { exclude_secrets = [], extra_environment = [] }).exclude_secrets
      extra_environment = lookup(local.service_overrides, svc, { exclude_secrets = [], extra_environment = [] }).extra_environment
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
