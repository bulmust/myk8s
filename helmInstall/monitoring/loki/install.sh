#!/bin/zsh
source ~/.zshrc

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=6.6.2
appNS=monitoring

# Install
helm upgrade --install\
    loki\
    grafana/loki\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer