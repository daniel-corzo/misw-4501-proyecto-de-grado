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

variable "file_path_filter" {
  description = "Patron de ruta para filtrar triggers (ej: 'src/backend/reservas/**'). Si es null, el pipeline se dispara con cualquier cambio."
  type        = string
  default     = null
}
