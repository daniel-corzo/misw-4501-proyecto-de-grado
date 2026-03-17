resource "aws_codebuild_project" "this" {
  name          = var.project_name
  service_role  = var.role_arn
  build_timeout = 30

  source {
    type      = "CODEPIPELINE"
    buildspec = var.buildspec_path
  }

  artifacts {
    type = "CODEPIPELINE"
  }

  environment {
    type            = "LINUX_CONTAINER"
    image           = "aws/codebuild/standard:7.0"
    compute_type    = "BUILD_GENERAL1_SMALL"
    privileged_mode = var.privileged_mode

    dynamic "environment_variable" {
      for_each = var.environment_variables
      content {
        name  = environment_variable.key
        value = environment_variable.value
      }
    }
  }

  tags = { Project = var.project_name }
}
