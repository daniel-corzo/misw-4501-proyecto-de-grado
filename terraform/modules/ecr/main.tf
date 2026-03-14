resource "aws_ecr_repository" "repository" {
  name = "${local.prefix}-ecr"

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = var.project_name
  }
}
