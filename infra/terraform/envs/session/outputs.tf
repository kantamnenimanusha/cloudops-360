output "cluster_name" {
  value = module.eks.cluster_name
}

output "update_kubeconfig" {
  value = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}

output "backend_role_arn" {
  value = module.eks.backend_role_arn
}

output "ci_server_public_ip" {
  value = try(module.ci_server[0].public_ip, null)
}

output "ci_server_private_ip" {
  value = try(module.ci_server[0].private_ip, null)
}

output "ecr_registry" {
  value = "${data.aws_caller_identity.me.account_id}.dkr.ecr.${var.region}.amazonaws.com"
}
