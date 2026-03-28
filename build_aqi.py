import re

with open('analytics.html', 'r', encoding='utf-8') as f:
    content = f.read()

head_nav = re.search(r'(?s)(.*?<main[^>]*>)', content).group(1)
bottom_nav = re.search(r'(?s)(</main>.*)', content).group(1)

# Modify top nav for active state
head_nav = head_nav.replace('href="analytics.html"', 'href="analytics.html" class="text-slate-500 dark:text-slate-400 hover:text-cyan-600 transition-colors"')
head_nav = head_nav.replace('class="text-slate-500 dark:text-slate-400 hover:text-cyan-600 transition-colors pb-1 font-medium"', 'class="text-slate-500 dark:text-slate-400 hover:text-cyan-600 transition-colors"')
head_nav = head_nav.replace('<a class="text-slate-500 dark:text-slate-400 hover:text-cyan-600 transition-colors"\n                        href="#">Controls</a>', '<a class="text-cyan-700 dark:text-cyan-400 border-b-2 border-cyan-700 dark:border-cyan-400 pb-1 font-medium"\n                        href="air_quality.html">Air Quality</a>')

# Strip old scripts
bottom_nav = re.sub(r'(?s)<script>.*?</script>', '', bottom_nav)
# Change controls icon in bottom nav of this new file
bottom_nav = bottom_nav.replace('data-icon="settings_input_component">settings_input_component</span>', 'data-icon="air">air</span>')
bottom_nav = bottom_nav.replace('uppercase tracking-wider">Controls</span>', 'uppercase tracking-wider">Air Quality</span>')

new_main = """
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div class="space-y-1">
                <p class="text-xs font-bold uppercase tracking-[0.15em] text-on-surface-variant/70">Atmospheric Data</p>
                <h2 class="font-headline text-3xl font-bold text-primary">Live Air Quality Tracker</h2>
            </div>
            <div class="flex flex-wrap gap-3">
                <div class="px-5 py-2.5 rounded-xl bg-surface-container-highest text-primary font-medium text-sm flex items-center gap-2 hover:bg-surface-container-high transition-colors">
                    <span class="material-symbols-outlined text-lg" data-icon="location_city">location_city</span>
                    <select id="city-selector" onchange="fetchCityAQI(this.value)" class="bg-transparent border-none text-sm font-bold text-primary focus:ring-0 cursor-pointer outline-none">
                        <optgroup label="Metros">
                            <option value="Delhi">Delhi</option>
                            <option value="Mumbai">Mumbai</option>
                            <option value="Chennai">Chennai</option>
                            <option value="Kolkata">Kolkata</option>
                            <option value="Bengaluru">Bengaluru</option>
                        </optgroup>
                        <optgroup label="River Cities">
                            <option value="Coimbatore">Coimbatore (Noyyal)</option>
                            <option value="Haridwar">Haridwar (Ganga)</option>
                            <option value="Guwahati">Guwahati (Brahmaputra)</option>
                            <option value="Nashik">Nashik (Godavari)</option>
                            <option value="Vijayawada">Vijayawada (Krishna)</option>
                            <option value="Jabalpur">Jabalpur (Narmada)</option>
                            <option value="Mysuru">Mysuru (Kaveri)</option>
                            <option value="Cuttack">Cuttack (Mahanadi)</option>
                            <option value="Surat">Surat (Tapi)</option>
                            <option value="Ludhiana">Ludhiana (Sutlej)</option>
                        </optgroup>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/10 shadow-sm relative min-h-[400px]">
            <div id="loading-indicator" class="absolute inset-0 flex flex-col items-center justify-center bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm z-10 hidden rounded-xl">
                <span class="material-symbols-outlined text-4xl text-primary animate-spin">sync</span>
                <p class="mt-4 font-headline font-bold tracking-widest text-primary uppercase text-sm">Fetching Data...</p>
            </div>
            
            <div class="flex justify-between items-start mb-8 border-b border-outline-variant/15 pb-4">
                <div>
                    <h3 class="font-headline text-xl font-bold text-on-surface" id="target-city-name">Delhi Air Quality</h3>
                    <p class="text-sm text-on-surface-variant">Real-time telemetry from Data.gov.in</p>
                </div>
                <div class="flex items-center gap-2 px-3 py-1 bg-secondary/10 rounded-full">
                    <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
                    <span class="text-[10px] font-bold text-secondary uppercase tracking-widest">LIVE API</span>
                </div>
            </div>

            <div id="pollutants-grid" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            </div>
        </div>
"""

