# Lee los outputs del stack static-frontend para obtener el nombre del bucket
data "terraform_remote_state" "static_frontend" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "static-frontend/terraform.tfstate"
    region = var.region
  }
}

# Lee los outputs del stack cloudfront para obtener el distribution ID
data "terraform_remote_state" "cloudfront" {
  backend = "s3"

  config = {
    bucket = "terraform-travelhub-state"
    key    = "cloudfront/terraform.tfstate"
    region = var.region
  }
}
