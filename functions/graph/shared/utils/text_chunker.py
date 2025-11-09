"""Text chunking utilities for document processing."""

import re
from typing import List, Dict

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict[str, any]]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Input text
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks in characters
        
    Returns:
        List of chunk dictionaries with text and position info
    """
    # Split by sentences first (simple approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    position = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # If adding this sentence exceeds chunk_size, save current chunk
        if current_length + sentence_length > chunk_size and current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'start_pos': position,
                'end_pos': position + len(chunk_text),
                'length': len(chunk_text)
            })
            
            # Start new chunk with overlap
            overlap_text = chunk_text[-overlap:] if len(chunk_text) > overlap else chunk_text
            current_chunk = [overlap_text, sentence]
            current_length = len(overlap_text) + sentence_length
            position += len(chunk_text) - len(overlap_text)
        else:
            current_chunk.append(sentence)
            current_length += sentence_length
    
    # Add the last chunk
    if current_chunk:
        chunk_text = ' '.join(current_chunk)
        chunks.append({
            'text': chunk_text,
            'start_pos': position,
            'end_pos': position + len(chunk_text),
            'length': len(chunk_text)
        })
    
    return chunks
