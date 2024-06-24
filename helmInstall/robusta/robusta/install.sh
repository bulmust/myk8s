#!/bin/zsh
source ~/.zshrc

#helm repo add robusta https://robusta-charts.storage.googleapis.com && helm repo update

kcuc kind-myk8s

# Helm
appVer=0.13.1
appNS=monitoring

# Install
helm upgrade --install\
    robusta\
    robusta/robusta\
    --debug\
    --namespace=$appNS --create-namespace\
    -f values.yaml~\
    --version=$appVer