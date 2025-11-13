#!/bin/bash
set -e

echo "Creating Backend Services for Serverless NEGs..."
echo ""

# Function to create backend service for serverless NEG
create_backend_service() {
    local name=$1
    local neg_name=$2
    
    echo "Creating backend service: backend-${name}..."
    
    # Create backend service (no protocol specified for serverless)
    gcloud compute backend-services create backend-${name} \
        --global \
        --load-balancing-scheme=EXTERNAL_MANAGED
    
    # Add NEG to backend service
    gcloud compute backend-services add-backend backend-${name} \
        --global \
        --network-endpoint-group=${neg_name} \
        --network-endpoint-group-region=us-central1
    
    echo "✅ Backend service backend-${name} created"
    echo ""
}

# Create backend services for all functions
create_backend_service "graphfunction" "neg-graphfunction"
create_backend_service "notesapifunction" "neg-notesapifunction"
create_backend_service "orchestrate" "neg-orchestrate"
create_backend_service "orchestration" "neg-orchestration"
create_backend_service "reviewapifunction" "neg-reviewapifunction"
create_backend_service "ingestion" "neg-ingestion"

echo ""
echo "✅ All backend services created successfully!"
echo ""
echo "Listing backend services:"
gcloud compute backend-services list

