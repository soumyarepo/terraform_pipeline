# Backend configuration is intentionally environment-specific.
# Configure the S3 backend in each environment before a real deployment.
#
# Example:
# terraform {
#   backend "s3" {
#     bucket       = "YOUR-ORG-terraform-state"
#     key          = "YOUR-ENV/terraform.tfstate"
#     region       = "ap-south-1"
#     encrypt      = true
#     use_lockfile = true
#   }
# }