new_script = """
    <script>
        async function fetchCityAQI(city) {
            const grid = document.getElementById("pollutants-grid");
            const loading = document.getElementById("loading-indicator");
            const title = document.getElementById("target-city-name");
            
            loading.classList.remove("hidden");
            title.innerText = `${city} Air Quality`;
            grid.innerHTML = "";

            try {
                const apiKey = "579b464db66ec23bdd0000018b72af4808f444b04705cb177217411e";
                const url = `https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69?api-key=${apiKey}&format=json&filters[city]=${city}&limit=50`;
                const res = await fetch(url);
                if (!res.ok) throw new Error("API Limit or Network");
                const data = await res.json();
                const records = data.records;
                
                if (records && records.length > 0) {
                    const uniquePollutants = {};
                    records.forEach(r => {
                        if(!uniquePollutants[r.pollutant_id]) {
                            uniquePollutants[r.pollutant_id] = r;
                        }
                    });
                    
                    Object.values(uniquePollutants).forEach(rec => {
                        const val = parseInt(rec.avg_value || rec.max_value || 0);
                        let statusColor = "primary";
                        let statusBg = "primary/10";
                        let statusText = "GOOD";

                        if(val > 100 && val <= 200) { statusColor = "secondary"; statusBg = "secondary/10"; statusText = "MODERATE"; }
                        else if(val > 200 && val <= 300) { statusColor = "tertiary"; statusBg = "tertiary/10"; statusText = "POOR"; }
                        else if(val > 300) { statusColor = "error"; statusBg = "error/10"; statusText = "SEVERE"; }

                        const cardHTML = `
                        <div class="bg-surface-container-low p-5 rounded-xl border border-outline-variant/10 shadow-sm hover:shadow-md transition-shadow">
                            <div class="flex justify-between items-start mb-4">
                                <span class="text-xs font-bold text-on-surface-variant uppercase tracking-widest">${rec.pollutant_id}</span>
                                <span class="text-[8px] px-2 py-0.5 bg-${statusBg} text-${statusColor} rounded-full font-black">${statusText}</span>
                            </div>
                            <div class="flex items-end gap-2 mb-2">
                                <p class="text-3xl font-black text-on-surface font-mono">${val}</p>
                                <span class="text-xs text-outline font-medium font-mono pb-1">µg/m³</span>
                            </div>
                            <div class="flex items-center gap-1.5 text-on-surface-variant/70">
                                <span class="material-symbols-outlined text-[14px]">sensors</span>
                                <p class="text-[10px] font-medium truncate" title="${rec.station}">${rec.station}</p>
                            </div>
                        </div>`;
                        grid.innerHTML += cardHTML;
                    });
                } else {
                    grid.innerHTML = `<div class="col-span-full rounded-xl bg-error/10 text-error p-6 text-center font-bold">No Data Available for ${city}</div>`;
                }
            } catch(e) {
                grid.innerHTML = `<div class="col-span-full rounded-xl bg-error/10 text-error p-6 text-center font-bold">Failed to Fetch Data</div>`;
                console.warn("City AQI Fetch Error:", e);
            }
            
            loading.classList.add("hidden");
        }

        fetchCityAQI("Delhi");
    </script>
"""

with open('air_quality.html', 'w', encoding='utf-8') as f:
    f.write(head_nav + new_main + bottom_nav.replace('</body>', new_script + '</body>'))
