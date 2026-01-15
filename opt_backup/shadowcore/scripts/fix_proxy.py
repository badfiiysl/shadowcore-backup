#!/usr/bin/env python3
import re

# Read the original file
with open('/opt/shadowcore/real_proxy.py', 'r') as f:
    content = f.read()

# Find the not_found function and everything after it
# We need to move it to the end
lines = content.split('\n')

# Find the not_found function
not_found_start = -1
not_found_end = -1
in_function = False
for i, line in enumerate(lines):
    if 'def not_found' in line:
        not_found_start = i
        in_function = True
    elif in_function and line.strip() == '' and i > not_found_start:
        # Look for end of function (empty line after indented code)
        not_found_end = i
        in_function = False

if not_found_start == -1:
    print("Error: Could not find not_found function")
    exit(1)

# Extract the not_found function
not_found_func = lines[not_found_start:not_found_end]

# Remove it from its current position
del lines[not_found_start:not_found_end]

# Find where to insert it (before the if __name__ block)
insert_point = len(lines)
for i, line in enumerate(lines):
    if '__name__' in line and '__main__' in line:
        insert_point = i
        break

# Insert the not_found function before if __name__ == '__main__':
lines = lines[:insert_point] + [''] + not_found_func + [''] + lines[insert_point:]

# Write the fixed file
with open('/opt/shadowcore/real_proxy.py.fixed', 'w') as f:
    f.write('\n'.join(lines))

print("✅ Created fixed version at /opt/shadowcore/real_proxy.py.fixed")
print("Original backed up to /opt/shadowcore/real_proxy.py.backup.*")
