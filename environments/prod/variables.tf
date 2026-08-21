variable "project_name" { type = string default = "terraform-infrastructure" }
variable "vpc_cidr" { type = string default = "10.30.0.0/16" }
variable "availability_zones" { type = list(string) default = ["ap-south-1a", "ap-south-1b"] }
variable "public_subnets" { type = list(string) default = ["10.30.1.0/24", "10.30.2.0/24"] }
variable "private_subnets" { type = list(string) default = ["10.30.11.0/24", "10.30.12.0/24"] }
variable "enable_nat_gateway" { type = bool default = false }
variable "tags" { type = map(string) default = { ManagedBy = "Terraform", Environment = "prod" } }
variable "aws_region" { type = string default = "ap-south-1" }
