# Google Cloud Terraform Module Template

*Purpose: Safely provision and manage Google Cloud (GCP) resources with reusable Terraform/OpenTofu modules.*

## When to Use

- Provisioning GCP infrastructure (GCS, GKE, Cloud SQL, IAM, networking)
- Supporting environment promotion (dev → staging → prod)
- Enforcing consistent labels, IAM boundaries, and naming conventions

---

# TEMPLATE STARTS HERE

## `versions.tf`

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}
```

## `variables.tf`

```hcl
variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "Default region for regional resources"
  default     = "us-central1"
}

variable "labels" {
  type        = map(string)
  description = "Resource labels"
  default     = {}
}

variable "bucket_name_prefix" {
  type        = string
  description = "Prefix used to build a globally-unique bucket name"
}

variable "force_destroy" {
  type        = bool
  description = "Whether to allow Terraform to delete non-empty buckets (AVOID true in prod)"
  default     = false
}
```

## `main.tf` (example: GCS bucket)

```hcl
resource "random_id" "suffix" {
  byte_length = 4
}

resource "google_storage_bucket" "main" {
  name          = "${var.bucket_name_prefix}-${random_id.suffix.hex}"
  location      = var.region
  labels        = var.labels
  force_destroy = var.force_destroy

  uniform_bucket_level_access = true
}
```

## `outputs.tf`

```hcl
output "bucket_name" {
  value       = google_storage_bucket.main.name
  description = "Created bucket name"
}
```

## Provider Usage (root module)

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}
```

## `README.md` (snippet)

```hcl
module "assets_bucket" {
  source            = "./modules/gcs-bucket"
  project_id        = "acme-prod"
  bucket_name_prefix = "acme-assets-prod"
  labels            = { env = "prod", owner = "team-x" }
}
```

## Quality Checklist

- Bucket deletion is safe by default (`force_destroy = false`)
- All variables have descriptions and types
- `terraform fmt` + `terraform validate` run in CI
- Labels/tags are applied consistently for cost attribution and ownership
- IAM is least-privilege (prefer separate module for IAM bindings)
