#!/bin/bash
# Check the current context is myk8s. If not, switch to it.
echo ">>>Checking current context..."
if [ "$(kubectl config current-context)" != "kind-myk8s" ]; then
    echo ">>>Switching to kind-myk8s context..."
    kubectl config use-context kind-myk8s
else
    echo ">>>Already in kind-myk8s context..."
fi

APP_NAME=superset
IMAGE=superset/superset
VER=0.11.2
# If no argument is passed install
if [ $# -eq 0 ]; then
    echo ">>>Installing $APP_NAME ChartVer: $VER..."
    helm upgrade --install -n default $APP_NAME $IMAGE\
     --version $VER --values values-helm.yaml --debug
# Else if -u is passed uninstall
elif [ "$1" == "-u" ]; then
    echo ">>>Uninstalling $APP_NAME..."
    helm uninstall -n default $APP_NAME
    kubectl delete job superset-init-db -n default
    # Do you want to delete pvc as well?
    read -p ">>>Do you want to delete pvc as well? (y/n): " delete_pvc
    if [ "$delete_pvc" == "y" ]; then
        kubectl delete pvc -n default $(kubectl get pvc -n default | grep $APP_NAME | awk '{print $1}')
    fi
fi
