module "rds" {
  source = "../../modules/rds"

  project_name          = var.project_name
  owner                 = var.owner
  instance_class        = var.instance_class
  jwt_private_key       = var.jwt_private_key
  jwt_public_key        = var.jwt_public_key
  vpc_id                = data.terraform_remote_state.network.outputs.vpc_id
  subnet_ids            = data.terraform_remote_state.network.outputs.public_subnet_ids
  ecs_security_group_id = data.terraform_remote_state.network.outputs.ecs_security_group_id
}
