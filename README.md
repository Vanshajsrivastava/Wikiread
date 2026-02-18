# Wikiread

A Django-based wiki app with markdown entries stored in a relational database.

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a
python manage.py migrate
python manage.py runserver
```

To import old markdown files from `entries/*.md` into DB:

```bash
python manage.py import_entries
```

## Current app architecture

This repository contains a Django web service (`encyclopedia` app inside `wiki` project), with relational DB support through `DATABASE_URL` (PostgreSQL recommended in production).

## Deployment model (Argo CD + EKS)

This repo now uses Argo-based GitOps deployment:

- `CodePipeline + CodeBuild` builds and pushes container image to ECR.
- Deploy stage bootstraps/updates:
  - Argo CD
  - Argo Rollouts
  - `wikiread-secrets` from AWS Secrets Manager
  - Argo CD `Application` (`k8s/argocd/application.yaml.tpl`)
- Argo CD syncs Kubernetes manifests from this repo (`k8s/base`).
- Blue/green is handled by Argo Rollouts (`k8s/base/rollout.yaml`).

## Kubernetes manifests

- `k8s/base/namespace.yaml`
- `k8s/base/configmap.yaml`
- `k8s/base/service-active.yaml` (public NLB)
- `k8s/base/service-preview.yaml`
- `k8s/base/rollout.yaml` (Argo Rollouts blue/green)
- `k8s/base/hpa.yaml` (horizontal pod autoscaling for the rollout)
- `k8s/base/kustomization.yaml`
- `k8s/base/secret.example.yaml` (example only; real secret is generated from Secrets Manager)
- `k8s/argocd/application.yaml.tpl`

## AWS target design

- App workloads run on EKS worker nodes in private subnets.
- Database (RDS PostgreSQL) is private (`publicly_accessible = false`) in private DB subnets.
- Public access to app is through `wikiread-active` Service (internet-facing NLB).
- Private subnets use NAT for outbound internet when needed.

## Terraform contents

`infra/terraform` provisions:

- VPC, subnets (public/private app/private DB), IGW, NAT
- EKS cluster + managed node group
- ECR repository
- Private RDS PostgreSQL
- AWS Secrets Manager app secret
- CodeBuild projects
- App/infra CodePipelines
- SNS topic + email subscription + manual approval gate for infra changes

Terraform modules:

- EKS uses `terraform-aws-modules/eks/aws`
- The rest of the stack is parameterized through variables (not hardcoded) so you can tune counts/sizes per environment.

## Terraform usage

1. Copy vars (single-file option):

```bash
cp infra/terraform/terraform.tfvars.example infra/terraform/terraform.tfvars
```

2. Fill required values in `infra/terraform/terraform.tfvars`.

Alternative environment var files:

- `infra/terraform/env/dev-eu-west-2.tfvars.example`
- `infra/terraform/env/prod-eu-west-2.tfvars.example`

Use with:

```bash
cd infra/terraform
terraform init
terraform plan -var-file=env/prod-eu-west-2.tfvars
terraform apply -var-file=env/prod-eu-west-2.tfvars
```

3. Apply:

```bash
cd infra/terraform
terraform init
terraform plan
terraform apply
```

4. Confirm SNS email subscription for `manager_email`.

5. Update Secrets Manager value (`<project>-<env>/app-secrets`) with:
   - `SECRET_KEY`
   - `DATABASE_URL`

## CI/CD flow

### App pipeline (`<project>-<env>-app-pipeline`)

1. Source from GitHub via CodeStar connection.
2. Build (`ci/buildspec.app-build.yml`):
   - Build Docker image
   - Push image to ECR
   - Output built image URI artifact
3. Deploy (`ci/buildspec.app-deploy.yml`):
   - Connect to EKS
   - Install/upgrade Argo CD + Argo Rollouts
   - Sync Kubernetes secret from Secrets Manager
   - Render/apply Argo CD Application with the built image URI
   - Trigger Argo CD refresh

### Infra pipeline (`<project>-<env>-infra-pipeline`)

1. Source from GitHub.
2. Plan (`ci/buildspec.infra-plan.yml`):
   - `terraform plan`
   - Upload plan text to S3
   - Send SNS email with plan location
3. Manual approval stage:
   - Manager approves/rejects
4. Apply (`ci/buildspec.infra-apply.yml`):
   - `terraform apply -auto-approve`

## Notes on CodeDeploy

For EKS, this implementation uses Argo CD/Argo Rollouts for deployments and blue/green control. CodeDeploy remains unnecessary in this path.

## Helm usage

Yes, Helm is used in `ci/buildspec.app-deploy.yml` to install/upgrade:

- Argo CD chart
- Argo Rollouts chart

Why Helm helps here:

- versioned installs/upgrades
- reusable chart values/config
- repeatable cluster bootstrapping from CI

## Recommended hardening

- Replace `AdministratorAccess` IAM policy for CodeBuild with least-privilege IAM.
- Restrict EKS API CIDRs (`allowed_cidrs_for_eks_api`).
- Add remote Terraform state backend (S3 + DynamoDB lock).
- Add HTTPS/ACM/WAF and external DNS/Route53 integration.
