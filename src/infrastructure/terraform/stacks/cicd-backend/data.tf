# Obtiene el ID de la cuenta AWS actual para construir la URL del ECR
data "aws_caller_identity" "current" {}

data "terraform_remote_state" "ecs" {
  backend = "local" # O s3 según la configuración real

  config = {
    path = "../ecs/terraform.tfstate"
  }
}
