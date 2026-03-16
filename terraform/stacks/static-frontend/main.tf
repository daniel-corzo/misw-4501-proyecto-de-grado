module "static_frontend" {
  source = "../../modules/static-frontend"

  project_name = var.project_name
  owner        = var.owner
}
