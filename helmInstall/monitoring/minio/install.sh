#!/bin/zsh
source ~/.zshrc

# helm repo add minio https://charts.min.io/
# helm repo update

kcuc kind-myk8s

# Helm
appVer=5.2.0
appNS=monitoring

# Install
helm upgrade --install\
    minio\
    minio/minio-operator\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer