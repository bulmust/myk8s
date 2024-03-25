#!/bin/sh

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Cluster Name
clusterName="myk8s"

# Check There is No Kind Cluster with the Same Name
echo "${GREEN}Check existence of Kind cluster with the same name${NC}"
kind get clusters | grep "$clusterName"
if [ $? -eq 0 ]; then
    echo "${RED}Kind Cluster with the Same Name Exists${NC}"
    exit 1
else
    echo "${GREEN}Kind Cluster with the Same Name Does Not Exist${NC}"
fi

# Create Kind cluster with 2 worker nodes and ingress-ready label
echo "${GREEN}Create Kind cluster with 1 control plane and 2 worker nodes and ingress-ready label${NC}"
kind create cluster --name "$clusterName" --config manifests/kind-1CP2W-Ingress.yaml

# Echo Current Context
echo "${GREEN}Current Context${NC}"
kubectl config current-context
# Sleep 2s
sleep 2

# Deploy Ingress-Nginx
echo "${GREEN}Deploy Ingress${NC}"
wget https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/provider/kind/deploy.yaml -O manifests/deploy-ingress-nginx-kind.yaml
kubectl apply -f manifests/deploy-ingress-nginx-kind.yaml
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
# Sleep 2s
sleep 2

# Do you want self-signed certificate?
echo "${GREEN}Do you want self-signed certificate?${NC}"
echo "${GREEN}y${NC}/${RED}n${NC}"
read response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    # Create Self-Signed Certificate
    echo "${GREEN}Create 365 Days valid Self-Signed certificate in certificates/ folder${NC}"
    # Check certificates folder
    if [ ! -d "certificates/" ]; then
        echo "${GREEN}Create certificates folder${NC}"
        mkdir -r certificates/
        cd certificates/
        # Create Self-Signed Certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certificates/localhost.key -out certificates/localhost.crt -subj "/CN=localhost"
        # Create Certificate and Key Secret in kube-system Namespace 
        kubectl create secret tls -n kube-system localhost-tls --cert=certificates/localhost.crt --key=certificates/localhost.key
        cd -
    else
        echo "${GREEN}certificates Folder Exists${NC}"
        # Hold Old Certificates and Continue
        echo "${GREEN}Hold old certificates and continue${NC}"
        cd certificates/
        # Create Certificate and Key Secret in kube-system Namespace 
        kubectl create secret tls -n kube-system localhost-tls --cert=certificates/localhost.crt --key=certificates/localhost.key
        cd -
    fi
    PORT=443
else
    echo "${GREEN}No Self-Signed Certificate${NC}"
    PORT=80
fi
# Sleep 2s
sleep 2

# Deploy Echo-Deployment
echo "${GREEN}Create Test Namespace${NC}"
kubectl create ns test
echo "${GREEN}Deploy Echo-Server${NC}"
# Deployment
kubectl apply -f manifests/deployment-echoserver-1-10.yaml
# Service
kubectl apply -f manifests/service-echoserver.yaml
# Wait for Deployment to be Ready
kubectl wait --namespace test --for=condition=available deployment/echo-server --timeout=180s
# Sleep 6s
sleep 6

# Initialize Echo Ingress
echo "${GREEN}Initialize Echo Ingress${NC}"
# If check if self-signed certificate is used
if [ "$PORT" = "443" ]; then
    echo "${GREEN}Initialize Echo Ingress with Self-Signed Certificate${NC}"
    kubectl apply -f manifests/ingress-echoserver-self-signed.yaml
# Test Ingress (Skip Certificate Verification)
echo "${GREEN}Test Ingress${NC}: ${RED}curl -k https://echo.localhost${NC}"
curl -k https://echo.localhost
else
    echo "${GREEN}Initialize Echo Ingress without Self-Signed Certificate${NC}"
    kubectl apply -f manifests/ingress-echoserver.yaml
# Test Ingress
echo "${GREEN}Test Ingress${NC}: ${RED}curl echo.localhost${NC}"
curl echo.localhost
fi
# Sleep 2s
sleep 2
# Echo Which Ingress to Use
echo "${GREEN}All DNS should be:${RED} *.localhost${NC}"
# Sleep 2s
sleep 2
echo "---------------------------------"

# Do you want to tainted the worker nodes?
echo "${GREEN}Do you want to tainted the myk8s-worker2 node? https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/${NC}"
echo "${GREEN}y${NC}/${RED}n${NC}"
read response
if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    # Taint Worker Nodes
    echo "${GREEN}Taint Worker Nodes${NC}${RED} product=monitoring:NoSchedule${NC}"
    kubectl taint nodes myk8s-worker2 product=monitoring:NoSchedule
    echo "${GREEN}Taints${NC}"
    kubectl get nodes -ojsonpath='{.items[*].spec.taints}'
    echo "${GREEN}Label Worker Nodes${NC}${RED} role=monitoring${NC}"
    kubectl label nodes myk8s-worker2 role=monitoring
    echo "${GREEN}Labels${NC}"
    kubectl get nodes -ojsonpath='{.items[*].metadata.labels}'
else
    echo "${GREEN}myk8s-worker2 Node is not tainted${NC}"
fi