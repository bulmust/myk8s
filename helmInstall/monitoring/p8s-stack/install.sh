#!/bin/zsh
source ~/.zshrc

# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=59.0.0
appNS=monitoring

# Install
helm upgrade --install\
    p8s-stack\
    prometheus-community/kube-prometheus-stack\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer

