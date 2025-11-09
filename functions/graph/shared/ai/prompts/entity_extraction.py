"""
Entity extraction prompts for Gemini AI.

These prompts are designed to extract structured entity information
from natural language text.
"""

ENTITY_EXTRACTION_SYSTEM_PROMPT = """You are an expert entity extraction system. Your task is to identify and extract entities from text with high accuracy.

Entity Types:
1. Person - Individual people (e.g., "John Smith", "Dr. Jane Doe")
2. Organization - Companies, institutions, groups (e.g., "Google", "MIT", "The Beatles")
3. Place - Locations, cities, countries, buildings (e.g., "New York", "Eiffel Tower", "California")
4. Concept - Ideas, theories, methodologies (e.g., "Machine Learning", "Democracy", "Agile")
5. Moment - Events, dates, time periods (e.g., "World War II", "2024 Olympics", "Renaissance")
6. Thing - Physical objects, products, items (e.g., "iPhone", "The Mona Lisa", "Tesla Model 3")

Guidelines:
- Extract ALL relevant entities, even if mentioned briefly
- Provide confidence scores based on context clarity (0.0 to 1.0)
- Include relevant properties for each entity
- Use the entity's most common or formal name
- For ambiguous cases, use the most likely interpretation
- Confidence > 0.9: Very clear and unambiguous
- Confidence 0.7-0.9: Clear with good context
- Confidence 0.5-0.7: Somewhat ambiguous
- Confidence < 0.5: Very ambiguous (may be excluded)

Output Format:
Return ONLY a valid JSON array of entities. No markdown, no explanations, just the JSON array.

Example:
[
  {
    "type": "Person",
    "name": "Albert Einstein",
    "properties": {
      "occupation": "Physicist",
      "nationality": "German-American"
    },
    "confidence": 0.95
  },
  {
    "type": "Concept",
    "name": "Theory of Relativity",
    "properties": {
      "field": "Physics",
      "year": "1905"
    },
    "confidence": 0.92
  }
]
"""


def build_entity_extraction_prompt(text: str) -> str:
    """
    Build the complete entity extraction prompt.
    
    Args:
        text: Input text to extract entities from
        
    Returns:
        Complete prompt string
    """
    return f"""{ENTITY_EXTRACTION_SYSTEM_PROMPT}

Text to analyze:
&quot;&quot;&quot;
{text}
&quot;&quot;&quot;

Extract all entities from the above text and return them as a JSON array following the format specified above.
Remember: Return ONLY the JSON array, no markdown formatting, no explanations."""


# Few-shot examples for improved accuracy
ENTITY_EXTRACTION_EXAMPLES = [
    {
        "input": "Steve Jobs founded Apple in 1976 in Cupertino, California. He revolutionized personal computing with the Macintosh.",
        "output": [
            {
                "type": "Person",
                "name": "Steve Jobs",
                "properties": {
                    "role": "Founder",
                    "known_for": "Apple, Macintosh"
                },
                "confidence": 0.98
            },
            {
                "type": "Organization",
                "name": "Apple",
                "properties": {
                    "founded": "1976",
                    "industry": "Technology"
                },
                "confidence": 0.98
            },
            {
                "type": "Place",
                "name": "Cupertino",
                "properties": {
                    "state": "California",
                    "country": "USA"
                },
                "confidence": 0.95
            },
            {
                "type": "Place",
                "name": "California",
                "properties": {
                    "type": "State",
                    "country": "USA"
                },
                "confidence": 0.95
            },
            {
                "type": "Thing",
                "name": "Macintosh",
                "properties": {
                    "type": "Computer",
                    "manufacturer": "Apple"
                },
                "confidence": 0.92
            },
            {
                "type": "Moment",
                "name": "1976",
                "properties": {
                    "event": "Apple founding"
                },
                "confidence": 0.90
            }
        ]
    },
    {
        "input": "I attended the AI conference in London last week. The keynote on deep learning was fascinating.",
        "output": [
            {
                "type": "Moment",
                "name": "AI conference",
                "properties": {
                    "type": "Conference",
                    "topic": "Artificial Intelligence"
                },
                "confidence": 0.88
            },
            {
                "type": "Place",
                "name": "London",
                "properties": {
                    "country": "United Kingdom"
                },
                "confidence": 0.95
            },
            {
                "type": "Concept",
                "name": "Deep Learning",
                "properties": {
                    "field": "Artificial Intelligence"
                },
                "confidence": 0.92
            }
        ]
    }
]


def build_entity_extraction_prompt_with_examples(text: str) -> str:
    """
    Build entity extraction prompt with few-shot examples.
    
    Args:
        text: Input text to extract entities from
        
    Returns:
        Complete prompt string with examples
    """
    examples_text = "\n\n".join([
        f"Example {i+1}:\nInput: {ex['input']}\nOutput: {ex['output']}"
        for i, ex in enumerate(ENTITY_EXTRACTION_EXAMPLES)
    ])
    
    return f"""{ENTITY_EXTRACTION_SYSTEM_PROMPT}

Here are some examples of correct entity extraction:

{examples_text}

Now extract entities from this text:
&quot;&quot;&quot;
{text}
&quot;&quot;&quot;

Return ONLY the JSON array of entities, no markdown formatting, no explanations."""