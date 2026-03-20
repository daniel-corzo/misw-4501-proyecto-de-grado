data "terraform_remote_state" "static_frontend" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "static-frontend/terraform.tfstate"
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
