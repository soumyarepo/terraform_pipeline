# Terraform Infrastructure — Final CI/CD Project

## Pipeline sequence

Feature branch → Pull Request → Terraform Plan → plan table in PR → reviewer approval → merge to `main` → production approval gate → Terraform Apply → deployment table → HTML email.

## GitHub repository variables

Configure these under **Settings → Secrets and variables → Actions → Variables**:

- `AWS_REGION` (example: `ap-south-1`)
- `TERRAFORM_VERSION` (example: `1.12.2`)
- `TERRAFORM_PLAN_ROLE_ARN`
- `TERRAFORM_APPLY_ROLE_ARN`
- `TF_STATE_BUCKET`

## GitHub Actions secrets for email

- `SMTP_HOST`
- `SMTP_PORT` (`587` for STARTTLS or `465` for SSL)
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

## AWS prerequisites

1. Configure GitHub Actions OIDC in AWS IAM.
2. Create a plan IAM role and an apply IAM role with appropriate least-privilege policies.
3. Create the S3 state bucket and enable versioning/encryption.
4. Configure the GitHub `production` Environment with required reviewers.
5. Protect `main` so changes are merged through approved Pull Requests.

## Important

The PR and Apply workflows both plan the **production tfvars** so the reviewer sees the same target environment that is later applied. The apply workflow creates a fresh plan from the approved merged commit and immediately applies that exact saved plan.

`main.tf` is included because a runnable root Terraform module must instantiate the VPC and security-group modules. EC2, EKS and RDS are provided as module placeholders and are not enabled by default.
