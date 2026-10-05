```markdown
# Terraform & IaC Template (DevOps)

*Purpose: A complete, production-ready template for building, testing, reviewing, and deploying Infrastructure-as-Code (IaC) using Terraform.*

---

# 1. Overview

**Infrastructure Component:**  
[e.g., VPC, cluster, database, service mesh]

**Purpose of Change:**  
[Describe what this Terraform update or module accomplishes]

**Environment:**  
- [ ] dev  
- [ ] staging  
- [ ] prod  
- [ ] multi-region  

**Change Type:**  
- [ ] New module  
- [ ] Modify module  
- [ ] Environment deployment  
- [ ] Provider upgrade  
- [ ] Infra migration  
- [ ] Bug fix  

---

# 2. Terraform Module Specification

## 2.1 Module Structure

```

modules/
  <module-name>/
    main.tf
    variables.tf
    outputs.tf
envs/
  dev/
  staging/
  prod/

```

**Checklist:**
- [ ] No hardcoded values  
- [ ] All variables typed  
- [ ] Outputs minimal and non-sensitive  
- [ ] Provider defined at root, not inside modules  
- [ ] No circular dependencies  

---

## 2.2 Variables & Inputs

```

variable "environment" {
  type    = string
}
variable "region" {
  type    = string
}
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

```

**Checklist:**
- [ ] Defaults only when safe  
- [ ] Validate blocks used  
- [ ] Sensitive = true for credentials  

---

## 2.3 Outputs

```

output "service_endpoint" {
  value = aws_lb.main.dns_name
}

```

**Checklist:**
- [ ] Avoid leaking secrets  
- [ ] Avoid huge JSON structures  
- [ ] Document use cases  

---

# 3. Backend & State

## 3.1 Remote Backend Example (AWS S3)

```

