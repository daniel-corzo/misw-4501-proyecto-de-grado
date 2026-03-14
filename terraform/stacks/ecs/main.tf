module "ecs" {
  source = "../../modules/ecs"

  project_name = var.project_name
  region       = var.region
  owner        = var.owner

  repository_url = data.terraform_remote_state.ecr.outputs.repository_url

  subnet_ids = data.terraform_remote_state.network.outputs.public_subnet_ids

  security_group_id = data.terraform_remote_state.network.outputs.ecs_security_group_id
}
