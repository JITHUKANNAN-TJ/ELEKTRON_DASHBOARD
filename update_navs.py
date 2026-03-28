import re

files = ["index.html", "map.html", "database.html", "analytics.html"]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    content = re.sub(r'href="#">Controls</a>', r'href="air_quality.html">Air Quality</a>', content)
    
    # Safe regex string
    target = r'data-icon="settings_input_component">settings_input_component</span>\s*<span class="font-\[\'Inter\'\] font-medium text-\[10px\] uppercase tracking-wider">Controls</span>'
    repl = r'data-icon="air">air</span>\n            <span class="font-[\'Inter\'] font-medium text-[10px] uppercase tracking-wider">Air Quality</span>'
    
    content = re.sub(target, repl, content)
    
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)

print("Navigation Links Updated!")
