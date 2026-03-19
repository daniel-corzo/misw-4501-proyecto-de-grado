# ===============================
# IAM Role para CodeDeploy
# ===============================

resource "aws_iam_role" "codedeploy" {
  name = "${var.project_name}-codedeploy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "codedeploy.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "codedeploy" {
  role       = aws_iam_role.codedeploy.name
  policy_arn = "arn:aws:iam::aws:policy/AWSCodeDeployRoleForECS"
}

# ===============================
# CodeDeploy Applications
# ===============================

resource "aws_codedeploy_app" "this" {
  for_each         = var.services
  compute_platform = "ECS"
  name             = "${var.project_name}-${each.key}"
}

# ===============================
# CodeDeploy Deployment Groups
# ===============================

resource "aws_codedeploy_deployment_group" "this" {
  for_each               = var.services
  app_name               = aws_codedeploy_app.this[each.key].name
  deployment_config_name = "CodeDeployDefault.ECSAllAtOnce"
  deployment_group_name  = "${var.project_name}-${each.key}-dg"
  service_role_arn       = aws_iam_role.codedeploy.arn

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE"]
  }

  blue_green_deployment_config {
    deployment_ready_option {
      action_on_timeout = "CONTINUE_DEPLOYMENT"
    }

    terminate_blue_instances_on_deployment_success {
      action                           = "TERMINATE"
      termination_wait_time_in_minutes = 5
    }
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }

  ecs_service {
    cluster_name = each.value.cluster_name
    service_name = each.value.service_name
  }

  load_balancer_info {
    target_group_pair_info {
      prod_traffic_route {
        listener_arns = [each.value.listener_arn]
      }

      target_group {
        name = each.value.blue_target_group_name
      }

      target_group {
        name = each.value.green_target_group_name
      }
    }
  }
}
