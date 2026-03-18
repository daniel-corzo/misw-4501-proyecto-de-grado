locals {
  services = toset([
    "autenticacion",
    "usuarios",
    "busqueda",
    "hoteles",
    "inventario",
    "reservas",
    "pagos",
    "notificaciones",
  ])
}

# ── Bucket S3 compartido para artefactos de todos los pipelines ───────────────

resource "aws_s3_bucket" "artifacts" {
  bucket        = "${var.project_name}-backend-pipeline-artifacts"
  force_destroy = true
  tags          = { Project = var.project_name }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ── IAM Role compartido para todos los CodeBuild ─────────────────────────────

resource "aws_iam_role" "codebuild" {
  name = "${var.project_name}-backend-codebuild-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codebuild.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "codebuild" {
  name = "${var.project_name}-backend-codebuild-policy"
  role = aws_iam_role.codebuild.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject"]
        Resource = "${aws_s3_bucket.artifacts.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:log-group:/aws/codebuild/${var.project_name}*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
        ]
        Resource = "*"
      },
    ]
  })
}

# ── IAM Role compartido para todos los CodePipeline ──────────────────────────

resource "aws_iam_role" "codepipeline" {
  name = "${var.project_name}-backend-codepipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "codepipeline.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "codepipeline" {
  name = "${var.project_name}-backend-codepipeline-policy"
  role = aws_iam_role.codepipeline.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:GetBucketVersioning"]
        Resource = [aws_s3_bucket.artifacts.arn, "${aws_s3_bucket.artifacts.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["codebuild:StartBuild", "codebuild:BatchGetBuilds"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["codestar-connections:UseConnection"]
        Resource = var.codestar_connection_arn
      },
    ]
  })
}

# ── Un CodeBuild + un CodePipeline por microservicio ─────────────────────────

module "build" {
  for_each = local.services
  source   = "../../modules/codebuild"

  project_name    = "${var.project_name}-${each.key}-build"
  role_arn        = aws_iam_role.codebuild.arn
  buildspec_path  = "src/backend/buildspec.yml"
  privileged_mode = true

  environment_variables = {
    AWS_REGION   = var.region
    ECR_REGISTRY = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
    SERVICE      = each.key
  }
}

module "pipeline" {
  for_each = local.services
  source   = "../../modules/codepipeline"

  project_name            = "${var.project_name}-${each.key}"
  role_arn                = aws_iam_role.codepipeline.arn
  artifact_bucket_id      = aws_s3_bucket.artifacts.id
  github_repo             = var.github_repo
  github_branch           = var.github_branch
  codestar_connection_arn = var.codestar_connection_arn
  codebuild_project_name  = module.build[each.key].project_name
  file_path_filter        = "src/backend/${each.key}/**"
}
