variable "project_name" {
  type = string
}

variable "role_arn" {
  description = "ARN del IAM role que CodePipeline asume (creado en el stack)"
  type        = string
}

variable "artifact_bucket_id" {
  description = "Nombre del bucket S3 compartido de artefactos (creado en el stack)"
  type        = string
}

variable "github_repo" {
  type = string
}

variable "github_branch" {
  type    = string
  default = "main"
}

variable "codebuild_project_name" {
  type = string
}

variable "codestar_connection_arn" {
  type = string
}

variable "container_name" {
  description = "Nombre del contenedor en la task definition (para Image1ContainerName de CodeDeploy)"
  type        = string
}

variable "codedeploy_app_name" {
  description = "Nombre de la CodeDeploy Application para el stage Deploy"
  type        = string
}

variable "codedeploy_deployment_group_name" {
  description = "Nombre del Deployment Group de CodeDeploy para el stage Deploy"
  type        = string
}

variable "file_path_filter" {
  description = "Patrones de ruta para filtrar triggers. Si es null o vacío, el pipeline se dispara con cualquier cambio."
  type        = list(string)
  default     = null
}
