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
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:soumyarepo@36677493/terraform_pipeline@1341957863:pull_request"
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
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"

      values = [
        "repo:soumyarepo@36677493/terraform_pipeline@1341957863:environment:production"
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
# APPLY Least Privilege Policy Document
############################################

data "aws_iam_policy_document" "terraform_apply_permissions" {

  ############################################
  # VPC / Networking Permissions
  ############################################

  statement {
    effect = "Allow"

    actions = [
      "ec2:CreateVpc",
      "ec2:DeleteVpc",
      "ec2:DescribeVpcs",
      "ec2:DescribeVpcAttribute",
      "ec2:ModifyVpcAttribute",

      "ec2:CreateSubnet",
      "ec2:DeleteSubnet",
      "ec2:DescribeSubnets",
      "ec2:ModifySubnetAttribute",

      "ec2:CreateInternetGateway",
      "ec2:DeleteInternetGateway",
      "ec2:AttachInternetGateway",
      "ec2:DetachInternetGateway",
      "ec2:DescribeInternetGateways",

      "ec2:CreateRouteTable",
      "ec2:DeleteRouteTable",
      "ec2:DescribeRouteTables",
      "ec2:AssociateRouteTable",
      "ec2:DisassociateRouteTable",
      "ec2:CreateRoute",
      "ec2:DeleteRoute",
      "ec2:ReplaceRoute",

      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:DescribeSecurityGroups",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:AuthorizeSecurityGroupEgress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupEgress",

      "ec2:CreateTags",
      "ec2:DeleteTags",
      "ec2:DescribeTags",

      "ec2:DescribeAvailabilityZones",
      "ec2:DescribeNetworkInterfaces"
    ]

    resources = ["*"]
  }
}


############################################
# Create APPLY Least Privilege IAM Policy
############################################

resource "aws_iam_policy" "terraform_apply_permissions" {
  name        = "terraform-github-apply-policy"
  description = "Least privilege permissions for Terraform GitHub Actions apply"

  policy = data.aws_iam_policy_document.terraform_apply_permissions.json
}


############################################
# Attach APPLY Least Privilege Policy
############################################

resource "aws_iam_role_policy_attachment" "terraform_apply_permissions" {
  role       = aws_iam_role.terraform_apply.name
  policy_arn = aws_iam_policy.terraform_apply_permissions.arn
}


############################################
# Terraform State Bucket Policy
############################################

data "aws_iam_policy_document" "terraform_state_access" {

  statement {
    effect = "Allow"

    actions = [
      "s3:ListBucket",
      "s3:GetBucketVersioning"
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


############################################
# Create Terraform State Access Policy
############################################

resource "aws_iam_policy" "terraform_state_access" {
  name = "terraform-state-access"

  policy = data.aws_iam_policy_document.terraform_state_access.json
}


############################################
# Attach State Policy to PLAN Role
############################################

resource "aws_iam_role_policy_attachment" "plan_state_access" {
  role       = aws_iam_role.terraform_plan.name
  policy_arn = aws_iam_policy.terraform_state_access.arn
}


############################################
# Attach State Policy to APPLY Role
############################################

resource "aws_iam_role_policy_attachment" "apply_state_access" {
  role       = aws_iam_role.terraform_apply.name
  policy_arn = aws_iam_policy.terraform_state_access.arn
}