#!/bin/zsh
source ~/.zshrc

# helm repo add eclipse-iot https://eclipse.org/packages/charts
# helm repo update

kcuc kind-myk8s

# Helm
appVer=1.6.0
appNS=hawkbit

# Install
helm upgrade --install\
    hawkbit\
    eclipse-iot/hawkbit\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml\
    --version=$appVer

# Ingress
kubectl apply -f ingress.yaml