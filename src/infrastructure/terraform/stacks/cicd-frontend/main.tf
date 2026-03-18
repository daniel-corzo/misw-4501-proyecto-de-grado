# ── Bucket S3 para artefactos del pipeline de frontend ───────────────────────

resource "aws_s3_bucket" "artifacts" {
  bucket        = "${var.project_name}-frontend-pipeline-artifacts"
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

# ── IAM Role para CodeBuild ───────────────────────────────────────────────────

resource "aws_iam_role" "codebuild" {
  name = "${var.project_name}-frontend-codebuild-role"

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
  name = "${var.project_name}-frontend-codebuild-policy"
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
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = ["arn:aws:s3:::*"]
      },
      {
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation"]
        Resource = "*"
      },
    ]
  })
}

# ── IAM Role para CodePipeline ────────────────────────────────────────────────

resource "aws_iam_role" "codepipeline" {
  name = "${var.project_name}-frontend-codepipeline-role"

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
  name = "${var.project_name}-frontend-codepipeline-policy"
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

# ── CodeBuild + CodePipeline ──────────────────────────────────────────────────

module "build" {
  source = "../../modules/codebuild"

  project_name    = "${var.project_name}-frontend-build"
  role_arn        = aws_iam_role.codebuild.arn
  buildspec_path  = "src/frontend/buildspec.yml"
  privileged_mode = false

  environment_variables = {
    S3_BUCKET_NAME             = data.terraform_remote_state.static_frontend.outputs.bucket_id
    CLOUDFRONT_DISTRIBUTION_ID = data.terraform_remote_state.cloudfront.outputs.distribution_id
  }
}

module "pipeline" {
  source = "../../modules/codepipeline"

  project_name            = "${var.project_name}-frontend"
  role_arn                = aws_iam_role.codepipeline.arn
  artifact_bucket_id      = aws_s3_bucket.artifacts.id
  github_repo             = var.github_repo
  github_branch           = var.github_branch
  codestar_connection_arn = var.codestar_connection_arn
  codebuild_project_name  = module.build.project_name
  file_path_filter        = "src/frontend/**"
}
