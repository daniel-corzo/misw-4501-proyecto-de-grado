data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "network/terraform.tfstate"
    region = var.region
  }
}

data "terraform_remote_state" "ecr" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "ecr/terraform.tfstate"
    region = var.region
  }
}

data "terraform_remote_state" "alb" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "alb/terraform.tfstate"
    region = var.region
  }
}

data "terraform_remote_state" "rds" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "rds/terraform.tfstate"
    region = var.region
  }
}
