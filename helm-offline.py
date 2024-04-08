import argparse
import os
import sys
import subprocess
import yaml
import re
# Class for helm application
class HelmApplication:
    def __init__(self, clusterName,  name, namespace, path):
        self.clusterName = clusterName
        self.name = name
        self.namespace = namespace
        self.path = path
        self.appPathValues = os.path.join(self.path, 'values.yaml')
        self.appPathChart = os.path.join(self.path, 'chart.yaml')
        self.appPathImagesTxt= os.path.join(offlinePackagesPath, f'images-{self.name}.txt')
        self.appPathHelmTemplate= os.path.join(offlinePackagesPath, f'helm-template-{self.name}.yaml')
        self.appPathHelmTemplateLocal= os.path.join(offlinePackagesPath, f'helm-template-local-{self.name}.yaml')
# Check Docker or Nerdctl is installed
def check_docker_nerdctl():
    containerRuntime= ''
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Docker is installed")
        containerRuntime= 'docker'
    except FileNotFoundError:
        print("Docker is not installed")
    try:
        subprocess.run(["nerdctl", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Nerdctl is installed")
        containerRuntime= 'nerdctl'
    except FileNotFoundError:
        print("Nerdctl is not installed")
    if containerRuntime == '':
        sys.exit("nerdctl or docker is not installed, exiting...")
    print("Container runtime is selected as", containerRuntime)
    return containerRuntime
# Create images for offline usage
def create_images(clusterName, imageName, localhostUrl):
    """Create images for offline usage

    Args:
        imageName (str): Application name or "all" for all applications.
    """
    # Helm Template Create (Both remote and local)
    def helm_template_create(helmApp):
        """Create Helm Template

        Args:
            helmApp (helmApplication): Helm Application object
        """
        # === Create Images ===
        print("------------------")
        print("Creating helm template...")
        # Parse Chart.yaml
        with open(helmApp.appPathChart, 'r') as file:
            chartYamlData = yaml.safe_load(file)
        print("chart.yaml read")
        # Create Helm Template in imagesPath folder
        print(f"Chart Name: {chartYamlData['chartName']}")
        print(f"Repository: {chartYamlData['repository']}")
        print(f"Version   : {chartYamlData['version']}")
        # === Helm Template ===
        with open(helmApp.appPathHelmTemplate, "w") as output_file:
            # Execute the command and redirect its output to the file
            subprocess.check_call(["helm"\
                                  , "template"\
                                  , f"{chartYamlData['chartName']}"\
                                  ,"--namespace" ,f"{helmApp.namespace}"\
                                  ,"--repo", f"{chartYamlData['repository']}"\
                                  ,"--version", f"{chartYamlData['version']}"\
                                  ,"--name-template", f"{helmApp.name}"\
                                  ,"--values", f"{helmApp.appPathValues}"\
                                  ]
                , stdout=output_file)
            print("Helm Template created")
        # === Helm Template END ===
        # === Find Images in Helm Template ===
        # Regex: find lines starting with "image:"
        imageRegex = re.compile(r'^\s*image:\s*[\'"]?(.*?)[\'"]?\s*$')
        # Store image names
        images = set()
        with open(helmApp.appPathHelmTemplate, 'r') as file:
            for line in file:
                match = imageRegex.match(line)
                if match:
                    imageNameTmp = match.group(1).strip()
                    images.add(imageNameTmp)
        # Write images to images.txt
        with open(helmApp.appPathImagesTxt, 'w') as file:
            for imageNameTmp in images:
                file.write(f"{imageNameTmp}\n")
        print(f"Images found in Helm Template and written to images-{helmApp.name}.txt")
        # === Find Images in Helm Template END ===
        # === Find and Replace Image Names in Helm Template ===
        # Read helm-template.yaml
        with open(helmApp.appPathHelmTemplate, 'r') as f:
            templateContent = f.read()
        # Replace image names with localhostUrl
        pattern = r"(\s*image\s*:\s*['\"]?)([^'\"\s]+)"
        matches = re.findall(pattern, templateContent)
        for match in matches:
            oldImag = match[1]
            newImag = f"{localhostUrl}/" + oldImag
            templateContent = templateContent.replace(match[0] + oldImag, match[0] + newImag)
        # Write to helm-template-local.yaml
        with open(helmApp.appPathHelmTemplateLocal, 'w') as f:
            f.write(templateContent)
        print(f"Images replaced with {localhostUrl} in {helmApp.appPathHelmTemplateLocal}")
        # Remove helm-template.yaml
        os.remove(helmApp.appPathHelmTemplate)
        # Add namespace to begining of yaml file
        with open(f"{helmApp.namespace}.yaml", 'w') as f:
            f.write("apiVersion: v1\n")
            f.write("kind: Namespace\n")
            f.write("metadata:\n")
            f.write(f"  name: {helmApp.namespace}\n")        
        # === Find and Replace Image Names in Helm Template END ===
        print("------------------")
        # === Create Images END ===
    # Save images
    def save_images(helmApp):
        print("------------------")
        print("Pulling images...")
        # Change directory to imagesPath
        os.chdir(offlinePackagesPath)
        # Check nerdctl or docker is installed
        containerRuntime= check_docker_nerdctl()
        with open(helmApp.appPathImagesTxt, 'r') as file:
            for imageName in file:
                imageName= imageName.strip()
                subprocess.check_call([containerRuntime, 'pull', imageName])
        # Change directory to currentDirPath
        os.chdir(currentDirPath)
        print("------------------")
    # Tag images
    def tag_images(helmApp):
        print("------------------")
        print("Tagging images...")
        # Current directory path
        currentDirPath = os.path.dirname(os.path.realpath(__file__))
        # Change directory to imagesPath
        os.chdir(offlinePackagesPath)
        # Check nerdctl or docker is installed
        containerRuntime= check_docker_nerdctl()
        with open(helmApp.appPathImagesTxt, 'r') as file:
            for imageName in file:
                imageName= imageName.strip()
                print(f"Tagging image: {imageName}")
                subprocess.check_call([containerRuntime, 'tag', imageName, f'localhost:6001/{imageName}'])
        # Change directory to currentDirPath
        os.chdir(currentDirPath)
        print("------------------")
    # Clean Original Images
    def clean_images(helmApp):
        print("------------------")
        print("Cleaning images...")
        # Current directory path
        currentDirPath = os.path.dirname(os.path.realpath(__file__))
        # Change directory to imagesPath
        os.chdir(offlinePackagesPath)
        # Check nerdctl or docker is installed
        containerRuntime= check_docker_nerdctl()
        with open(helmApp.appPathImagesTxt, 'r') as file:
            for imageName in file:
                imageName= imageName.strip()
                print(f"Removing image: {imageName}")
                subprocess.check_call([containerRuntime, 'rmi', imageName])
        # Change directory to currentDirPath
        os.chdir(currentDirPath)
        print("------------------")
    # Save local images
    def save_local_images_tar(helmApp):
        print("------------------")
        print("Saving local images as zip files...")
        # Current directory path
        currentDirPath = os.path.dirname(os.path.realpath(__file__))
        # Change directory to imagesPath
        os.chdir(offlinePackagesPath)
        # Check nerdctl or docker is installed
        containerRuntime= check_docker_nerdctl()
        # All Images
        allImages= []
        with open(helmApp.appPathImagesTxt, 'r') as file:
            for imageName in file:
                imageName= imageName.strip()
                print(f"Saving image: {imageName}")
                # Save image as tar file
                subprocess.check_call([containerRuntime\
                    , 'save', f"localhost:6001/{imageName}"\
                    , '-o', f"{imageName.replace('/', '_')}.tar"])
                allImages.append(f"{imageName.replace('/', '_')}.tar")
        os.chdir(currentDirPath)
        print("------------------")
    # Save Registery Image and Zip them
    def save_all():
        print("------------------")
        print("Saving registery images as zip files...")
        # Current directory path
        currentDirPath = os.path.dirname(os.path.realpath(__file__))
        # Change directory to imagesPath
        os.chdir(offlinePackagesPath)
        # Check nerdctl or docker is installed
        containerRuntime= check_docker_nerdctl()
        
        # === Save Registery Image ===
        # Pull docker registery
        print("Pulling docker registery 2.8.3...")
        subprocess.check_call([containerRuntime, 'pull', 'registry:2.8.3'])
        # Tag docker registery
        subprocess.check_call([containerRuntime, 'tag'\
            , 'registry:2.8.3', 'registry:2.8.3'])
        # Save docker registery as tar file
        print("Saving docker registery 2.8.3...")
        subprocess.check_call([containerRuntime\
            , 'save', 'registry:2.8.3'\
            , '-o', 'registry:2.8.3.tar'])
        # === Save Registery Image END ===
        
        # === Create SH Script ===
        # Read All images.txt
        allImages= []
        # List all txt files
        print("Reading all images txt files")
        txtFiles= [f for f in os.listdir(offlinePackagesPath) if f.endswith('.txt')]
        yamlFiles= [f for f in os.listdir(offlinePackagesPath) if f.endswith('.yaml')]
        # Read all txt files and append to allImages
        for txtFile in txtFiles:
            with open(txtFile, 'r') as file:
                for imageName in file:
                    allImages.append(imageName.strip())
        with open('install.sh', 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("set -o allexport; source .env; set +o allexport\n")
            f.write(f"{containerRuntime} load -i registry:2.8.3.tar\n")
            f.write(f"{containerRuntime} run -d -p 6001:5000 --restart=always --name borda_registry registry:2.8.3\n")
            # Load all images
            for imageName in allImages:
                f.write(f"{containerRuntime} load -i {imageName.replace('/', '_')}.tar\n")
            # Push all images
            for imageName in allImages:
                f.write(f"{containerRuntime} push localhost:6001/{imageName}\n")
            # Add kubectl apply helm-template-local.yaml
            for yamlFile in yamlFiles:
                f.write(f"kubectl apply -f {yamlFile}\n")
                # Wait 5 seconds
                f.write("sleep 5\n")
        # Change permissions of install.sh
        subprocess.check_call(['chmod', '+x', 'install.sh'])
        # === Create SH Script END ===
        
        # === Zip all images ===
        # Zip all tar files, yaml files inside of offlinePackagesPath
        print("Zipping everything...")
        subprocess.check_call(['zip', '-r'\
            , f'{helmApp.name}-offline-packages.zip', '.'])
        # === Zip all images END ===
        # Remove everything except zip file
        print("Removing everything except zip file...")
        for file in os.listdir(offlinePackagesPath):
            if not file.endswith(".zip"):
                os.remove(file)
        # Change directory to currentDirPath
        os.chdir(currentDirPath)
        print("------------------")
    
    # Change currentDirPath to cluster path
    os.chdir(currentDirPath)
    print("\n====== Checking folders... ======")
    # Namespaces are the folder names in clusters directory
    namespaces = next(os.walk('.'))[1]
    # Print namespaces side by side
    print("Namespaces:", namespaces)
    # Apllication names are the folder names in each namespace
    for namespace in namespaces:
        applications = next(os.walk(namespace))[1]
    # Print applications side by side
    print("Applications:", applications)
    # If applications is empty, exit
    if not applications:
        sys.exit("No applications found, exiting...")
    # === ALL APPLICATIONS ===
    if imageName.lower() == 'all':
        print("All applications will be checked\n")
        for application in applications:
            # Hold the application information
            helmApp= HelmApplication(clusterName\
                , application\
                , namespace\
                , os.path.join(currentDirPath, namespace, application))
            # if values.yaml and chart.yaml exists, print the application
            print("====================================")
            print(f"Cluster name             : {helmApp.clusterName}")
            print(f"Application name         : {helmApp.name}")
            print(f"Namespace                : {helmApp.namespace}")
            print(f"Path                     : {helmApp.path}")
            print(f"Values Path              : {helmApp.appPathValues}")
            print(f"Chart Path               : {helmApp.appPathChart}")
            print(f"Images Text Path         : {helmApp.appPathImagesTxt}")
            print(f"Helm Template Path       : {helmApp.appPathHelmTemplate}")
            print(f"Helm Template Local Path : {helmApp.appPathHelmTemplateLocal}")
            if not (os.path.exists(helmApp.appPathValues) \
                and os.path.exists(helmApp.appPathChart)):
                    print(f"Application {application}\nis not valid for offline helm operation")
                    sys.exit("Check values.yaml and chart.yaml files, exiting...")
            print("====================================")
            # Create Helm Template
            helm_template_create(helmApp)
            # Save images
            save_images(helmApp)
            # Tag images
            tag_images(helmApp)
            # Clean images
            clean_images(helmApp)
            # Save local images as zip files
            save_local_images_tar(helmApp)
    # === ALL APPLICATIONS END ===
    
    # === SINGLE APPLICATION ===
    else:
        # Find the application in the applications list
        if imageName not in applications:
            print("\n====================================")
            print(f"Application {imageName}\nis not valid for offline helm operation")
            print("====================================")
            sys.exit("Check namespaces and application names, exiting...")
        else:
            # Find the namespace of the application
            for namespace in namespaces:
                if imageName in applications:
                    # if values.yaml and chart.yaml exists, print the application
                    # Hold the application information
                    helmApp= HelmApplication(clusterName\
                        , imageName\
                        , namespace\
                        , os.path.join(currentDirPath, namespace, imageName))
                    break
        print("====================================")
        print(f"Cluster name             : {helmApp.clusterName}")
        print(f"Application name         : {helmApp.name}")
        print(f"Namespace                : {helmApp.namespace}")
        print(f"Path                     : {helmApp.path}")
        print(f"Values Path              : {helmApp.appPathValues}")
        print(f"Chart Path               : {helmApp.appPathChart}")
        print(f"Images Text Path         : {helmApp.appPathImagesTxt}")
        print(f"Helm Template Path       : {helmApp.appPathHelmTemplate}")
        print(f"Helm Template Local Path : {helmApp.appPathHelmTemplateLocal}")
        if not (os.path.exists(helmApp.appPathValues) \
                and os.path.exists(helmApp.appPathChart)):
                    print(f"Application {application}\nis not valid for offline helm operation")
                    sys.exit("Check values.yaml and chart.yaml files, exiting...")
        # Create Helm Template
        helm_template_create(helmApp)
        # Save images
        save_images(helmApp)
        # Tag images
        tag_images(helmApp)
        # Clean images
        clean_images(helmApp)
        # Save local images as zip files
        save_local_images_tar(helmApp)
        print("====================================")
    # === SINGLE APPLICATION END ===

    # Create Registery Image and Zip them
    save_all()
    print("====================================")
# Script
if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(\
        description='Offline Operations for Helm Charts')
    parser.add_argument('--create-images'\
        , metavar='APP_NAME', type=str\
            , help='Create images for offline usage. Use "all" for all applications')
    parser.add_argument('--localhost-url'\
        , metavar='LOCALHOST_URL', type=str\
            , help='Localhost URL for images')
    parser.add_argument('--cluster'\
        , metavar='CLUSTER_NAME', type=str\
            , help='Cluster name for the application')
    # If no arguments, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit('No arguments provided, exiting...')
    # If unrecognized arguments, print help
    args, unknown = parser.parse_known_args()
    if unknown:
        parser.print_help(sys.stderr)
        sys.exit('Unrecognized arguments provided, exiting...')
    # Parse arguments
    args = parser.parse_args()
    # If create-images is provided, cluster have to be provided
    if args.create_images:
        if not args.cluster:
            sys.exit("--cluster argument is required, exiting...")
        # If localhost-url is not provided, set it to localhost_url=''
        if not args.localhost_url:
            sys.exit("--localhost-url argument is required, exiting...")
    # Current directory path
    thisFilePath= os.path.dirname(os.path.realpath(__file__))
    offlinePackagesPath= os.path.join(thisFilePath, f'offline-packages-{args.cluster}-{args.create_images}')
    if not os.path.exists(offlinePackagesPath):
        os.makedirs(offlinePackagesPath)
        print("Offline Package folder created")
    else:
        print("Offline Package folder already exists")
        sys.exit(f"Check {offlinePackagesPath}, exiting...")
    clusterPath= os.path.join(thisFilePath, 'clusters')
    # Add Cluster name to currentDirPath
    currentDirPath= os.path.join(clusterPath, args.cluster)
    # Create images
    create_images(clusterName= args.cluster\
        , imageName= args.create_images\
        , localhostUrl=args.localhost_url)
    # Create exacutabels (docker registery, load, push, kubectl apply helm-template-local.yaml) and ZIP them
        
    # Obtain secrets from Vault
    
    # Connect VPN
    
    # Check SSH connection
    
    # Send ZIP
    
    # Connect SSH
    
    # Apply ZIP
    
    # Check 