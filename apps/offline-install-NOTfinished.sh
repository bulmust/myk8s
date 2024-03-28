#!/bin/bash
# If argument is --create-images, create images directory and save all the images in it
if [ "$1" == "--create-images" ]; then
    echo ">>>Creating images directory and saving all the images in it..."
    # Create a directory images
    if [ ! -d images ]; then
        mkdir -p images
    else
        echo ""
        echo ">>>images directory already exists. To continue delete it manually."
        echo ""
        exit 1
    fi
    cd images
    # Helm template
    helm template -n default superset superset/superset --version 0.11.2 > helm-template.yaml
    # Get all the images from the helm chart
    cat helm-template.yaml| yq '..|.image? | select(.)' | sort -u > images.txt
    # Remove first line
    sed -i '1d' images.txt
    cp helm-template.yaml helm-template-remote.yaml
    # Find each line in images.txt in helm-template.yaml and add "local:5000" to it. Save it in helm-template-local.yaml
    for image in $(cat images.txt); do
        sed -i "s#$image#localhost:5000/$image#g" helm-template.yaml
    done
    mv helm-template.yaml helm-template-local.yaml    
    # Create Local Registry
    docker run -d -p 5000:5000 --restart=always --name registry registry:2.8.3
    # For each line, save the image with the name of image using docker save
    iter=0
    for image in $(cat images.txt); do
        docker pull $image
        # Tag the image with local registry
        docker tag $image localhost:5000/$image
        # Save it with the name of numbers
        docker save localhost:5000/$image -o $iter.zip
        iter=$((iter+1))
    done
    cd ..
# Else if --load-images is passed, load all the images from images directory
elif [ "$1" == "--load-images" ]; then
    # ls only zip files in images directory
    for image in $(ls images/*.zip); do
        docker load -i $image
    done
# Else if --delete-images is passed, delete images directory
elif [ "$1" == "--delete-images" ]; then
    echo ">>>Deleting images directory..."
    rm -rf images
# Else if --install is passed, install the helm chart
elif [ "$1" == "--install" ]; then
    echo ">>>Installing superset ChartVer: 0.11.2..."
    # helm upgrade --install -n default superset superset/superset\
    #  --version 0.11.2 --values values-helm.yaml --debug
    # ./helm-install-uninstall.sh
    kubectl config use-context kind-myk8s
    cd images
    kubectl apply -f helm-template-local.yaml
    cd ..
else
    echo ">>>Invalid argument. Pass --create-images, --load-images, --delete-images or --install."
    exit 1
fi
