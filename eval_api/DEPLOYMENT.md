# Cloud Run Deployment Guide

## Quick Deploy

1. Set your project ID:
```bash
export GCP_PROJECT_ID="your-project-id"
```

2. Run deployment:
```bash
./deploy.sh
```

## Manual Deployment

If you prefer manual control:

```bash
# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com aiplatform.googleapis.com

# Deploy
gcloud run deploy eval-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --cpu-always-allocated \
  --set-env-vars GCP_PROJECT_ID=your-project-id

# Get URL
gcloud run services describe eval-api --region us-central1 --format 'value(status.url)'
```

## Testing

```bash
# Health check
curl https://your-service-url/health

# Start evaluation
curl -X POST https://your-service-url/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test-123",
    "query": "What is AI?",
    "response": "AI is artificial intelligence..."
  }'

# Check status
curl https://your-service-url/evaluation/test-123
```

## Background Tasks Note

Current deployment uses `--cpu-always-allocated` to support FastAPI BackgroundTasks. This keeps CPU active after requests complete but increases costs (~$0.05/hour vs $0.000024/GB-sec).

### Production Upgrade: Cloud Tasks

For production, replace BackgroundTasks with Cloud Tasks:

1. Add endpoint in `eval_api.py`:
```python
@app.post("/run-eval/{conv_id}")
async def run_eval(conv_id: str, query: str, response: str):
    run_evaluation(conv_id, query, response)
    return {"status": "completed"}
```

2. Install Cloud Tasks client:
```bash
pip install google-cloud-tasks
```

3. Modify `/evaluate` to queue tasks instead of using BackgroundTasks.

This provides reliable, retryable background processing without keeping CPU allocated.

## Storage

Current JSON file storage works for dev. For production:
- **Firestore**: Document-based, real-time
- **Cloud SQL**: Relational database
- **Cloud Storage**: Large-scale file storage

## Monitoring

- View logs: `gcloud run logs read eval-api --region us-central1`
- Console: https://console.cloud.google.com/run
- Vertex AI quotas: https://console.cloud.google.com/iam-admin/quotas

## Costs

- Cloud Run: ~$0.000024/GB-sec (with always-allocated: ~$0.05/hour)
- Vertex AI: Per evaluation request
- Network egress: $0.12/GB after 1GB free
