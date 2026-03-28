import csv
import json

csv_path = r"C:\Users\DELL\Documents\Downloads\Rivers_India.csv"
out_path = r"c:\Users\DELL\OneDrive\jithu\New folder (2)\backend\out_utf8.txt"

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

html_rows = []
js_regions = {}
optgroup_html = '                    <optgroup label="Rivers of India">\n'

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["name"]
        loc = row["origin_location"]
        pli = float(row["pollution_level_index"])
        wqi = int(pli * 60)
        
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

with open(out_path, "w", encoding="utf-8") as f:
    f.write("===DB_ROWS===\n")
    f.write("\n".join(html_rows))
    f.write("\n===OPTGROUP===\n")
    f.write(optgroup_html)
    f.write("\n===REGIONS===\n")
    f.write(json.dumps(js_regions, indent=12)[2:-2])
    f.write("\n")
