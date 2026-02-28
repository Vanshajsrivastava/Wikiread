# Wikiread

Wikiread is a Django application deployed on AWS EKS with GitOps delivery (Argo CD + Argo Rollouts), Terraform-based infrastructure provisioning, and CI/CD using CodePipeline + CodeBuild.

## What this project provisions

Terraform in `infra/terraform` creates:

- VPC with public, private-app, and private-db subnets
- Internet Gateway + NAT Gateway routing
- EKS cluster and managed node group
- ECR repository for app images
- RDS PostgreSQL (private, not publicly accessible)
- Secrets Manager app secret (`<name>/app-secrets`)
- S3 buckets for pipeline artifacts and Terraform plans
- SNS topic + email subscription for plan review notifications
- CodeBuild projects (app build/deploy, infra plan/apply)
- CodePipeline pipelines (app and infra)
- EKS addons (optional): `metrics-server`, `amazon-cloudwatch-observability`

## Architecture summary

- App traffic enters via `wikiread-active` Kubernetes Service (`LoadBalancer`, NLB, internet-facing).
- App pods run in private app subnets on EKS worker nodes.
- Database runs in private DB subnets and accepts traffic only from EKS node security group.
- Outbound internet from private subnets goes via NAT.
- Argo CD continuously syncs desired Kubernetes state from this Git repo.
- Argo Rollouts handles blue/green delivery using active and preview services.

## Repository structure

- `infra/terraform`: Infrastructure as Code
- `infra/terraform/modules/network`: VPC/subnet/NAT module
- `infra/terraform/modules/rds`: RDS + secret module
- `infra/terraform/modules/observability`: EKS addons/IRSA
- `ci/buildspec.*.yml`: CodeBuild workflows
- `k8s/base`: Kubernetes app manifests (Kustomize base)
- `k8s/argocd/application.yaml.tpl`: Argo CD Application template

## Kubernetes manifest roles

- `k8s/base/namespace.yaml`: creates `wikiread` namespace
- `k8s/base/configmap.yaml`: non-sensitive app config (`DEBUG`, `ALLOWED_HOSTS`, `PORT`)
- `k8s/base/rollout.yaml`: Argo Rollouts `Rollout` for blue/green deployment
- `k8s/base/service-active.yaml`: public service (active version)
- `k8s/base/service-preview.yaml`: internal preview service for rollout promotion
- `k8s/base/hpa.yaml`: HorizontalPodAutoscaler targeting the Rollout
- `k8s/base/kustomization.yaml`: Kustomize entrypoint
- `k8s/base/secret.example.yaml`: local example only (real secret is generated from Secrets Manager by deploy job)

## CI/CD flow

### App pipeline (`<project>-<env>-app-pipeline`)

1. Source from GitHub via CodeStar connection.
2. Build (`ci/buildspec.app-build.yml`):
   - builds Docker image
   - pushes image to ECR
   - outputs `out/image-uri.txt`
3. Deploy (`ci/buildspec.app-deploy.yml`):
   - connects to EKS
   - reads app secret JSON from Secrets Manager
   - creates/updates Kubernetes `wikiread-secrets`
   - renders `k8s/argocd/application.yaml.tpl` with image URI
   - applies Argo CD Application and forces refresh

### Infra pipeline (`<project>-<env>-infra-pipeline`)

1. Source from GitHub via CodeStar connection.
2. Plan (`ci/buildspec.infra-plan.yml`):
   - `terraform init/fmt/validate/plan`
   - uploads plan text to S3 (`tf-plans` bucket)
   - sends SNS email with plan location
3. Manual approval stage:
   - reviewer approves/rejects in CodePipeline
4. Apply (`ci/buildspec.infra-apply.yml`):
   - `terraform apply -auto-approve`

## SNS approval model

- Terraform plan stage sends notification to `manager_email` using SNS.
- Email is for notification and plan review link.
- Actual approve/reject action requires AWS IAM login with `codepipeline:PutApprovalResult`.

## Argo CD and Rollouts

Important: current deploy buildspec assumes Argo CD exists in the cluster.

One-time bootstrap example:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm upgrade --install argocd argo/argo-cd -n argocd --create-namespace
helm upgrade --install argo-rollouts argo/argo-rollouts -n argo-rollouts --create-namespace
```

After bootstrap, app deployment is handled by the pipeline + Argo sync.

## Prerequisites

- AWS account and IAM user/role with required permissions
- GitHub repository access
- AWS CodeConnections connection to GitHub
- Terraform >= 1.6
- AWS CLI + kubectl + helm (for operator actions)

## Initial setup

1. Configure backend resources for Terraform state:
   - S3 bucket for state
   - DynamoDB table for state lock
2. Update backend values in `infra/terraform/versions.tf` for your account/region.
3. Create environment var file:

```bash
cp infra/terraform/env/prod-eu-west-2.tfvars.example infra/terraform/env/prod-eu-west-2.tfvars
```

4. Fill required values:
   - `repo_owner`, `repo_name`, `repo_branch`
   - `codestar_connection_arn`
   - `manager_email`
   - `db_password`
   - sizing/scaling variables (`node_instance_types`, min/desired/max, NAT/AZ counts)

5. Run provisioning:

```bash
cd infra/terraform
terraform init
terraform plan -var-file=env/prod-eu-west-2.tfvars
terraform apply -var-file=env/prod-eu-west-2.tfvars
```

6. Confirm SNS email subscription.
7. Update Secrets Manager secret with valid `SECRET_KEY` and `DATABASE_URL`.

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a
python manage.py migrate
python manage.py runserver
```

Optional import from markdown files:

```bash
python manage.py import_entries
```

## Destroy

```bash
cd infra/terraform
terraform destroy -var-file=env/prod-eu-west-2.tfvars
```

If lock exists, clear lock before retry (`terraform force-unlock`).

## Security and production hardening

- Replace broad `AdministratorAccess` on CodeBuild role with least privilege.
- Restrict `allowed_cidrs_for_eks_api` from `0.0.0.0/0`.
- Add HTTPS (ACM + ingress/load balancer config).
- Add WAF, backup/DR policy, and secret rotation strategy.
- Add policy checks and tests in pipeline before apply/deploy.