terraform {
  backend "s3" {
    bucket         = "infra-state"
    key            = "prod/network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

```

**Checklist:**
- [ ] Backend unique per environment  
- [ ] State locked (DynamoDB/Blob Locks)  
- [ ] Encryption enabled  
- [ ] State access restricted  
- [ ] State not checked into version control  

---

## 3.2 State Files Safety

- [ ] Never edit manually  
- [ ] Backed up automatically  
- [ ] Encrypted at rest  
- [ ] Lifecycle policies enabled  

---

# 4. Provider Management

```

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

```

**Checklist:**
- [ ] Pin provider versions  
- [ ] Review provider release notes before upgrade  
- [ ] Avoid “latest” tags  

---

# 5. Secret Handling

### Approved Methods
- AWS SSM Parameter Store  
- AWS Secrets Manager  
- HashiCorp Vault  
- KMS-encrypted files  
- GitHub Actions OIDC + cloud IAM roles  

### Example (SSM):

```

data "aws_ssm_parameter" "db_password" {
  name            = "/prod/db/password"
  with_decryption = true
}

```

**Checklist:**
- [ ] No secrets in variables.tf  
- [ ] No secrets in tfvars checked into repo  
- [ ] No cleartext secrets in state  
- [ ] Sensitive marked true  

---

# 6. Terraform Workflow

```

terraform fmt -check
terraform init -upgrade
terraform validate
tflint
checkov -d .
terraform plan -out plan.tfplan
terraform show plan.tfplan
terraform apply plan.tfplan

```

---

# 7. CI/CD Integration

## 7.1 Example GitHub Actions Workflow

```

name: Terraform Plan & Apply
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Setup Terraform
      uses: hashicorp/setup-terraform@v3

    - name: Init
      run: terraform init

    - name: Validate
      run: terraform validate

    # Plan and apply run in the SAME job so the binary plan file never leaves
    # the runner: Terraform plan files store every secret passed to a resource
    # or data source in plain text, so uploading one as a build artifact
    # publishes those secrets to anyone who can read the artifact.
    - name: Plan
      run: terraform plan -out plan.tfplan

    # Share the human-readable diff for review, never the binary plan.
    # `-no-color` keeps it diffable; values marked `sensitive = true` are
    # redacted by `terraform show`, so mark every secret-bearing variable
    # and output sensitive before relying on this.
    - name: Render plan for review (secrets masked)
      run: terraform show -no-color plan.tfplan > plan.txt

    - name: Post plan to PR
      if: github.event_name == 'pull_request'
      run: gh pr comment "$PR" --body-file plan.txt
      env:
        PR: ${{ github.event.pull_request.number }}
        GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Apply (manual approval)
      if: github.ref == 'refs/heads/main'
      environment: production   # GitHub environment gate = required reviewer
      run: terraform apply plan.tfplan

```

### CI Checklist

- [ ] Plan file (`*.tfplan`) treated as a secret-bearing artifact — never uploaded unencrypted, never committed, never emailed. Keep it inside one job, or store it encrypted at rest and in transit with access controls as tight as those on the secrets themselves
- [ ] Only the `terraform show` text output is shared for review, with every secret-bearing variable and output marked `sensitive = true`
- [ ] Require manual approval for apply
- [ ] Run tfsec/checkov
- [ ] Use IAM roles, not secrets
- [ ] Persistent caching for terraform providers

> **Why:** Brikman, *Terraform: Up & Running* (3e), Ch6, "Plan files": "just as with Terraform state, any secrets you pass into your Terraform resources and data sources will end up in plain text in your Terraform plan files!" He requires that saved plan files be encrypted in transit and on disk, and that access be controlled "with at least as much care as you control access to the secrets themselves." The same chapter notes state files have the identical property — "All data in Terraform state files is stored in plain text."

---

# 8. Testing Terraform

## 8.1 Static Tests
- `terraform validate`  
- `terraform fmt`  
- `tflint`  
- `checkov`  

## 8.2 Integration Tests (Terratest)

Example:
```

func TestInfra(t *testing.T) {
  terraformOptions := &terraform.Options{
    TerraformDir: "../modules/network",
  }
  terraform.InitAndApply(t, terraformOptions)
}

```

---

# 9. Drift Detection

**Method 1:**  
```

terraform plan -detailed-exitcode

```

Interpretation:
- Exit 0: No changes  
- Exit 1: Error  
- Exit 2: Drift detected  

**Checklist:**
- [ ] Output drift alerts to Slack  
- [ ] Document required fixes  
- [ ] Never apply automatically on drift  

---

# 10. Rollback Plan (Infra)

### Rollback Methods
- Redeploy previous module version  
- Use state snapshots (carefully)  
- Revert Git commit → re-apply  
- Restore from backup (RDS/cluster)  

### Rollback Checklist

- [ ] Rollback tested in staging  
- [ ] Zero downtime confirmed  
- [ ] State restored in controlled way  
- [ ] Dependencies verified (network/db)  

---

# 11. Examples

## 11.1 Standard Resource Example

```

resource "aws_instance" "app" {
  ami           = "ami-123456789"
  instance_type = var.instance_type
  tags = {
    Name = "app"
    Env  = var.environment
  }
}

```

---

## 11.2 Network Example

```

resource "aws_vpc" "main" {
  cidr_block = var.cidr
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.public_subnet_cidr
}

```

---

## 11.3 Terraform Destroy Safety

- [ ] Never allow destroy in prod  
- [ ] Use `-target=` for safe partial deletes  
- [ ] Use lifecycle `prevent_destroy` for critical resources  

Example:
```

resource "aws_db_instance" "prod" {
  lifecycle {
    prevent_destroy = true
  }
}

```

---

# 12. Final Review Checklist

### Module Quality
- [ ] No hardcoded values  
- [ ] Variables clearly typed  
- [ ] Outputs minimal  
- [ ] Providers pinned  

### Security
- [ ] Secrets handled securely  
- [ ] Backends encrypted  
- [ ] IAM least-privilege  

### Reliability
- [ ] Drift detection configured  
- [ ] State locking enabled  
- [ ] Rollback documented  

### CI/CD
- [ ] Plan stored as artifact  
- [ ] Apply gated behind approval  
- [ ] Tests & scans included  

---

# END
```
