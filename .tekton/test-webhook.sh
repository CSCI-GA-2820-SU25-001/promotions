#!/bin/bash

# Test Tekton Triggers with a simulated GitHub webhook payload
echo "🧪 Testing Tekton Triggers with simulated GitHub webhook..."

# Get EventListener service details
SERVICE_NAME="el-promotions-github-listener"
NAMESPACE="default"

# Check if service exists
if ! kubectl get svc $SERVICE_NAME -n $NAMESPACE &>/dev/null; then
    echo "❌ EventListener service not found. Please deploy triggers first."
    exit 1
fi

# Get service URL
SERVICE_IP=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
SERVICE_PORT=$(kubectl get svc $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.spec.ports[0].port}')

echo "🌐 EventListener URL: http://$SERVICE_IP:$SERVICE_PORT"

# Create a test webhook payload
cat > /tmp/test-webhook-payload.json << 'EOF'
{
  "ref": "refs/heads/master",
  "after": "abc123def456",
  "repository": {
    "name": "promotions",
    "clone_url": "https://github.com/CSCI-GA-2820-SU25-001/promotions.git"
  },
  "head_commit": {
    "id": "abc123def456",
    "message": "Test commit for pipeline trigger"
  }
}
EOF

# Get webhook secret
WEBHOOK_SECRET=$(kubectl get secret github-webhook-secret -n $NAMESPACE -o jsonpath='{.data.secretToken}' 2>/dev/null | base64 -d 2>/dev/null)

if [ "$WEBHOOK_SECRET" = "your-webhook-secret-token-here" ] || [ -z "$WEBHOOK_SECRET" ]; then
    echo "⚠️  Using default webhook secret. Update it for production use."
    WEBHOOK_SECRET="your-webhook-secret-token-here"
fi

# Create GitHub signature (simplified - in real GitHub webhooks this is HMAC-SHA256)
SIGNATURE="sha256=$(echo -n "$(cat /tmp/test-webhook-payload.json)" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" | cut -d' ' -f2)"

echo ""
echo "🔐 Webhook Secret: ${WEBHOOK_SECRET:0:8}... (showing first 8 chars)"
echo "📝 Test Payload: /tmp/test-webhook-payload.json"

# Test the webhook endpoint (port-forward method)
echo ""
echo "🚀 Starting port-forward to test EventListener..."
kubectl port-forward svc/$SERVICE_NAME 8080:$SERVICE_PORT -n $NAMESPACE &
PORT_FORWARD_PID=$!

# Wait a moment for port-forward to establish
sleep 3

# Send test webhook
echo "📤 Sending test webhook payload..."
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: $SIGNATURE" \
  -d @/tmp/test-webhook-payload.json \
  -v

# Clean up
sleep 2
kill $PORT_FORWARD_PID 2>/dev/null
rm -f /tmp/test-webhook-payload.json

echo ""
echo "✅ Test webhook sent!"
echo ""
echo "🔍 Check if a PipelineRun was created:"
echo "   kubectl get pipelineruns"
echo ""
echo "📋 Monitor pipeline execution:"
echo "   kubectl get pipelineruns -w"
echo ""
echo "🔍 Check EventListener logs:"
echo "   kubectl logs -l eventlistener=promotions-github-listener -f"
