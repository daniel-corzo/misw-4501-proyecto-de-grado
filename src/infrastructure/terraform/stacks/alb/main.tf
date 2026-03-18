locals {
  services = [
    "autenticacion",
    "usuarios",
    "busqueda",
    "hoteles",
    "inventario",
    "reservas",
    "pagos",
    "notificaciones",
  ]
}

module "alb" {
  source = "../../modules/alb"

  project_name = var.project_name
  owner        = var.owner

  vpc_id     = data.terraform_remote_state.network.outputs.vpc_id
  subnet_ids = data.terraform_remote_state.network.outputs.public_subnet_ids

  target_port       = var.target_port
  health_check_path = var.health_check_path
  services          = local.services
}
