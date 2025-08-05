# Tekton CD Pipeline for Promotions Service

This directory contains the Tekton pipeline configuration for implementing a complete Continuous Deployment (CD) pipeline that automatically deploys the promotions service to OpenShift when changes are pushed to the master branch.

## Pipeline Overview

The pipeline consists of 6 main tasks:

1. **Clone Repository** - Uses the git-clone ClusterTask to fetch the source code
2. **Lint Code** - Runs flake8 linting on the service code
3. **Unit Tests** - Runs pytest with coverage reporting
4. **Build Image** - Uses buildah-1-19-0 to build and push Docker image
5. **Deploy** - Updates the Kubernetes deployment with the new image
6. **BDD Tests** - Runs Behave tests against the deployed service

## Files Description

- `workspace.yaml` - PersistentVolumeClaim for shared workspace storage
- `tasks.yaml` - Custom task definitions (flake8-lint, pytest-env, behave, deploy-image)
- `pipeline.yaml` - Main pipeline definition with all 6 tasks
- `triggers.yaml` - EventListener, TriggerBinding, and TriggerTemplate for webhook integration
- `rbac.yaml` - ServiceAccount and permissions for pipeline execution
- `pipelinerun-example.yaml` - Example PipelineRun for manual testing
- `README.md` - This documentation file

## Setup Instructions

### 1. Prerequisites

Ensure you have:
- OpenShift cluster with Tekton Pipelines installed
- Tekton Triggers installed
- kubectl/oc CLI access to the cluster

### 2. Install ClusterTasks

Install the required ClusterTasks from Tekton Hub:

```bash
# Install git-clone ClusterTask
oc apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml

# Install buildah-1-19-0 ClusterTask
oc apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/buildah/0.6/buildah.yaml
```

### 3. Deploy Pipeline Components

Apply all the Tekton resources:

```bash
# Apply in order
oc apply -f workspace.yaml
oc apply -f rbac.yaml
oc apply -f tasks.yaml
oc apply -f pipeline.yaml
oc apply -f triggers.yaml
```

### 4. Deploy Application Infrastructure

Deploy PostgreSQL and the application:

```bash
# Deploy PostgreSQL
oc apply -f ../k8s/postgres/

# Deploy the application
oc apply -f ../k8s/
```

### 5. Set up Route for BDD Tests

Update the service-url parameter in your PipelineRuns to match your actual route:

```bash
# Get your route URL
oc get route promotions -o jsonpath='{.spec.host}'
```

### 6. Create Webhook (Admin Required)

Create a webhook in your GitHub repository:

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add a new webhook with:
   - **Payload URL**: `http://el-cd-pipeline-listener-<namespace>.apps.<cluster-domain>/`
   - **Content type**: `application/json`
   - **Events**: Just the push event
   - **Branch filter**: `master` branch only

## Manual Pipeline Execution

To manually trigger the pipeline:

```bash
# Update the repo-url and service-url in pipelinerun-example.yaml first
oc create -f pipelinerun-example.yaml
```

Monitor the pipeline run:

```bash
# List pipeline runs
oc get pipelineruns

# View logs
oc logs -f <pipelinerun-name>
```

## Troubleshooting

### Common Issues

1. **BuildAh Task Fails**: Ensure you're using `buildah-1-19-0` instead of the default buildah task
2. **Permission Errors**: Verify the RBAC configuration is applied correctly
3. **Webhook Not Triggering**: Check that the EventListener service is running and accessible
4. **BDD Tests Fail**: Ensure the service-url parameter points to the correct route

### Checking Pipeline Status

```bash
# Check all pipeline components
oc get pipeline,pipelinerun,task,taskrun

# Check EventListener
oc get eventlistener

# Check triggers
oc get triggerbinding,triggertemplate,trigger
```

### Viewing Logs

```bash
# View EventListener logs
oc logs -l eventlistener=cd-pipeline-listener

# View pipeline run logs
tkn pipelinerun logs <pipelinerun-name> -f
```

## Customization

### Adding New Tasks

1. Add your task definition to `tasks.yaml`
2. Add the task to the pipeline in `pipeline.yaml`
3. Update runAfter dependencies as needed

### Modifying Parameters

Update pipeline parameters in:
- `pipeline.yaml` for default values
- `triggers.yaml` for webhook-triggered runs
- `pipelinerun-example.yaml` for manual runs

### Environment-Specific Configuration

Update the following for different environments:
- Image registry URL in pipeline parameters
- Service URLs for BDD tests
- Namespace references in RBAC
- Route domains

## Security Considerations

- The pipeline ServiceAccount has cluster-wide permissions
- Consider using namespace-scoped roles for production
- Ensure webhook endpoints are properly secured
- Use secrets for sensitive configuration data

## Team Collaboration

Each team member should:
1. Add one task to the pipeline
2. Test their task individually
3. Export their work to YAML files
4. Commit changes to the `.tekton` folder
5. Next team member applies manifests and continues

This ensures collaborative development while maintaining the pipeline definition in Git.
