# Ensure we’re at the project root
cd C:\dev\aletheia-codex

# Ensure infrastructure folder exists
New-Item -ItemType Directory -Path .\infrastructure -Force | Out-Null

# Create the script with your project prefilled
$saScript = @'
# AletheiaCodex Service Account Setup Script

# Set your project ID
$PROJECT_ID = "aletheia-codex-prod"  # already set
$REGION = "us-central1"
$RUNTIME_SA = "aletheia-runtime-sa"
$RUNTIME_SA_EMAIL = "$RUNTIME_SA@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "Setting up service accounts for: $PROJECT_ID" -ForegroundColor Green

# Get project number
$PROJECT_NUMBER = (gcloud projects describe $PROJECT_ID --format="value(projectNumber)").Trim()
$CLOUD_BUILD_SA = "$PROJECT_NUMBER@cloudbuild.gserviceaccount.com"

Write-Host "Project Number: $PROJECT_NUMBER" -ForegroundColor Yellow
Write-Host "Runtime SA: $RUNTIME_SA_EMAIL" -ForegroundColor Yellow
Write-Host "Cloud Build SA: $CLOUD_BUILD_SA" -ForegroundColor Yellow

# Create runtime service account (idempotent; will no-op if exists)
Write-Host "Creating runtime service account..." -ForegroundColor Green
gcloud iam service-accounts create $RUNTIME_SA `
  --display-name="Aletheia Runtime Service Account" `
  --project=$PROJECT_ID

# Grant permissions to runtime SA
Write-Host "Granting permissions to runtime SA..." -ForegroundColor Green
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$RUNTIME_SA_EMAIL" `
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$RUNTIME_SA_EMAIL" `
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$RUNTIME_SA_EMAIL" `
  --role="roles/cloudtasks.enqueuer"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$RUNTIME_SA_EMAIL" `
  --role="roles/cloudfunctions.invoker"

# Configure Cloud Build SA (used by Firebase/GCloud deploys)
Write-Host "Configuring Cloud Build SA..." -ForegroundColor Green
gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$CLOUD_BUILD_SA" `
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$CLOUD_BUILD_SA" `
  --role="roles/firebase.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$CLOUD_BUILD_SA" `
  --role="roles/cloudfunctions.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID `
  --member="serviceAccount:$CLOUD_BUILD_SA" `
  --role="roles/iam.serviceAccountUser"

Write-Host "Service accounts configured successfully!" -ForegroundColor Green
'@

Set-Content -Path .\infrastructure\setup-service-accounts.ps1 -Value $saScript -Encoding UTF8

# Show the file to confirm it exists and has content
Get-Item .\infrastructure\setup-service-accounts.ps1 | Format-List Name,Length,FullName
