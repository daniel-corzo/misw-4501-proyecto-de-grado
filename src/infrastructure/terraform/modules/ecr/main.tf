resource "aws_ecr_repository" "repository" {
  for_each = var.services

  name = "${local.prefix}-${each.key}"

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project = var.project_name
  }
}
