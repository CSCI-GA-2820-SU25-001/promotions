#!/bin/bash

# Tekton Pipeline Setup Script for Promotions Service
# This script sets up the complete CD pipeline

set -e

echo "Setting up Tekton CD Pipeline for Promotions Service..."

# Check if we're logged into OpenShift
if ! oc whoami > /dev/null 2>&1; then
    echo "Error: Not logged into OpenShift. Please run 'oc login' first."
    exit 1
fi

# Get current namespace
NAMESPACE=$(oc project -q)
echo "Using namespace: $NAMESPACE"

# Install required ClusterTasks if they don't exist
echo "Checking for required ClusterTasks..."

if ! oc get clustertask git-clone > /dev/null 2>&1; then
    echo "Installing git-clone ClusterTask..."
    oc apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml
else
    echo "git-clone ClusterTask already exists"
fi

if ! oc get clustertask buildah-1-19-0 > /dev/null 2>&1; then
    echo "Installing buildah-1-19-0 ClusterTask..."
    # Note: Adjust URL if needed based on actual Tekton catalog structure
    echo "Please manually install buildah-1-19-0 ClusterTask from Tekton Hub"
    echo "You can find it at: https://hub.tekton.dev/tekton/task/buildah"
else
    echo "buildah-1-19-0 ClusterTask already exists"
fi

# Update RBAC namespace in rbac.yaml
echo "Updating RBAC configuration with current namespace..."
sed -i "s/namespace: default/namespace: $NAMESPACE/g" rbac.yaml

# Apply Tekton resources in correct order
echo "Applying Tekton resources..."

echo "1. Creating workspace PVC..."
oc apply -f workspace.yaml

echo "2. Setting up RBAC..."
oc apply -f rbac.yaml

echo "3. Creating custom tasks..."
oc apply -f tasks.yaml

echo "4. Creating pipeline..."
oc apply -f pipeline.yaml

echo "5. Setting up triggers..."
oc apply -f triggers.yaml

# Deploy PostgreSQL if not exists
if ! oc get deployment postgres > /dev/null 2>&1; then
    echo "Deploying PostgreSQL..."
    oc apply -f ../k8s/postgres/
else
    echo "PostgreSQL already deployed"
fi

# Deploy application
echo "Deploying promotions application..."
oc apply -f ../k8s/

# Get route URL for webhook setup
echo ""
echo "Setup complete!"
echo ""
echo "Your EventListener webhook URL is:"
ROUTE_HOST=$(oc get route el-cd-pipeline-listener -o jsonpath='{.spec.host}' 2>/dev/null || echo "Route not ready yet")
if [ "$ROUTE_HOST" != "" ]; then
    echo "http://$ROUTE_HOST"
else
    echo "EventListener route not ready. Check with: oc get route el-cd-pipeline-listener"
fi

echo ""
echo "Your application route is:"
APP_ROUTE=$(oc get route promotions -o jsonpath='{.spec.host}' 2>/dev/null || echo "Route not ready yet")
if [ "$APP_ROUTE" != "" ]; then
    echo "http://$APP_ROUTE"
    echo ""
    echo "Update the service-url parameter in pipelinerun-example.yaml to:"
    echo "http://$APP_ROUTE"
else
    echo "Application route not ready. Check with: oc get route promotions"
fi

echo ""
echo "To test the pipeline manually:"
echo "1. Update the repo-url and service-url in pipelinerun-example.yaml"
echo "2. Run: oc create -f pipelinerun-example.yaml"
echo ""
echo "To set up the webhook, add this URL to your GitHub repository:"
echo "Repository Settings > Webhooks > Add webhook"
echo "Payload URL: http://el-cd-pipeline-listener-$NAMESPACE.apps.<your-cluster-domain>/"
echo "Content type: application/json"
echo "Events: Just the push event"
