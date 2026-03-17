# Obtiene el ID de la cuenta AWS actual para construir la URL del ECR
data "aws_caller_identity" "current" {}
