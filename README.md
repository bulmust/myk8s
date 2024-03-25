# myk8s

My personal dev k8s.

## Folders

- `create-kind-cluster` Script to create a kind cluster.
  - `manifests` K8s manifests.
  - `certificates` self signed certificate for ingress.
  - Run `./kind-1CP2W-Ingress.sh` to create 1 control panel, 2 worker nodes kind cluster. Follow instructions.
- `docs` Documentation.
- `apps` Applications, deployed via Helm, manifests, argocd etc.
  - `default-values` Default values for helm charts.

