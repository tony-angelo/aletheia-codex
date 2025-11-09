#!/bin/bash

# Sprint 4 Deployment Script
# Deploys all Sprint 4 components to production

set -e  # Exit on error

echo "=========================================="
echo "Sprint 4 Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI not found. Please install it first."
    exit 1
fi

if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI not found. Please install it first."
    exit 1
fi

print_status "Prerequisites check passed"
echo ""

# Confirm deployment
read -p "Deploy to production? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "=========================================="
echo "Step 1: Deploy Firestore Rules & Indexes"
echo "=========================================="
echo ""

cd "$(dirname "$0")/.."

print_status "Deploying Firestore rules..."
firebase deploy --only firestore:rules --project aletheia-codex

print_status "Deploying Firestore indexes..."
firebase deploy --only firestore:indexes --project aletheia-codex

echo ""
echo "=========================================="
echo "Step 2: Deploy Orchestration Function"
echo "=========================================="
echo ""

cd functions/orchestration

print_status "Deploying orchestration function..."
gcloud functions deploy orchestration \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=orchestrate \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --project=aletheia-codex

cd ../..

echo ""
echo "=========================================="
echo "Step 3: Deploy Notes API Function"
echo "=========================================="
echo ""

cd functions/notes_api

# Create symlink to shared directory if it doesn't exist
if [ ! -L "shared" ]; then
    print_status "Creating symlink to shared directory..."
    ln -s ../orchestration/shared shared
fi

print_status "Deploying notes_api function..."
gcloud functions deploy notes_api \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=notes_api \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=60s \
  --memory=256MB \
  --project=aletheia-codex

cd ../..

echo ""
echo "=========================================="
echo "Step 4: Deploy Frontend Application"
echo "=========================================="
echo ""

cd web

print_status "Installing dependencies..."
npm install

print_status "Building frontend..."
npm run build

print_status "Deploying to Firebase Hosting..."
firebase deploy --only hosting --project aletheia-codex

cd ..

echo ""
echo "=========================================="
echo "Step 5: Verification"
echo "=========================================="
echo ""

print_status "Running smoke tests..."

# Test frontend
echo "Testing frontend..."
if curl -s -o /dev/null -w "%{http_code}" https://aletheia-codex.web.app | grep -q "200"; then
    print_status "Frontend is accessible"
else
    print_error "Frontend is not accessible"
fi

# Test orchestration function
echo "Testing orchestration function..."
response=$(curl -s -w "%{http_code}" -X POST \
  https://us-central1-aletheia-codex.cloudfunctions.net/orchestration \
  -H "Content-Type: application/json" \
  -d '{"noteId":"test","content":"test","userId":"test"}' \
  -o /dev/null)

if [ "$response" = "200" ]; then
    print_status "Orchestration function is responding"
else
    print_warning "Orchestration function returned: $response"
fi

# Test notes API
echo "Testing notes API..."
response=$(curl -s -w "%{http_code}" \
  https://us-central1-aletheia-codex.cloudfunctions.net/notes_api/notes \
  -H "Authorization: Bearer test" \
  -o /dev/null)

if [ "$response" = "200" ]; then
    print_status "Notes API is responding"
else
    print_warning "Notes API returned: $response"
fi

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
print_status "All components deployed successfully"
echo ""
echo "Next steps:"
echo "1. Run manual functional tests"
echo "2. Monitor logs for errors"
echo "3. Verify production behavior"
echo "4. Update team on deployment status"
echo ""
echo "Production URLs:"
echo "  Frontend: https://aletheia-codex.web.app"
echo "  Orchestration: https://us-central1-aletheia-codex.cloudfunctions.net/orchestration"
echo "  Notes API: https://us-central1-aletheia-codex.cloudfunctions.net/notes_api"
echo ""