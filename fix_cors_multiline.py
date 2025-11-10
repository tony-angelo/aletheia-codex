#!/usr/bin/env python3
"""Script to fix multi-line CORS calls in review_api/main.py"""

# Read the file
with open('functions/review_api/main.py', 'r') as f:
    lines = f.readlines()

# Process line by line, looking for cors_response calls
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this line contains "return cors_response"
    if 'return cors_response(' in line:
        # Look ahead to find the closing parenthesis
        j = i
        paren_count = line.count('(') - line.count(')')
        
        while paren_count > 0 and j < len(lines) - 1:
            j += 1
            paren_count += lines[j].count('(') - lines[j].count(')')
        
        # Now j points to the line with the closing parenthesis
        # Check if origin is already in the last line
        if ', origin)' not in lines[j] and ',origin)' not in lines[j]:
            # Add origin before the closing parenthesis
            lines[j] = lines[j].replace(')', ', origin)', 1)
        
        # Add all lines from i to j
        for k in range(i, j + 1):
            new_lines.append(lines[k])
        i = j + 1
    else:
        new_lines.append(line)
        i += 1

# Write back
with open('functions/review_api/main.py', 'w') as f:
    f.writelines(new_lines)

print("Fixed all multi-line cors_response calls in review_api/main.py")