locals {
  # Mapa de nombre de servicio → prefijo real del router en la app
  services = {
    usuarios       = "usuarios"
    busquedas      = "busquedas"
    hoteles        = "hoteles"
    reservas       = "reservas"
    notificaciones = "notificaciones"
  }
}

module "alb" {
  source = "../../modules/alb"

  project_name = var.project_name
  owner        = var.owner

  vpc_id     = data.terraform_remote_state.network.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.network.outputs.public_subnet_ids

  certificate_arn   = data.terraform_remote_state.dns.outputs.acm_certificate_arn
  zone_id           = data.terraform_remote_state.dns.outputs.route53_zone_id
  full_domain       = var.full_domain

  target_port       = var.target_port
  health_check_path = var.health_check_path
  services          = local.services

  # /auth/* y /api/auth/* (tras strip de CloudFront) deben llegar a usuarios
  auth_path_rules = {
    auth = "usuarios"
  }
}
