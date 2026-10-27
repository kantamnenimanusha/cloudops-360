# Run ONCE with local state. Creates the private, versioned, encrypted S3 bucket that holds Terraform state for the other roots.
# Cost: cents per month. Locking uses S3 native lock files (Terraform >= 1.10), so no DynamoDB table is needed.
terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.60, < 7.0" }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "cloudops360", ManagedBy = "terraform", Stack = "bootstrap" }
  }
}

variable "region" {
  type = string
}

variable "state_bucket_name" {
  type        = string
  description = "Globally unique bucket name, e.g. cloudops360-tfstate-<random>"
}

resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "state_bucket" {
  value = aws_s3_bucket.state.bucket
}
