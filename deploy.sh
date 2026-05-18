#!/bin/bash

# Configuration - Update these
PROJECT_ID="your-google-cloud-project-id"
REGION="us-central1"
BACKEND_SERVICE="portfolio-analyzer-api"
FRONTEND_SERVICE="portfolio-analyzer-ui"

# 1. Build and Push Backend
echo "Building Backend..."
docker build -t gcr.io/$PROJECT_ID/$BACKEND_SERVICE ./backend
docker push gcr.io/$PROJECT_ID/$BACKEND_SERVICE

# 2. Deploy Backend to Cloud Run
echo "Deploying Backend..."
gcloud run deploy $BACKEND_SERVICE \
  --image gcr.io/$PROJECT_ID/$BACKEND_SERVICE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GITHUB_TOKEN=your_token_here,GEMINI_API_KEY=your_key_here

# 3. Get Backend URL (IMPORTANT: You will need this for the frontend)
BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --platform managed --region $REGION --format 'value(status.url)')
echo "Backend URL is: $BACKEND_URL"

# 4. Update Frontend API URL in app.js
# (In a real CI/CD you might use build-args, but here we'll do it manually)
echo "Update your frontend/app.js API_BASE_URL to $BACKEND_URL before proceeding."

# 5. Build and Push Frontend
echo "Building Frontend..."
docker build -t gcr.io/$PROJECT_ID/$FRONTEND_SERVICE ./frontend
docker push gcr.io/$PROJECT_ID/$FRONTEND_SERVICE

# 6. Deploy Frontend
echo "Deploying Frontend..."
gcloud run deploy $FRONTEND_SERVICE \
  --image gcr.io/$PROJECT_ID/$FRONTEND_SERVICE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "Deployment Complete!"
