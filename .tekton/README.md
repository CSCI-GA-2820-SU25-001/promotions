# Tekton CD Pipeline for OpenShift Deployment

This directory contains Tekton pipelines and tasks for continuous deployment of the Promotions application to OpenShift/Kubernetes.

## Overview

The CD pipeline performs the following steps:
1. **Clone** - Fetch source code from Git repository
2. **Lint** - Run code quality checks with flake8 and pylint
3. **Test** - Execute unit tests with pytest
4. **Build** - Build and push Docker image using Kaniko
5. **Deploy** - Deploy application to OpenShift cluster

## Files

- `tasks.yaml` - Individual Tekton Tasks definitions
- `pipeline.yaml` - Main CD Pipeline definition
- `workspace.yaml` - Workspace and PVC definitions
- `pipelinerun-template.yaml` - Template for running the pipeline
- `deploy-verify.sh` - Manual deployment verification script

## Usage

### Prerequisites

1. Tekton Pipelines installed in your OpenShift cluster
2. Necessary RBAC permissions for service accounts
3. Access to image registry (OpenShift internal registry or external)

### Apply Tekton Resources

```bash
# Apply workspace and PVC
kubectl apply -f .tekton/workspace.yaml

# Apply tasks
kubectl apply -f .tekton/tasks.yaml

# Apply pipeline
kubectl apply -f .tekton/pipeline.yaml
```

### Run the Pipeline

#### Option 1: Using the template
```bash
# Edit pipelinerun-template.yaml with your parameters
kubectl apply -f .tekton/pipelinerun-template.yaml
```

#### Option 2: Using tkn CLI
```bash
tkn pipeline start promotions-cd-pipeline \
  --param repo-url="https://github.com/CSCI-GA-2820-SU25-001/promotions.git" \
  --param revision="main" \
  --param image-name="promotions" \
  --param image-tag="v1.0.0" \
  --param registry="image-registry.openshift-image-registry.svc:5000" \
  --param namespace="promotions-prod" \
  --workspace name=shared-data,claimName=tekton-workspace-pvc
```

### Monitor Pipeline Execution

```bash
# List pipeline runs
tkn pipelinerun list

# Follow logs of a specific run
tkn pipelinerun logs <pipelinerun-name> -f

# Get pipeline run status
kubectl get pipelinerun
```

## Tasks Description

### git-clone
Clones the Git repository to the shared workspace.

**Parameters:**
- `url`: Repository URL
- `revision`: Git revision (branch, tag, SHA)

### lint
Runs Python code quality checks using flake8 and pylint.

### unit-tests
Executes unit tests using pytest.

### build-image-kaniko
Builds and pushes Docker image using Kaniko (no privileged access required).

**Parameters:**
- `IMAGE_NAME`: Name of the image
- `IMAGE_TAG`: Image tag
- `REGISTRY`: Registry URL
- `DOCKERFILE`: Path to Dockerfile
- `CONTEXT`: Build context directory

### deploy-to-openshift
Deploys the application to OpenShift/Kubernetes cluster.

**Parameters:**
- `IMAGE_NAME`: Application name
- `IMAGE_TAG`: Image tag to deploy
- `REGISTRY`: Registry where image is stored
- `NAMESPACE`: Target namespace
- `MANIFESTS_DIR`: Directory containing k8s manifests

**Steps:**
1. Updates deployment manifest with new image tag
2. Deploys PostgreSQL database (StatefulSet + Service)
3. Deploys application (Deployment + Service + Ingress)
4. Verifies deployment status and health

## Deployment Verification

Use the provided script to manually verify deployment:

```bash
# Basic verification
./.tekton/deploy-verify.sh

# Specify namespace and app name
./.tekton/deploy-verify.sh my-namespace promotions
```

## Customization

### Parameters
You can customize the pipeline behavior by modifying parameters in `pipelinerun-template.yaml`:

- `repo-url`: Git repository URL
- `revision`: Branch or tag to build
- `image-name`: Application name
- `image-tag`: Docker image tag
- `registry`: Container registry URL
- `namespace`: Kubernetes namespace for deployment

### Manifests
The deployment task applies Kubernetes manifests from the `k8s/` directory:
- `k8s/postgres/secret.yaml` - Database credentials
- `k8s/postgres/postgres.yaml` - PostgreSQL StatefulSet and Service  
- `k8s/deployment.yaml` - Application Deployment
- `k8s/service.yaml` - Application Service
- `k8s/ingress.yaml` - Ingress configuration

### Environment-specific Configurations
For different environments (dev, staging, prod), you can:
1. Create separate namespaces
2. Use different parameter values in PipelineRuns
3. Maintain environment-specific manifest overlays
4. Use different image tags for each environment

## Troubleshooting

### Pipeline Failures
```bash
# Check pipeline run logs
tkn pipelinerun logs <name> -f

# Check individual task logs
kubectl logs <pod-name> -c step-<step-name>
```

### Deployment Issues
```bash
# Check deployment status
kubectl get deployment promotions -n <namespace>

# Check pod logs
kubectl logs -l app=promotions -n <namespace>

# Check events
kubectl get events -n <namespace> --sort-by='.firstTimestamp'
```

### Image Pull Issues
- Verify image exists in registry
- Check image pull secrets if using external registry
- Ensure service account has proper permissions

## Security Considerations

- Service accounts should have minimal required permissions
- Use secrets for sensitive data (database credentials, registry auth)
- Consider using image pull secrets for private registries
- Implement network policies for pod-to-pod communication

## Future Enhancements

- Add integration tests after deployment
- Implement blue-green or canary deployment strategies
- Add monitoring and alerting setup
- Include database migration steps
- Add rollback capabilities
