resource "aws_s3_bucket" "this" {
  bucket = "${var.project_name}-static-frontend"

  tags = {
    Project = var.project_name
    Owner   = var.owner
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
