#!/bin/bash
set -e

echo "Creating Serverless Network Endpoint Groups (NEGs)..."
echo ""

# Gen 2 Functions (Cloud Run Services)
echo "Creating NEG for graphfunction..."
gcloud compute network-endpoint-groups create neg-graphfunction \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=graphfunction

echo "Creating NEG for notesapifunction..."
gcloud compute network-endpoint-groups create neg-notesapifunction \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=notesapifunction

echo "Creating NEG for orchestrate..."
gcloud compute network-endpoint-groups create neg-orchestrate \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=orchestrate

echo "Creating NEG for orchestration..."
gcloud compute network-endpoint-groups create neg-orchestration \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=orchestration

echo "Creating NEG for reviewapifunction..."
gcloud compute network-endpoint-groups create neg-reviewapifunction \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-run-service=reviewapifunction

# Gen 1 Function (Cloud Functions)
echo "Creating NEG for ingestion (Gen 1)..."
gcloud compute network-endpoint-groups create neg-ingestion \
    --region=us-central1 \
    --network-endpoint-type=serverless \
    --cloud-function=ingestion

echo ""
echo "✅ All NEGs created successfully!"
echo ""
echo "Listing NEGs:"
gcloud compute network-endpoint-groups list

