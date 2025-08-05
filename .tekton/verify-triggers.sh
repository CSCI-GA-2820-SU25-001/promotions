#!/bin/bash

# Tekton Triggers Verification Script
echo "🔍 Verifying Tekton Triggers Configuration..."
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Function to check resource status
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local namespace=${3:-default}
    
    if kubectl get $resource_type $resource_name -n $namespace &> /dev/null; then
        echo "✅ $resource_type/$resource_name exists"
        return 0
    else
        echo "❌ $resource_type/$resource_name not found"
        return 1
    fi
}

# Check pipeline components
echo "📋 Checking Pipeline Components:"
check_resource "pipeline" "promotions-cd-pipeline"
check_resource "pvc" "tekton-workspace-pvc"

# Check RBAC
echo ""
echo "🔐 Checking RBAC Configuration:"
check_resource "serviceaccount" "pipeline"
check_resource "clusterrole" "pipeline-cluster-role"
check_resource "clusterrolebinding" "pipeline-cluster-role-binding"

# Check trigger components
echo ""
echo "🎯 Checking Trigger Components:"
check_resource "secret" "github-webhook-secret"
check_resource "triggerbinding" "promotions-github-binding"
check_resource "triggertemplate" "promotions-trigger-template"
check_resource "eventlistener" "promotions-github-listener"

# Check EventListener service
echo ""
echo "🌐 Checking EventListener Service:"
check_resource "service" "el-promotions-github-listener"

# Check EventListener pod status
echo ""
echo "🚀 Checking EventListener Pod Status:"
if kubectl get pods -l eventlistener=promotions-github-listener --no-headers 2>/dev/null | grep -q "Running"; then
    echo "✅ EventListener pod is running"
    
    # Get the service endpoint
    echo ""
    echo "📡 EventListener Service Information:"
    kubectl get svc el-promotions-github-listener -o wide
    
    # Check if service is accessible (optional, might not work in all environments)
    echo ""
    echo "🔗 Webhook URL for GitHub:"
    SERVICE_IP=$(kubectl get svc el-promotions-github-listener -o jsonpath='{.spec.clusterIP}')
    echo "   Internal: http://$SERVICE_IP:8080"
    
    # Check if running on minikube
    if command -v minikube &> /dev/null && minikube status &> /dev/null; then
        MINIKUBE_IP=$(minikube ip)
        NODE_PORT=$(kubectl get svc el-promotions-github-listener -o jsonpath='{.spec.ports[0].nodePort}')
        if [ -n "$NODE_PORT" ]; then
            echo "   External (Minikube): http://$MINIKUBE_IP:$NODE_PORT"
        fi
    fi
    
elif kubectl get pods -l eventlistener=promotions-github-listener --no-headers 2>/dev/null | grep -q "Pending\|ContainerCreating"; then
    echo "⏳ EventListener pod is starting..."
elif kubectl get pods -l eventlistener=promotions-github-listener --no-headers 2>/dev/null | wc -l | grep -q "0"; then
    echo "❌ EventListener pod not found"
else
    echo "⚠️  EventListener pod status unknown"
    kubectl get pods -l eventlistener=promotions-github-listener
fi

# Check webhook secret content
echo ""
echo "🔑 Checking Webhook Secret:"
SECRET_TOKEN=$(kubectl get secret github-webhook-secret -o jsonpath='{.data.secretToken}' 2>/dev/null | base64 -d 2>/dev/null)
if [ "$SECRET_TOKEN" = "your-webhook-secret-token-here" ]; then
    echo "⚠️  Webhook secret is still set to default value"
    echo "   Please update it with: kubectl patch secret github-webhook-secret -p '{\"stringData\":{\"secretToken\":\"your-actual-secret-token\"}}'"
elif [ -n "$SECRET_TOKEN" ]; then
    echo "✅ Webhook secret is configured (length: ${#SECRET_TOKEN} characters)"
else
    echo "❌ Webhook secret is not readable"
fi

echo ""
echo "📊 Summary:"
echo "   Pipeline: $(check_resource "pipeline" "promotions-cd-pipeline" &>/dev/null && echo "✅" || echo "❌")"
echo "   Triggers: $(check_resource "eventlistener" "promotions-github-listener" &>/dev/null && echo "✅" || echo "❌")"
echo "   RBAC: $(check_resource "serviceaccount" "pipeline" &>/dev/null && echo "✅" || echo "❌")"
echo "   Workspace: $(check_resource "pvc" "tekton-workspace-pvc" &>/dev/null && echo "✅" || echo "❌")"

echo ""
echo "📚 Next Steps:"
echo "1. Update webhook secret if needed"
echo "2. Configure GitHub webhook with the EventListener URL"
echo "3. Test by pushing to master branch"
echo "4. Monitor with: kubectl get pipelineruns -w"
