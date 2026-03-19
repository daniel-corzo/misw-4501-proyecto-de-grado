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

# ── IAM Role para CodeBuild (build + invalidación) ───────────────────────────

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
        # Permiso para subir los archivos al bucket de producción (stage Deploy)
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:DeleteObject", "s3:GetObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::${data.terraform_remote_state.static_frontend.outputs.bucket_id}",
          "arn:aws:s3:::${data.terraform_remote_state.static_frontend.outputs.bucket_id}/*",
        ]
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

# ── CodeBuild: compilación Angular ───────────────────────────────────────────

module "build" {
  source = "../../modules/codebuild"

  project_name    = "${var.project_name}-frontend-build"
  role_arn        = aws_iam_role.codebuild.arn
  buildspec_path  = "src/frontend/buildspec.yml"
  privileged_mode = false

  environment_variables = {}
}

# ── CodeBuild: invalidación CloudFront (stage separado) ──────────────────────

resource "aws_codebuild_project" "invalidate" {
  name          = "${var.project_name}-frontend-invalidate"
  service_role  = aws_iam_role.codebuild.arn
  build_timeout = 10

  source {
    type      = "CODEPIPELINE"
    buildspec = <<-BUILDSPEC
      version: 0.2
      phases:
        build:
          commands:
            - echo "Invalidando cache de CloudFront..."
            - aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/*"
            - echo "Invalidacion completada."
    BUILDSPEC
  }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"
    image        = "aws/codebuild/standard:7.0"
    type         = "LINUX_CONTAINER"

    environment_variable {
      name  = "CLOUDFRONT_DISTRIBUTION_ID"
      value = data.terraform_remote_state.cloudfront.outputs.distribution_id
    }
  }

  artifacts {
    type = "CODEPIPELINE"
  }

  logs_config {
    cloudwatch_logs {
      group_name = "/aws/codebuild/${var.project_name}-frontend-invalidate"
    }
  }
}

# ── CodePipeline: Source → Build → Deploy → Invalidate ───────────────────────

resource "aws_codepipeline" "frontend" {
  name          = "${var.project_name}-frontend"
  role_arn      = aws_iam_role.codepipeline.arn
  pipeline_type = "V2"

  artifact_store {
    type     = "S3"
    location = aws_s3_bucket.artifacts.id
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        ConnectionArn    = var.codestar_connection_arn
        FullRepositoryId = var.github_repo
        BranchName       = var.github_branch
        DetectChanges    = "false"
      }
    }
  }

  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      version          = "1"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]

      configuration = {
        ProjectName = module.build.project_name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "DeployToS3"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "S3"
      version         = "1"
      input_artifacts = ["build_output"]

      configuration = {
        BucketName = data.terraform_remote_state.static_frontend.outputs.bucket_id
        Extract    = "true"
      }
    }
  }

  stage {
    name = "Invalidate"

    action {
      name            = "InvalidateCloudFront"
      category        = "Build"
      owner           = "AWS"
      provider        = "CodeBuild"
      version         = "1"
      input_artifacts = ["source_output"]

      configuration = {
        ProjectName = aws_codebuild_project.invalidate.name
      }
    }
  }

  trigger {
    provider_type = "CodeStarSourceConnection"

    git_configuration {
      source_action_name = "Source"

      push {
        branches {
          includes = [var.github_branch]
        }

        file_paths {
          includes = ["src/frontend/**"]
        }
      }
    }
  }

  tags = { Project = var.project_name }
}
