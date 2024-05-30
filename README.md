# myk8s

My personal dev k8s cluster.

>Check `values.yaml` for the explanation of what I have done.

## Folders

- `create-kind-cluster` Script to create a kind cluster.
  - `manifests` K8s manifests.
  - `certificates` self signed certificate for ingress.
  - Run `./kind-1CP2W-Ingress.sh` to create 1 control panel, 2 worker nodes kind cluster. Follow instructions.
- `helmInstall` helm related files. These are helm values file (must have `values.yaml`), installation script and/or k8s manifests.
  - The structure is as follows: `helmInstall/<namespace>/<application-name>`.