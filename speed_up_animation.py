import os
import re

template_dir = r"c:\Users\KIIT0001\Desktop\nepal_health_bridge-20260221T085532Z-1-001\nepal_health_bridge\directory\templates"

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            # Speed up the CSS animation from 2.5s to 1.2s
            new_content = re.sub(r'animation:\s*fillBg\s+2\.5s', 'animation: fillBg 1.2s', new_content)
            # Speed up the Redirect Timeout from 2500ms to 1200ms
            new_content = re.sub(r'\}, \s*2500\s*\)', '}, 1200)', new_content)
            new_content = re.sub(r'\}\,\s*2500\s*\)', '}, 1200)', new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
