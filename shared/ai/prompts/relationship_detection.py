"""
Relationship detection prompts for Gemini AI.

These prompts are designed to identify relationships between entities
extracted from text.
"""

RELATIONSHIP_DETECTION_SYSTEM_PROMPT = """You are an expert relationship detection system. Your task is to identify meaningful relationships between entities with high accuracy.

Standard Relationship Types:
1. KNOWS - Person knows another Person
2. WORKS_AT - Person works at Organization
3. LOCATED_IN - Entity is located in Place
4. RELATED_TO - General relationship between entities
5. HAPPENED_AT - Moment happened at Place
6. INVOLVES - Moment involves Entity
7. PART_OF - Entity is part of another Entity
8. CREATED - Person/Organization created Thing/Concept
9. OWNS - Person/Organization owns Thing/Organization
10. MEMBER_OF - Person is member of Organization
11. MANAGES - Person manages Person/Organization
12. FOUNDED - Person founded Organization
13. ATTENDED - Person attended Moment/Organization
14. STUDIED_AT - Person studied at Organization

Guidelines:
- Only create relationships that are explicitly stated or strongly implied
- Provide confidence scores based on evidence strength (0.0 to 1.0)
- Include relevant properties for each relationship
- Use standard relationship types when possible
- Create custom relationship types for unique relationships
- Confidence > 0.9: Explicitly stated
- Confidence 0.7-0.9: Strongly implied
- Confidence 0.5-0.7: Moderately implied
- Confidence < 0.5: Weakly implied (may be excluded)

Output Format:
Return ONLY a valid JSON array of relationships. No markdown, no explanations, just the JSON array.

Example:
[
  {
    "source_entity": "Steve Jobs",
    "target_entity": "Apple",
    "relationship_type": "FOUNDED",
    "properties": {
      "year": "1976",
      "role": "Co-founder"
    },
    "confidence": 0.98
  },
  {
    "source_entity": "Apple",
    "target_entity": "Cupertino",
    "relationship_type": "LOCATED_IN",
    "properties": {
      "headquarters": true
    },
    "confidence": 0.95
  }
]
"""


def build_relationship_detection_prompt(text: str, entities: list) -> str:
    """
    Build the complete relationship detection prompt.
    
    Args:
        text: Original text containing the entities
        entities: List of entity dictionaries
        
    Returns:
        Complete prompt string
    """
    # Format entities for the prompt
    entities_text = "\n".join([
        f"- {e.get('name', 'Unknown')} ({e.get('type', 'Unknown')})"
        for e in entities
    ])
    
    return f"""{RELATIONSHIP_DETECTION_SYSTEM_PROMPT}

Original Text:
&quot;&quot;&quot;
{text}
&quot;&quot;&quot;

Entities Found:
{entities_text}

Identify all meaningful relationships between these entities based on the original text.
Return ONLY the JSON array of relationships, no markdown formatting, no explanations."""


# Few-shot examples for improved accuracy
RELATIONSHIP_DETECTION_EXAMPLES = [
    {
        "text": "Steve Jobs founded Apple in 1976 in Cupertino, California.",
        "entities": [
            {"name": "Steve Jobs", "type": "Person"},
            {"name": "Apple", "type": "Organization"},
            {"name": "Cupertino", "type": "Place"},
            {"name": "California", "type": "Place"},
            {"name": "1976", "type": "Moment"}
        ],
        "output": [
            {
                "source_entity": "Steve Jobs",
                "target_entity": "Apple",
                "relationship_type": "FOUNDED",
                "properties": {"year": "1976"},
                "confidence": 0.98
            },
            {
                "source_entity": "Apple",
                "target_entity": "Cupertino",
                "relationship_type": "LOCATED_IN",
                "properties": {"type": "headquarters"},
                "confidence": 0.95
            },
            {
                "source_entity": "Cupertino",
                "target_entity": "California",
                "relationship_type": "LOCATED_IN",
                "properties": {},
                "confidence": 0.98
            },
            {
                "source_entity": "Apple",
                "target_entity": "1976",
                "relationship_type": "FOUNDED_IN",
                "properties": {},
                "confidence": 0.95
            }
        ]
    },
    {
        "text": "I met Sarah at the conference in London. She works at Google as a software engineer.",
        "entities": [
            {"name": "Sarah", "type": "Person"},
            {"name": "conference", "type": "Moment"},
            {"name": "London", "type": "Place"},
            {"name": "Google", "type": "Organization"}
        ],
        "output": [
            {
                "source_entity": "Sarah",
                "target_entity": "Google",
                "relationship_type": "WORKS_AT",
                "properties": {"role": "software engineer"},
                "confidence": 0.95
            },
            {
                "source_entity": "conference",
                "target_entity": "London",
                "relationship_type": "HAPPENED_AT",
                "properties": {},
                "confidence": 0.92
            },
            {
                "source_entity": "Sarah",
                "target_entity": "conference",
                "relationship_type": "ATTENDED",
                "properties": {},
                "confidence": 0.88
            }
        ]
    }
]


def build_relationship_detection_prompt_with_examples(text: str, entities: list) -> str:
    """
    Build relationship detection prompt with few-shot examples.
    
    Args:
        text: Original text containing the entities
        entities: List of entity dictionaries
        
    Returns:
        Complete prompt string with examples
    """
    examples_text = "\n\n".join([
        f"Example {i+1}:\nText: {ex['text']}\nEntities: {ex['entities']}\nOutput: {ex['output']}"
        for i, ex in enumerate(RELATIONSHIP_DETECTION_EXAMPLES)
    ])
    
    # Format entities for the prompt
    entities_text = "\n".join([
        f"- {e.get('name', 'Unknown')} ({e.get('type', 'Unknown')})"
        for e in entities
    ])
    
    return f"""{RELATIONSHIP_DETECTION_SYSTEM_PROMPT}

Here are some examples of correct relationship detection:

{examples_text}

Now identify relationships in this text:

Original Text:
&quot;&quot;&quot;
{text}
&quot;&quot;&quot;

Entities Found:
{entities_text}

Return ONLY the JSON array of relationships, no markdown formatting, no explanations."""