#!/bin/zsh
source ~/.zshrc

# helm repo add grafana https://grafana.github.io/helm-charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=7.3.11
appNS=monitoring

# Install
helm upgrade --install\
    grafana\
    grafana/grafana\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer

# Apply the dashboards
kaf dashboard-root.yaml
