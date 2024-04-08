# myk8s

My personal dev k8s.

## Folders

- `create-kind-cluster` Script to create a kind cluster.
  - `manifests` K8s manifests.
  - `certificates` self signed certificate for ingress.
  - Run `./kind-1CP2W-Ingress.sh` to create 1 control panel, 2 worker nodes kind cluster. Follow instructions.
- `docs` Documentation.
- `clusters` Clusters and its helm related files. The structure is as follows:
  - `cluster-name` Cluster name. `kind-myk8s` is our cluster name.
    - `namespace` Namespaces in the cluster.
      - `application-name` application names in cluster. It can be a Helm chart (must have `values.yaml` and `chart.yaml` files) or K8s manifests.
- `helm-offline.py` Script to download helm charts, images in the charts, creates a tarball, uploads to a local registry and more.
  - Run `./helm-offline.py --help` to see the options.