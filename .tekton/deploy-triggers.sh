#!/bin/bash

# Deploy Tekton Triggers for Promotions Pipeline
echo "Deploying Tekton Triggers for Promotions Pipeline..."

# Apply RBAC first
echo "1. Applying RBAC configuration..."
kubectl apply -f .tekton/rbac.yaml

# Apply the workspace PVC
echo "2. Applying workspace PVC..."
kubectl apply -f .tekton/workspace.yaml

# Apply the webhook secret (you should update the token before running)
echo "3. Applying GitHub webhook secret..."
kubectl apply -f .tekton/github-webhook-secret.yaml

# Apply trigger components
echo "4. Applying TriggerBinding..."
kubectl apply -f .tekton/trigger-binding.yaml

echo "5. Applying TriggerTemplate..."
kubectl apply -f .tekton/trigger-template.yaml

echo "6. Applying EventListener..."
kubectl apply -f .tekton/event-listener.yaml

# Wait for EventListener to be ready
echo "7. Waiting for EventListener to be ready..."
kubectl wait --for=condition=Ready pod -l eventlistener=promotions-github-listener --timeout=300s

# Show the EventListener service
echo "8. EventListener service information:"
kubectl get svc el-promotions-github-listener

echo ""
echo "✅ Tekton Triggers deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Update the webhook secret with your actual GitHub token:"
echo "   kubectl patch secret github-webhook-secret -p '{\"stringData\":{\"secretToken\":\"your-actual-secret-token\"}}'"
echo ""
echo "2. Get the EventListener URL for GitHub webhook configuration:"
echo "   kubectl get svc el-promotions-github-listener"
echo ""
echo "3. Configure the GitHub webhook in your repository settings"
echo "   - Payload URL: http://<eventlistener-url>:8080"
echo "   - Content type: application/json"
echo "   - Secret: <your-secret-token>"
echo "   - Events: Just the push event"
