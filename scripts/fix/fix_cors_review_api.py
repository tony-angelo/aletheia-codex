#!/usr/bin/env python3
"""Script to fix CORS in review_api/main.py"""

import re

# Read the file
with open('functions/review_api/main.py', 'r') as f:
    content = f.read()

# Replace all cors_response calls to include origin parameter
# Pattern: cors_response({...}, status_code)
# Replace with: cors_response({...}, status_code, origin)

# Find all cors_response calls and add origin parameter
pattern = r'return cors_response\((.*?)\)(\s*$)'

def replace_cors_call(match):
    args = match.group(1)
    # Check if origin is already there
    if ', origin)' in args or ',origin)' in args:
        return match.group(0)
    # Add origin parameter
    return f'return cors_response({args}, origin){match.group(2)}'

content = re.sub(pattern, replace_cors_call, content, flags=re.MULTILINE)

# Write back
with open('functions/review_api/main.py', 'w') as f:
    f.write(content)

print("Fixed all cors_response calls in review_api/main.py")