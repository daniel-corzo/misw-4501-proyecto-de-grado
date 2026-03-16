data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "network/terraform.tfstate"
    region = var.region
  }
}
