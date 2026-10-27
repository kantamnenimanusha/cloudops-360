terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.60, < 7.0" }
    tls = { source = "hashicorp/tls", version = ">= 4.0" }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "cloudops360", ManagedBy = "terraform", Stack = "session" }
  }
}

data "aws_caller_identity" "me" {}

locals {
  name = "cloudops360"
  ecr_repo_arns = [for r in ["orders-service", "inventory-service", "cloudops-backend", "cloudops-frontend"] :
  "arn:aws:ecr:${var.region}:${data.aws_caller_identity.me.account_id}:repository/cloudops/${r}"]
}

module "network" {
  source        = "../../modules/network"
  name          = local.name
  private_nodes = var.private_nodes
}

module "eks" {
  source             = "../../modules/eks"
  name               = local.name
  cluster_version    = var.cluster_version
  cluster_subnet_ids = module.network.public_subnet_ids
  node_subnet_ids    = module.network.node_subnet_ids
  admin_cidrs        = var.admin_cidrs
  desired_nodes      = var.node_count
}

module "ci_server" {
  count               = var.create_ci_server ? 1 : 0
  source              = "../../modules/ci_server"
  name                = local.name
  vpc_id              = module.network.vpc_id
  subnet_id           = module.network.public_subnet_ids[0]
  key_name            = var.key_name
  admin_cidrs         = var.admin_cidrs
  ecr_repository_arns = local.ecr_repo_arns
}
