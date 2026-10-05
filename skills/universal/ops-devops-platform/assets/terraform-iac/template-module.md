# Terraform/OpenTofu Module Template

*Purpose: Standardize reusable, testable, and safe infrastructure modules across providers and environments.*

## When to Use

- Building cloud/network/database resources with Terraform/OpenTofu
- Enforcing DRY IaC (reusable patterns + consistent interfaces)
- Supporting multi-env or multi-region deployments with clear inputs/outputs

---

# TEMPLATE STARTS HERE

## Recommended Layout

```text
modules/<module-name>/
  main.tf
  variables.tf
  outputs.tf
  versions.tf
  README.md
```

## `versions.tf` (example)

```hcl
terraform {
  required_version = ">= 1.5.0"
}
```

## `variables.tf` (example)

```hcl
variable "name" {
  type        = string
  description = "Resource name"
}

variable "tags" {
  type        = map(string)
  description = "Resource tags/labels"
  default     = {}
}
```

## `main.tf` (example: AWS S3 bucket)

```hcl
resource "aws_s3_bucket" "main" {
  bucket = var.name
  tags   = var.tags
}
```

## `outputs.tf` (example)

```hcl
output "bucket_arn" {
  value       = aws_s3_bucket.main.arn
  description = "Bucket ARN"
}
```

## `README.md` (snippet)

```hcl
module "bucket" {
  source = "./modules/s3-bucket"
  name   = "my-bucket"
  tags   = { environment = "prod", owner = "platform" }
}
```

## Quality Checklist

- Inputs are minimal, typed, and documented (avoid giant `any` objects)
- Defaults are safe (no destructive deletes or public exposure by default)
- Output names are stable and documented (treat as API surface)
- CI runs `terraform fmt` + `terraform validate` (+ optional `tflint`/policy checks)
- Secrets are never inputs in plaintext (use secret managers; pass references/IDs)
- Providers are configured in the root module; modules stay provider-agnostic where possible

## Related Templates

- [template-env-promotion.md](template-env-promotion.md) — Environment promotion workflow patterns
- [../cicd-pipelines/template-ci-cd.md](../cicd-pipelines/template-ci-cd.md) — CI/CD gates (SAST/DAST/SCA)
- [../cicd-pipelines/template-github-actions.md](../cicd-pipelines/template-github-actions.md) — GitHub Actions workflow template
