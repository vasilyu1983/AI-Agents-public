```markdown
# AWS Terraform Module Template

*Purpose: Safely automate AWS resource provisioning (EC2, RDS, S3, IAM, etc.) with reusable modules.*

## When to Use
- New AWS service deployments
- IaC for scalable/ephemeral infrastructure
- Secure, auditable production changes

---

# TEMPLATE STARTS HERE

## variables.tf
```hcl
variable "region"      { type = string; default = "us-east-1" }
variable "tags"        { type = map(string); default = {} }
variable "bucket_name" { type = string }
main.tf (example: S3 Bucket)

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name
  tags   = var.tags
}

output "bucket_arn" { value = aws_s3_bucket.main.arn }
README.md (snippet)

module "bucket" {
  source      = "./modules/s3"
  bucket_name = "acme-app-prod-assets"
  tags        = { Environment = "prod", Owner = "team-y" }
}
Quality Checklist

 AWS credentials provided via environment or secrets manager
 Remote state (S3 + DynamoDB) configured for production
 Plan and apply peer-reviewed
 IAM roles use least privilege for module resources
---

## `assets/cloud/template-azure-terraform.md`
```markdown
# Azure Terraform Module Template

*Purpose: Automate and version Azure resource deployment (storage, compute, networking, RBAC) with secure, modular IaC.*

## When to Use
- Provisioning Azure resources via CI/CD
- Environment promotion and compliance
- RBAC, networking, storage automation

---

# TEMPLATE STARTS HERE

## variables.tf
```hcl
variable "resource_group_name" { type = string }
variable "location"            { type = string; default = "eastus" }
variable "tags"                { type = map(string); default = {} }
main.tf (example: Storage Account)

provider "azurerm" {
  features = {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "azurerm_storage_account" "main" {
  name                     = "${var.resource_group_name}sa"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  tags                     = var.tags
}
outputs.tf

output "storage_account_name" { value = azurerm_storage_account.main.name }
README.md (snippet)

module "storage" {
  source               = "./modules/azure-storage"
  resource_group_name  = "my-app-prod"
  tags                 = { environment = "prod", owner = "team-z" }
}
Quality Checklist

 Provider and resource group created with correct permissions
 State stored securely (Azure Blob, key vault, etc.)
 Secrets not hardcoded
 Peer review and CI plan before production apply

