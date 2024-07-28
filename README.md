Here's an updated README that includes steps for installing Prometheus and Grafana for monitoring the METAR/TAF Decoder application on AWS EKS.

```markdown
# METAR/TAF Decoder Deployment Guide

This guide provides step-by-step instructions for deploying the METAR/TAF Decoder application to AWS EKS using GitHub Actions, and setting up Prometheus and Grafana for monitoring.

## Prerequisites

- GitHub account
- AWS account with EKS cluster set up
- Docker Hub account (or another container registry)
- AWS CLI installed and configured
- kubectl installed and configured to work with your EKS cluster
- Helm installed (for Prometheus and Grafana installation)

## Step 1: Prepare Your Repository

1. Push your code to a GitHub repository.
2. Create a `Dockerfile` in the root of your repository:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

3. Create a `requirements.txt` file with the following contents:

```
streamlit
boto3
```

## Step 2: Set Up GitHub Secrets

In your GitHub repository, go to Settings > Secrets and add the following secrets:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password

## Step 3: Create GitHub Actions Workflow

Create a file named `.github/workflows/deploy.yml` with the following content:

```yaml
name: Deploy to EKS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2  # Change this to your AWS region

    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build, tag, and push image to Docker Hub
      env:
        DOCKER_REPO: your-dockerhub-username/metar-taf-decoder
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $DOCKER_REPO:$IMAGE_TAG .
        docker push $DOCKER_REPO:$IMAGE_TAG

    - name: Update kube config
      run: aws eks get-token --cluster-name your-cluster-name | kubectl apply -f -

    - name: Deploy to EKS
      run: |
        kubectl set image deployment/metar-taf-decoder metar-taf-decoder=$DOCKER_REPO:$IMAGE_TAG
        kubectl rollout status deployment/metar-taf-decoder
```

## Step 4: Prepare Kubernetes Manifests

Create a file named `kubernetes/deployment.yml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metar-taf-decoder
spec:
  replicas: 1
  selector:
    matchLabels:
      app: metar-taf-decoder
  template:
    metadata:
      labels:
        app: metar-taf-decoder
    spec:
      containers:
      - name: metar-taf-decoder
        image: your-dockerhub-username/metar-taf-decoder:latest
        ports:
        - containerPort: 8501
```

Create a file named `kubernetes/service.yml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: metar-taf-decoder
spec:
  selector:
    app: metar-taf-decoder
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8501
  type: LoadBalancer
```

## Step 5: Initial Deployment

1. Apply the Kubernetes manifests:

```bash
kubectl apply -f kubernetes/deployment.yml
kubectl apply -f kubernetes/service.yml
```

2. Push your code to the main branch of your GitHub repository.

## Step 6: Verify Deployment

1. Check the status of your deployment:

```bash
kubectl get deployments
kubectl get services
```

2. Get the external IP of your LoadBalancer service:

```bash
kubectl get services metar-taf-decoder
```

3. Access your application using the external IP.

## Step 7: Install Prometheus and Grafana for Monitoring

### Install Prometheus

1. Add the Prometheus Helm repository:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

2. Install Prometheus using Helm:

```bash
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --create-namespace
```

### Install Grafana

1. Add the Grafana Helm repository:

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Install Grafana using Helm:

```bash
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set adminPassword='admin' \
  --set service.type=LoadBalancer
```

3. Get the Grafana admin password:

```bash
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

4. Get the Grafana service IP:

```bash
kubectl get svc --namespace monitoring grafana
```

### Configure Prometheus as a Data Source in Grafana

1. Access Grafana using the external IP and login with the username `admin` and the password obtained above.
2. Add Prometheus as a data source in Grafana:
   - Go to Configuration > Data Sources.
   - Click "Add data source".
   - Select "Prometheus".
   - Set the URL to `http://prometheus-server.monitoring.svc.cluster.local:80`.
   - Click "Save & Test".

## Step 8: Monitoring Metrics

### Metrics to Monitor

Monitor the following metrics for your METAR/TAF Decoder application:

- **CPU Usage**: `container_cpu_usage_seconds_total`
- **Memory Usage**: `container_memory_usage_bytes`
- **Network Traffic**: `container_network_receive_bytes_total`, `container_network_transmit_bytes_total`
- **Request Latency**: Custom metrics if available (e.g., response time of the Streamlit app)

### Creating Grafana Dashboards

1. In Grafana, go to Dashboards > Manage > New Dashboard.
2. Add panels for the metrics listed above.
3. Save the dashboard for ongoing monitoring.

## Continuous Deployment

With this setup, every push to the main branch will trigger a new deployment to your EKS cluster.

## Troubleshooting

- Check GitHub Actions logs for any deployment errors.
- Use `kubectl logs` and `kubectl describe` commands to diagnose issues with pods.
- Ensure all required AWS permissions are set up correctly.

```

This README provides a comprehensive guide for deploying your Streamlit application to AWS EKS using GitHub Actions, and setting up Prometheus and Grafana for monitoring. Remember to replace placeholders like `your-dockerhub-username`, `your-cluster-name`, and adjust any region-specific settings to match your AWS setup.