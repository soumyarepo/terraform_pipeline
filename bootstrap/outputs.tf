output "terraform_plan_role_arn" {

  description = "GitHub Terraform Plan Role ARN"

  value = aws_iam_role.terraform_plan.arn
}


output "terraform_apply_role_arn" {

  description = "GitHub Terraform Apply Role ARN"

  value = aws_iam_role.terraform_apply.arn
}


output "terraform_state_bucket" {

  description = "Terraform state S3 bucket"

  value = aws_s3_bucket.terraform_state.bucket
}


output "github_oidc_provider_arn" {

  description = "GitHub OIDC Provider ARN"

  value = aws_iam_openid_connect_provider.github.arn
}