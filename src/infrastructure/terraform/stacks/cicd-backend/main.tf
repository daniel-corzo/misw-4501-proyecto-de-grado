locals {
  services = toset([
    "usuarios",
    "busquedas",
    "hoteles",
    "reservas",
    "notificaciones",
  ])
}

# ── CodeDeploy: una app + deployment group por servicio ───────────────────────
# El build y push a ECR se hace desde GitHub Actions.
# CodeDeploy se encarga del blue/green ECS deployment.

module "codedeploy" {
  source = "../../modules/codedeploy"

  project_name = var.project_name
  region       = var.region

  services = {
    for svc in local.services : svc => {
      cluster_name            = "${var.project_name}-cluster"
      service_name            = "${var.project_name}-${svc}-service"
      listener_arn            = data.aws_lb_listener.http.arn
      blue_target_group_name  = "${var.project_name}-${svc}-blue"
      green_target_group_name = "${var.project_name}-${svc}-green"
    }
  }
}
