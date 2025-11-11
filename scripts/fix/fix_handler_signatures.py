#!/usr/bin/env python3
"""Script to fix handler function signatures in review_api/main.py"""

import re

# Read the file
with open('functions/review_api/main.py', 'r') as f:
    content = f.read()

# Update handler function signatures to include origin parameter
handlers = [
    'handle_approve_item',
    'handle_reject_item',
    'handle_batch_approve_items',
    'handle_batch_reject_items',
    'handle_get_user_stats'
]

for handler in handlers:
    # Pattern: def handler_name(request: Request, user_id: str) -> flask.Response:
    pattern = f'def {handler}\\(request: Request, user_id: str\\) -> flask\\.Response:'
    replacement = f'def {handler}(request: Request, user_id: str, origin: str = None) -> flask.Response:'
    content = re.sub(pattern, replacement, content)

# Write back
with open('functions/review_api/main.py', 'w') as f:
    f.write(content)

print("Fixed all handler function signatures in review_api/main.py")