############################################
# GitHub OIDC Provider
############################################

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]
}


############################################
# Terraform State S3 Bucket
############################################

resource "aws_s3_bucket" "terraform_state" {
  bucket = var.state_bucket_name

  tags = {
    Name      = "Terraform Remote State"
    ManagedBy = "Terraform"
  }
}


############################################
# Enable Bucket Versioning
############################################

resource "aws_s3_bucket_versioning" "terraform_state" {

  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}


############################################
# Enable Encryption
############################################

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {

  bucket = aws_s3_bucket.terraform_state.id

  rule {

    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }

  }
}


############################################
# Block Public Access
############################################

resource "aws_s3_bucket_public_access_block" "terraform_state" {

  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}


############################################
# GitHub OIDC Trust Policy - PLAN
############################################

data "aws_iam_policy_document" "github_plan_assume_role" {

  statement {

    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {

      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {

      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:${var.github_org}/${var.github_repo}:*"
      ]
    }
  }
}


############################################
# Terraform PLAN Role
############################################

resource "aws_iam_role" "terraform_plan" {

  name = "terraform-github-plan-role"

  assume_role_policy = data.aws_iam_policy_document.github_plan_assume_role.json

  tags = {
    ManagedBy = "Terraform"
    Purpose   = "GitHub Terraform Plan"
  }
}


############################################
# GitHub OIDC Trust Policy - APPLY
############################################

data "aws_iam_policy_document" "github_apply_assume_role" {

  statement {

    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {
      type = "Federated"

      identifiers = [
        aws_iam_openid_connect_provider.github.arn
      ]
    }

    condition {

      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"

      values = [
        "sts.amazonaws.com"
      ]
    }

    condition {

      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:${var.github_org}/${var.github_repo}:*"
      ]
    }
  }
}


############################################
# Terraform APPLY Role
############################################

resource "aws_iam_role" "terraform_apply" {

  name = "terraform-github-apply-role"

  assume_role_policy = data.aws_iam_policy_document.github_apply_assume_role.json

  tags = {
    ManagedBy = "Terraform"
    Purpose   = "GitHub Terraform Apply"
  }
}


############################################
# PLAN Permissions
############################################

resource "aws_iam_role_policy_attachment" "plan_readonly" {

  role = aws_iam_role.terraform_plan.name

  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}


############################################
# APPLY Permissions
############################################

resource "aws_iam_role_policy_attachment" "apply_admin" {

  role = aws_iam_role.terraform_apply.name

  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}


############################################
# Terraform State Bucket Policy
############################################

data "aws_iam_policy_document" "terraform_state_access" {

  statement {

    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.terraform_state.arn
    ]
  }

  statement {

    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "${aws_s3_bucket.terraform_state.arn}/*"
    ]
  }
}


resource "aws_iam_policy" "terraform_state_access" {

  name = "terraform-state-access"

  policy = data.aws_iam_policy_document.terraform_state_access.json
}


resource "aws_iam_role_policy_attachment" "plan_state_access" {

  role       = aws_iam_role.terraform_plan.name
  policy_arn = aws_iam_policy.terraform_state_access.arn
}


resource "aws_iam_role_policy_attachment" "apply_state_access" {

  role       = aws_iam_role.terraform_apply.name
  policy_arn = aws_iam_policy.terraform_state_access.arn
}