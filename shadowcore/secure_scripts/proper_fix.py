#!/usr/bin/env python3

with open('/opt/shadowcore/real_proxy.py', 'r') as f:
    content = f.read()

# Find the if __name__ == '__main__': block
lines = content.split('\n')

# Find where the main block starts
main_start = -1
main_end = len(lines)
for i, line in enumerate(lines):
    if '__name__' in line and '__main__' in line:
        main_start = i
        break

if main_start == -1:
    print("Error: Could not find main block")
    exit(1)

# Find where the main block ends (look for app.run)
for i in range(main_start, len(lines)):
    if 'app.run(' in lines[i]:
        main_end = i + 1
        break

# Extract the main block
main_block = lines[main_start:main_end]

# Extract everything AFTER the main block (the endpoints we need to move)
endpoints_block = lines[main_end:]

# Find where the endpoints block actually ends
endpoints_end = len(endpoints_block)
for i in range(len(endpoints_block)):
    if endpoints_block[i].strip() == '':
        endpoints_end = i
        break

# The actual endpoints to move
endpoints_to_move = endpoints_block[:endpoints_end]

# Now reconstruct the file:
# 1. Everything before main block
# 2. The endpoints to move
# 3. The main block
# 4. Anything left after

before_main = lines[:main_start]
remaining_after = endpoints_block[endpoints_end:] if endpoints_end < len(endpoints_block) else []

# Reconstruct
fixed_lines = before_main + [''] + endpoints_to_move + [''] + main_block + remaining_after

# Write the fixed file
with open('/opt/shadowcore/real_proxy.py.fixed2', 'w') as f:
    f.write('\n'.join(fixed_lines))

print("✅ Created properly fixed file at /opt/shadowcore/real_proxy.py.fixed2")
print("The endpoints are now BEFORE the main block and will be registered properly.")
