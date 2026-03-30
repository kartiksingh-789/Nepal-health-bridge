import re
import io

with open("db.sqlite3", "rb") as f:
    data = f.read()

urls = re.findall(b"https://images.unsplash.com/[a-zA-Z0-9-?&=/._]+", data)
unique_urls = set([u.decode('utf-8') for u in urls])

with io.open('urls_utf8.txt', 'w', encoding='utf-8') as fh:
    for u in unique_urls:
        fh.write(u + '\n')
