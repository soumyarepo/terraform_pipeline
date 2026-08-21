# Terraform AWS Infrastructure CI/CD

Production-oriented starter repository for Terraform on AWS with GitHub Actions.

## Workflow

1. Pull request triggers `terraform-plan.yml`.
2. Checkout and Terraform file validation.
3. `terraform init -upgrade`.
4. `terraform fmt -check -recursive`.
5. `terraform validate`.
6. `terraform plan` and JSON conversion.
7. Plan summary is posted to the PR.
8. Merge to `main` triggers `terraform-apply.yml`.
9. Production GitHub Environment approval can gate the apply.
10. Apply generates a deployment report artifact.

## Before first deployment

This repository is intentionally a safe starter and does not contain organization-specific AWS credentials, state buckets, or IAM role ARNs.

Configure:

- AWS IAM OIDC trust for GitHub Actions.
- `TERRAFORM_PLAN_ROLE_ARN` repository/environment variable.
- `TERRAFORM_APPLY_ROLE_ARN` repository/environment variable.
- `AWS_REGION`.
- A protected `production` GitHub Environment with required reviewers.
- An S3 remote backend in each environment.
- Commit generated `.terraform.lock.hcl` files after running Terraform init for your target platform.

## Important

Do not commit AWS access keys or Terraform state files.

The sample security group intentionally allows HTTPS from the internet; review it for your actual application requirements before production use.

The EC2, EKS and RDS modules are placeholders and are not deployed by default.

## Local validation

From an environment directory:

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
```
