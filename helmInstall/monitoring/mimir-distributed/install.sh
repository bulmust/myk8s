#!/bin/zsh
source ~/.zshrc

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=5.3.0
appNS=monitoring

# Install
helm upgrade --install\
    mimir-distributed\
    grafana/mimir-distributed\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer
