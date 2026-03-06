# Wikiread Architecture Diagram

- Source file: `docs/architecture/wikiread-aws-architecture.mmd`
- Open in Mermaid Live Editor: https://mermaid.live/
- Paste the file content and export as SVG/PNG for your portfolio.

## What this diagram shows

- Terraform provisioning and state backend
- Infra approval flow (CodeBuild Plan -> SNS -> Manual Approval -> Apply)
- App CI/CD flow (CodeBuild Build -> ECR -> Argo CD sync)
- EKS runtime with Argo Rollouts blue/green services and HPA
- Private RDS and Secrets Manager integration
