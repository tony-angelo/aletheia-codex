# AletheiaCodex API Enablement Script

# Set your project ID
$PROJECT_ID = "aletheia-codex-prod"  # already set

Write-Host "Enabling APIs for project: $PROJECT_ID" -ForegroundColor Green

# Enable all required APIs
gcloud services enable `
  iam.googleapis.com `
  firebase.googleapis.com `
  cloudbuild.googleapis.com `
  cloudfunctions.googleapis.com `
  cloudscheduler.googleapis.com `
  cloudtasks.googleapis.com `
  run.googleapis.com `
  artifactregistry.googleapis.com `
  secretmanager.googleapis.com `
  firestore.googleapis.com `
  storage.googleapis.com `
  monitoring.googleapis.com `
  logging.googleapis.com `
  --project=$PROJECT_ID

Write-Host "APIs enabled successfully!" -ForegroundColor Green
