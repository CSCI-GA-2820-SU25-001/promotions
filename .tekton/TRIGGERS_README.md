# Tekton Triggers Setup

This directory contains the Tekton Triggers configuration for automatically running the promotions CD pipeline on every push to the master branch.

## Components

### 1. EventListener (`event-listener.yaml`)
- Listens for GitHub webhook events
- Filters events to only trigger on pushes to the master branch
- Includes security verification for GitHub webhook payloads
- Creates a Kubernetes service to expose the webhook endpoint

### 2. TriggerBinding (`trigger-binding.yaml`)
- Extracts parameters from the GitHub webhook payload:
  - `git-repo-url`: Repository clone URL
  - `git-repo-name`: Repository name
  - `git-revision`: Git reference (branch/tag)
  - `git-commit-sha`: Commit SHA for image tagging

### 3. TriggerTemplate (`trigger-template.yaml`)
- Creates a PipelineRun when triggered
- Uses parameters from the TriggerBinding
- Configures the workspace binding to use the PVC
- Tags the image with the commit SHA for traceability

### 4. Supporting Resources
- `github-webhook-secret.yaml`: Secret for webhook payload verification
- `rbac.yaml`: ServiceAccount and permissions for the EventListener
- `workspace.yaml`: PersistentVolumeClaim for pipeline workspace

## Setup Instructions

### 1. Deploy the Tekton Resources
```bash
# Apply all Tekton resources
kubectl apply -f .tekton/

# Verify the EventListener is running
kubectl get eventlisteners
kubectl get pods -l eventlistener=promotions-github-listener
```

### 2. Configure GitHub Webhook Secret
```bash
# Update the webhook secret with your actual token
kubectl patch secret github-webhook-secret -p '{"stringData":{"secretToken":"your-actual-secret-token"}}'
```

### 3. Get the EventListener URL
```bash
# Get the service URL (for local/minikube)
kubectl get svc el-promotions-github-listener

# For OpenShift, create a route:
oc expose svc el-promotions-github-listener
oc get route el-promotions-github-listener
```

### 4. Configure GitHub Webhook
1. Go to your GitHub repository settings
2. Navigate to "Webhooks"
3. Click "Add webhook"
4. Set the payload URL to your EventListener endpoint
5. Set content type to "application/json"
6. Enter your secret token (same as in the Kubernetes secret)
7. Select "Just the push event"
8. Ensure "Active" is checked

## Usage

Once configured, the pipeline will automatically trigger when:
- A push is made to the `master` branch
- The webhook payload is successfully verified

The pipeline will:
1. Clone the repository at the specific commit
2. Run linting and unit tests
3. Build and push a Docker image tagged with the commit SHA
4. Run BDD tests
5. Deploy to OpenShift

## Monitoring

Monitor pipeline runs:
```bash
# Watch pipeline runs
kubectl get pipelineruns -w

# Check EventListener logs
kubectl logs -l eventlistener=promotions-github-listener -f

# View pipeline run details
kubectl describe pipelinerun <pipelinerun-name>
```

## Troubleshooting

### Common Issues

1. **EventListener not receiving webhooks**
   - Check if the service is accessible from GitHub
   - Verify the webhook URL in GitHub settings
   - Check EventListener logs for errors

2. **Pipeline not triggering**
   - Verify the branch filter (must be `refs/heads/master`)
   - Check webhook secret configuration
   - Review TriggerBinding parameter extraction

3. **Permission errors**
   - Ensure the `pipeline` ServiceAccount has proper RBAC permissions
   - Check cluster role binding configuration

### Debug Commands
```bash
# Check EventListener status
kubectl describe eventlistener promotions-github-listener

# View webhook deliveries in GitHub
# Go to Settings > Webhooks > Recent Deliveries

# Check pipeline service account permissions
kubectl auth can-i create pipelineruns --as=system:serviceaccount:default:pipeline
```
