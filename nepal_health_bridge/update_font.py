import os
file_path = r"c:\Users\KIIT0001\Desktop\mini proj\Nepal-health-bridge-master\nepal_health_bridge\directory\templates\directory\landing.html"
with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace google font link
old_link = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap"
new_link = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap"
html_content = html_content.replace(old_link, new_link)

# Replace all occurrences of Plus Jakarta Sans -> Montserrat
html_content = html_content.replace("'Plus Jakarta Sans'", "'Montserrat'")
html_content = html_content.replace("Plus Jakarta Sans", "Montserrat")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Font updated to Montserrat successfully.")
