#!/bin/bash

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="us-central1"
SERVICE_NAME="eval-api"

echo "Deploying to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  --project=$PROJECT_ID

# Deploy to Cloud Run with CPU always allocated for background tasks
echo "Building and deploying..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --cpu-always-allocated \
  --set-env-vars GCP_PROJECT_ID=$PROJECT_ID \
  --project=$PROJECT_ID

# Get the service URL
echo ""
echo "Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --project=$PROJECT_ID \
  --format 'value(status.url)')

echo "Service URL: $SERVICE_URL"
echo "API Docs: $SERVICE_URL/docs"
echo "Health Check: $SERVICE_URL/health"
