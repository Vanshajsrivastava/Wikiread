apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: wikiread
  namespace: argocd
spec:
  project: default
  source:
    repoURL: REPO_URL
    targetRevision: TARGET_REVISION
    path: k8s/base
    kustomize:
      images:
        - wikiread=IMAGE_URI
  destination:
    server: https://kubernetes.default.svc
    namespace: wikiread
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
