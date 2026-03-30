import os
import re

directory = r"c:\Users\KIIT0001\Downloads\Nepal-health-bridge-master\Nepal-health-bridge-master\nepal_health_bridge\directory\templates\directory"
count = 0

for root, _, files in os.walk(directory):
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Use regex to insert spaces around == inside {% if ... %} or {% elif ... %}
            # We specifically target cases like `patient.gender=='male'` or `selected_status == 'upcoming'` 
            
            def repl_eq(match):
                inner = match.group(1)
                # target == missing spaces
                # Example: `patient.gender=='male'` -> `patient.gender == 'male'`
                fixed_inner = re.sub(r'(?<!\s)==(?!\s)', ' == ', inner)
                fixed_inner = re.sub(r'\s+==(?!\s)', ' == ', fixed_inner)
                fixed_inner = re.sub(r'(?<!\s)==\s+', ' == ', fixed_inner)
                return "{%" + fixed_inner + "%}"

            new_content = re.sub(r'\{%([^%]+)%\}', repl_eq, content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                count += 1
                print(f"Fixed: {f}")

print(f"Total fixed files: {count}")
