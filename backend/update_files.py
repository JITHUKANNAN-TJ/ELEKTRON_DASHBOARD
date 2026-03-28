import csv
import json

csv_path = r"C:\Users\DELL\Documents\Downloads\Rivers_India.csv"
map_path = r"c:\Users\DELL\OneDrive\jithu\New folder (2)\map.html"
db_path = r"c:\Users\DELL\OneDrive\jithu\New folder (2)\database.html"

# Coordinates mapping for origin
coords = {
    "Ganga": {"lat": 30.9947, "lng": 78.9398},
    "Brahmaputra": {"lat": 30.3333, "lng": 82.0000},
    "Yamuna": {"lat": 31.0140, "lng": 78.4600},
    "Godavari": {"lat": 19.9333, "lng": 73.5333},
    "Krishna": {"lat": 17.9237, "lng": 73.6586},
    "Narmada": {"lat": 22.6710, "lng": 81.7580},
    "Kaveri": {"lat": 12.3850, "lng": 75.4910},
    "Mahanadi": {"lat": 20.2880, "lng": 81.9330},
    "Tapi": {"lat": 21.4330, "lng": 75.5000},
    "Sutlej": {"lat": 30.6830, "lng": 81.2330}
}

html_rows = []
js_regions = {}
optgroup_html = '                    <optgroup label="Rivers of India">\n'

def get_status(pli):
    pli = float(pli)
    if pli >= 5: return "Critical Warning", "error"
    if pli >= 3: return "Highly Polluted", "tertiary"
    if pli >= 2: return "Moderate", "primary"
    return "Acceptable", "secondary"

def get_pollutants(pli):
    pli = float(pli)
    if pli >= 5: return "Sewage, Industrial Waste, Heavy Metals"
    if pli >= 3: return "Agricultural Runoff, Plastics"
    return "Silt, Minor Runoff"

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["name"]
        loc = row["origin_location"]
        pli = float(row["pollution_level_index"])
        wqi = int(pli * 60) # Scaled to look like WQI
        
        status, color = get_status(pli)
        pollutants = get_pollutants(pli)
        
        # Database Row
        r_html = f'''                    <tr class="hover:bg-surface-container-low/30 transition-colors">
                        <td class="px-6 py-4 font-headline font-bold text-base text-primary">{name}</td>
                        <td class="px-6 py-4 text-sm text-on-surface-variant">India ({loc})</td>
                        <td class="px-6 py-4"><span class="font-bold text-{color}">{wqi}</span></td>
                        <td class="px-6 py-4 text-xs">{pollutants}</td>
                        <td class="px-6 py-4"><span class="px-2 py-1 bg-{color}/10 text-{color} text-[10px] font-bold uppercase rounded-full">{status}</span></td>
                        <td class="px-6 py-4 text-right"><button class="text-primary hover:underline text-sm font-medium">Analyze</button></td>
                    </tr>'''
        html_rows.append(r_html)
        
        # Map Region
        lat, lng = coords.get(name, {"lat": 20.0, "lng": 80.0}).values()
        marker_type = "critical" if pli >= 4 else "warning"
        js_regions[f"india_{name.lower()}"] = {
            "lat": lat, "lng": lng, "zoom": 13,
            "markers": [{"lat": lat, "lng": lng, "type": marker_type, "name": f"{name} Origin", "bod": str(int(pli*15))}],
            "droneOffset": {"lat": 0.005, "lng": 0.005}
        }
        
        optgroup_html += f'                        <option value="india_{name.lower()}">{name} ({loc})</option>\n'

optgroup_html += '                    </optgroup>'
all_rows_html = "\n".join(html_rows)

# Update database.html
with open(db_path, "r", encoding="utf-8") as f:
    db_content = f.read()

# insert before </tbody>
db_content = db_content.replace('                </tbody>', all_rows_html + '\n                </tbody>')
with open(db_path, "w", encoding="utf-8") as f:
    f.write(db_content)

# Update map.html
with open(map_path, "r", encoding="utf-8") as f:
    map_content = f.read()

# insert optgroup before </select>
map_content = map_content.replace('                </select>', optgroup_html + '\n                </select>')

# extract regions object
import re
# Append to regions dict
regions_str = json.dumps(js_regions, indent=12)[1:-1] # remove { } to inject inside regions
match = re.search(r'const regions = \{([^}]+?)\n\s+};', map_content, re.DOTALL)
if match:
    old_inner = match.group(1)
    new_inner = old_inner + "," + regions_str
    map_content = map_content.replace(match.group(0), f'const regions = {{{new_inner}\n        }};')

with open(map_path, "w", encoding="utf-8") as f:
    f.write(map_content)

print("Files updated successfully!")
