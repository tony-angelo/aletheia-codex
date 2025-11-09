"""Gemini AI client with automatic API key retrieval."""

import google.generativeai as genai
from google.cloud import secretmanager
from typing import Optional

_configured: bool = False


def get_secret(project_id: str, secret_id: str, version: str = "latest") -> str:
    """
    Retrieve a secret from Secret Manager.
    
    Args:
        project_id: GCP project ID
        secret_id: Secret name
        version: Secret version (default: latest)
        
    Returns:
        Secret value as string
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


def configure_gemini(project_id: str = "aletheia-codex-prod"):
    """
    Configure the Gemini API with credentials from Secret Manager.
    
    Args:
        project_id: GCP project ID
    """
    global _configured
    if not _configured:
        api_key = get_secret(project_id, "GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        _configured = True


def get_model(model_name: str = "gemini-1.5-flash") -> genai.GenerativeModel:
    """
    Get a Gemini generative model.
    
    Args:
        model_name: Model identifier (default: gemini-1.5-flash)
        
    Returns:
        Initialized GenerativeModel
    """
    configure_gemini()
    return genai.GenerativeModel(model_name)


def generate_text(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Generate text using Gemini.
    
    Args:
        prompt: Input prompt
        model_name: Model to use
        
    Returns:
        Generated text
    """
    model = get_model(model_name)
    response = model.generate_content(prompt)
    return response.text


def generate_embeddings(text: str, model_name: str = "models/text-embedding-004") -> list:
    """
    Generate embeddings for text.
    
    Args:
        text: Input text
        model_name: Embedding model to use
        
    Returns:
        List of embedding values
    """
    configure_gemini()
    result = genai.embed_content(
        model=model_name,
        content=text,
        task_type="retrieval_document"
    )
    return result['embedding']
