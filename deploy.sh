#!/bin/bash

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo "📦 Using project: $PROJECT_ID"

# Build the container in europe-west1
echo "🏗️ Building container in europe-west1..."
gcloud builds submit \
    --tag gcr.io/$PROJECT_ID/flex-checker \
    --region=europe-west1

# Deploy to Cloud Run in europe-west2
echo "🚀 Deploying to Cloud Run in europe-west2..."
gcloud run deploy flex-checker \
    --image gcr.io/$PROJECT_ID/flex-checker \
    --platform managed \
    --region=europe-west2 \
    --min-instances 0 \
    --max-instances 1 \
    --concurrency 1 \
    --memory 2Gi \
    --timeout 300s

# Get the latest revision
echo "📋 Getting latest revision..."
LATEST_REVISION=$(gcloud run revisions list --service flex-checker --region europe-west2 --format="value(name)" --limit 1)

# Get logs for verification
echo "📜 Getting logs for verification..."
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=flex-checker" --limit 50

# Get the service URL
echo "🔗 Getting service URL..."
SERVICE_URL=$(gcloud run services describe flex-checker --region europe-west2 --format "value(status.url)")

echo "✅ Deployment complete!"
echo "Service URL: $SERVICE_URL"
echo "To test: curl -X POST $SERVICE_URL"