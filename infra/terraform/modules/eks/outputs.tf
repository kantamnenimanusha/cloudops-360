output "cluster_name" {
  value = aws_eks_cluster.this.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.this.endpoint
}

output "backend_role_arn" {
  value = aws_iam_role.backend.arn
}
