variable "aws_region" {
  type        = string
  description = "AWS region."
  default     = "ap-south-1"
}

variable "project_name" {
  type        = string
  description = "Project name."
  default     = "terraform-infrastructure"
}

variable "environment" {
  type        = string
  description = "Deployment environment."
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR block."
}
