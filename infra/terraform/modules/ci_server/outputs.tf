output "instance_id" {
  value = aws_instance.ci.id
}

output "public_ip" {
  value = aws_instance.ci.public_ip
}

output "private_ip" {
  value = aws_instance.ci.private_ip
}
