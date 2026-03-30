import os
import re

directory = r"c:\Users\KIIT0001\Downloads\Nepal-health-bridge-master\Nepal-health-bridge-master\nepal_health_bridge\directory\templates\directory"
count = 0

for f in os.listdir(directory):
    if f.endswith('.html'):
        filepath = os.path.join(directory, f)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Fix any {{ ... }} tag that spans multiple lines by collapsing whitespace
        def fix_multiline_var(match):
            inner = match.group(1)
            # Collapse newlines and extra whitespace into single spaces
            cleaned = ' '.join(inner.split())
            return '{{ ' + cleaned + ' }}'
        
        new_content = re.sub(r'\{\{\s*\n\s*(.+?)\s*\}\}', fix_multiline_var, content, flags=re.DOTALL)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(new_content)
            count += 1
            print(f"Fixed multiline tags in: {f}")

print(f"Total files fixed: {count}")
