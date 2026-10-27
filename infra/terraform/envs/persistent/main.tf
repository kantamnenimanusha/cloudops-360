terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.60, < 7.0" }
  }
  # After running bootstrap, copy backend.tf.example to backend.tf, fill it in, then `terraform init -migrate-state`.
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "cloudops360", ManagedBy = "terraform", Stack = "persistent" }
  }
}

variable "region" {
  type = string
}

variable "budget_email" {
  type = string
}

module "ecr" {
  source = "../../modules/ecr"
}

module "budget" {
  source = "../../modules/budget"
  email  = var.budget_email
}

output "repository_urls" {
  value = module.ecr.repository_urls
}
