module "vpc" {
  source = "../../modules/vpc"

  name               = "${var.project_name}-staging"
  cidr_block         = var.vpc_cidr
  availability_zones = var.availability_zones
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  enable_nat_gateway = var.enable_nat_gateway
  tags               = var.tags
}

module "security_groups" {
  source = "../../modules/security-groups"

  name   = "${var.project_name}-staging"
  vpc_id = module.vpc.vpc_id
  tags   = var.tags
}
