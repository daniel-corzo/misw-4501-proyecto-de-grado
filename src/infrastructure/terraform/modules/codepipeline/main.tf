resource "aws_codepipeline" "this" {
  name          = var.project_name
  role_arn      = var.role_arn
  pipeline_type = "V2"

  artifact_store {
    type     = "S3"
    location = var.artifact_bucket_id
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
        ProjectName = var.codebuild_project_name
      }
    }
  }

  stage {
    name = "Deploy"

    action {
      name            = "Deploy"
      category        = "Deploy"
      owner           = "AWS"
      provider        = "CodeDeployToECS"
      version         = "1"
      input_artifacts = ["build_output"]

      configuration = {
        AppSpecTemplateArtifact        = "build_output"
        AppSpecTemplatePath            = "appspec.yaml"
        TaskDefinitionTemplateArtifact = "build_output"
        TaskDefinitionTemplatePath     = "taskdef.json"
        Image1ArtifactName             = "build_output"
        Image1ContainerName            = var.container_name
        ApplicationName                = var.codedeploy_app_name
        DeploymentGroupName            = var.codedeploy_deployment_group_name
      }
    }
  }

  dynamic "trigger" {
    for_each = var.file_path_filter != null ? [1] : []

    content {
      provider_type = "CodeStarSourceConnection"

      git_configuration {
        source_action_name = "Source"

        push {
          branches {
            includes = [var.github_branch]
          }

          file_paths {
            includes = var.file_path_filter
          }
        }
      }
    }
  }

  tags = { Project = var.project_name }
}
