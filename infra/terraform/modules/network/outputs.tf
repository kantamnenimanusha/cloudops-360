output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "node_subnet_ids" {
  value = var.private_nodes ? aws_subnet.private[*].id : aws_subnet.public[*].id
}
