#!/bin/zsh
source ~/.zshrc

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=6.15.5
appNS=monitoring

# Install
helm upgrade --install\
    promtail\
    grafana/promtail\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer
