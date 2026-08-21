module "vpc" {
  source = "./modules/vpc"

  name       = "${var.project_name}-${var.environment}"
  cidr_block = var.vpc_cidr
}

module "security_groups" {
  source = "./modules/security-groups"

  name   = "${var.project_name}-${var.environment}-app"
  vpc_id = module.vpc.vpc_id
}
