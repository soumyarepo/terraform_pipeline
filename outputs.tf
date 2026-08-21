output "vpc_id" {
  description = "Created VPC ID."
  value       = module.vpc.vpc_id
}

output "security_group_id" {
  description = "Created security group ID."
  value       = module.security_groups.security_group_id
}
