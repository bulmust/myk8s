#!/bin/zsh
source ~/.zshrc

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=0.79.0
appNS=monitoring

# Install
helm upgrade --install\
    loki-distributed\
    grafana/loki-distributed\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer
