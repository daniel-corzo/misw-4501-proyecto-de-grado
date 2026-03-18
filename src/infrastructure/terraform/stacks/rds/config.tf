provider "aws" {
  region = var.region

  default_tags {
    tags = {
      terraform = true
      owner     = var.owner
      project   = var.project_name
    }
  }
}

terraform {
  required_version = "~> 1.13"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3"
    }
  }

  backend "s3" {}
}
