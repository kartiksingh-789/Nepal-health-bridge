import os
file_path = r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge\directory\templates\directory\landing.html"
with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Reverse string replacements
old_link = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap"
new_link = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
html_content = html_content.replace(old_link, new_link)

html_content = html_content.replace("'Montserrat'", "'Plus Jakarta Sans'")
html_content = html_content.replace("Montserrat", "Plus Jakarta Sans")

# Revert the custom * injection
old_star_block = """        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
            font-family: 'Plus Jakarta Sans', sans-serif !important; 
        }

        body {
            background-color: var(--bg-light);"""

new_star_block = """        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-light);"""

html_content = html_content.replace(old_star_block, new_star_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Font reverted to Plus Jakarta Sans successfully.")
