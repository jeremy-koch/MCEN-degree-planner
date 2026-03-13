<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ME Planner | Full Templates</title>
    <style>
        :root {
            --cu-gold: #CFB87C;
            --cu-black: #000000;
            --light-gray: #f4f4f4;
            --border-color: #ddd;
            --summer-blue: #f0faff;
            --error-red: #dc3545;
            --error-bg: #f8d7da;
        }
        body { font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; background: var(--light-gray); }
        
        #sidebar { width: 320px; background: white; border-right: 2px solid var(--border-color); display: flex; flex-direction: column; }
        .sidebar-header { background: var(--cu-black); color: var(--cu-gold); padding: 20px; text-align: center; }
        .catalog-container { padding: 15px; overflow-y: auto; flex-grow: 1; }
        
        .course-pill {
            background: var(--light-gray); border: 1px solid var(--border-color);
            padding: 8px 10px; margin-bottom: 8px; border-radius: 4px; cursor: grab;
            display: flex; justify-content: space-between; align-items: center; font-size: 0.9em;
        }
        .credits-badge { background: var(--cu-gold); color: var(--cu-black); padding: 2px 6px; border-radius: 12px; font-size: 0.8em; font-weight: bold; }

        #main-content { flex-grow: 1; display: flex; flex-direction: column; overflow-y: auto; }
        .controls { 
            background: white; padding: 15px 30px; display: flex; gap: 12px; align-items: center; 
            border-bottom: 2px solid var(--border-color); position: sticky; top: 0; z-index: 10; 
        }
        
        #studentID { padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; width: 120px; }
        #planTemplate { padding: 8px; border: 1px solid var(--border-color); border-radius: 4px; }

        button.action-btn { background: #eee; border: 1px solid #ccc; padding: 8px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; }
        button.add-year-btn { background: #28a745; color: white; border: none; }
        button.clear-btn { background: #fff1f1; color: #721c24; border: 1px solid #f5c6cb; }

        .planner-grid { padding: 20px; }
        .year-row { background: white; margin-bottom: 25px; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .year-title { margin-top: 0; border-bottom: 2px solid var(--cu-gold); padding-bottom: 5px; display: flex; justify-content: space-between; align-items: center; }
        .semesters { display: flex; gap: 10px; margin-top: 15px; }
        
        .semester-box { flex: 1; background: var(--light-gray); border: 2px dashed var(--border-color); border-radius: 6px; min-height: 160px; padding: 10px; }
        .semester-header { display: flex; justify-content: space-between; font-size: 0.75em; font-weight: bold; color: #777; margin-bottom: 10px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }
        .sem-credits.overload { color: var(--error-red); font-weight: 900; }

        .dropped-course { background: white; border: 1px solid #ccc; padding: 10px; margin-bottom: 8px; border-radius: 4px; cursor: grab; font-size: 0.85em; }
        .dropped-course.prereq-error { background: var(--error-bg) !important; border-color: var(--error-red) !important; }
        .error-label { display: none; color: #721c24; font-size: 0.75em; font-weight: bold; margin-top: 5px; }
        .prereq-error .error-label { display: block; }
        .remove-btn { color: red; cursor: pointer; border: none; background: none; }
    </style>
</head>
<body>

    <div id="sidebar">
        <div class="sidebar-header"><h2>ME Catalog</h2></div>
        <div class="catalog-container" id="catalog"></div>
    </div>

    <div id="main-content">
        <div class="controls">
            <input type="text" id="studentID" placeholder="Student ID">
            <select id="planTemplate">
                <option value="">-- Select Template --</option>
                <option value="blue_plan">Blue Plan (Standard)</option>
                <option value="green_plan">Green Plan (Alt)</option>
            </select>
            <button class="action-btn" onclick="applyTemplate()">Apply</button>
            <button class="action-btn add-year-btn" onclick="addYear()">+ Year</button>
            <button class="action-btn" onclick="duplicatePlan()">Duplicate</button>
            <button class="action-btn clear-btn" style="margin-left:auto" onclick="clearPlan()">Clear</button>
        </div>

        <div class="planner-grid" id="planner">
            <div class="year-row" style="background: #f0f7ff;">
                <h3 class="year-title">Transfer / AP Credits</h3>
                <div class="semesters">
                    <div class="semester-box" data-sid="transfer" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                        <div class="semester-header"><span>Prior</span><span class="sem-credits" id="cr-transfer">0 cr</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const CATALOG = { 
            "APPM 1350": 4, "MCEN 1030": 4, "PHYS 1110": 4, "GEEN 1400": 3, "COEN 1500": 1, 
            "APPM 1360": 4, "MCEN 1024": 3, "MCEN 1025": 4, "PHYS 1120": 4, "PHYS 1140": 1, 
            "APPM 2350": 4, "MCEN 2000": 1, "MCEN 2023": 3, "MCEN 2024": 3, "APPM 2360": 4, 
            "MCEN 2043": 3, "MCEN 2063": 3, "MCEN 3012": 3, "MCEN 3021": 3, "MCEN 3025": 3, 
            "MCEN 3030": 3, "MCEN 3022": 3, "MCEN 4026": 3, "MCEN 4043": 3, "MCEN 3032": 3, 
            "MCEN 3047": 4, "MCEN 4045": 3, "MCEN 4085": 3, "ECEN 3010": 3,
            "H&SS Lower": 3, "H&SS Upper": 3, "Free Elective": 3, "Writing": 3, 
            "Gen Tech": 3, "ME Tech": 3
        };

        const PREREQS = {
            "APPM 1360": ["APPM 1350"], "PHYS 1120": ["PHYS 1110"], "APPM 2350": ["APPM 1360"],
            "APPM 2360": ["APPM 1360"], "MCEN 2023": ["APPM 1360", "PHYS 1110"], "MCEN 2063": ["MCEN 2023"],
            "MCEN 3021": ["MCEN 2023", "APPM 2350"], "MCEN 3022": ["MCEN 3021"], "MCEN 4045": ["MCEN 3022", "MCEN 3030"],
            "MCEN 4085": ["MCEN 4045"]
        };

        const TEMPLATES = {
            "blue_plan": {
                "Year1-Fall": ["GEEN 1400", "MCEN 1030", "APPM 1350", "PHYS 1110"],
                "Year1-Spring": ["MCEN 1025", "MCEN 1024", "APPM 1360", "PHYS 1120", "PHYS 1140"],
                "Year2-Fall": ["H&SS Lower", "MCEN 2000", "MCEN 2024", "APPM 2350", "MCEN 2023"],
                "Year2-Spring": ["H&SS Lower", "Free Elective", "MCEN 3012", "APPM 2360", "MCEN 2063", "MCEN 2043"],
                "Year3-Fall": ["MCEN 3012", "MCEN 3021", "MCEN 3030", "H&SS Lower", "Gen Tech"],
                "Year3-Spring": ["MCEN 3022", "MCEN 3032", "ECEN 3010", "Writing", "ME Tech"],
                "Year4-Fall": ["MCEN 4026", "MCEN 4043", "MCEN 4045", "ME Tech", "H&SS Upper"],
                "Year4-Spring": ["MCEN 4085", "MCEN 3047", "ME Tech", "H&SS Upper", "Free Elective"]
            },
            "green_plan": {
                "Year1-Fall": ["H&SS Lower", "GEEN 1400", "MCEN 1024", "APPM 1350"],
                "Year1-Spring": ["H&SS Lower", "PHYS 1110", "APPM 1360", "MCEN 1030"],
                "Year2-Fall": ["PHYS 1120", "PHYS 1140", "APPM 2350", "MCEN 1025", "MCEN 2023"],
                "Year2-Spring": ["APPM 2360", "MCEN 2024", "MCEN 2063", "MCEN 2000", "H&SS Lower"],
                "Year3-Fall": ["MCEN 3012", "MCEN 3021", "MCEN 2043", "Writing", "H&SS Lower"],
                "Year3-Spring": ["MCEN 3022", "MCEN 3030", "MCEN 3032", "ECEN 3010", "ME Tech"],
                "Year4-Fall": ["MCEN 4026", "MCEN 4043", "MCEN 4045", "Gen Tech", "H&SS Upper"],
                "Year4-Spring": ["MCEN 4085", "MCEN 3047", "ME Tech", "ME Tech", "H&SS Upper"]
            }
        };

        let yearCount = 0;
        let SEM_ORDER = ["transfer"];

        function init() {
            renderCatalog();
            const urlParams = new URLSearchParams(window.location.search);
            const savedPlan = urlParams.get('plan');
            if (savedPlan) {
                const data = JSON.parse(decodeURIComponent(savedPlan));
                const numYears = Math.max(...Object.keys(data).map(k => parseInt(k.match(/\d+/)?.[0] || 0)), 4);
                while(yearCount < numYears) addYear();
                Object.entries(data).forEach(([sid, courses]) => {
                    const box = document.querySelector(`[data-sid="${sid}"]`);
                    if (box) courses.forEach(c => createCourseDOM(c, box));
                });
            } else {
                for(let i=0; i<4; i++) addYear();
            }
            validateAll();
        }

        function addYear() {
            yearCount++;
            const labels = ["First Year", "Sophomore Year", "Junior Year", "Senior Year", "Fifth Year", "Sixth Year"];
            const titleText = labels[yearCount-1] || `Year ${yearCount}`;
            const cleanY = `Year${yearCount}`;
            const row = document.createElement('div');
            row.className = 'year-row';
            row.id = `row-${cleanY}`;
            let semsHtml = '';
            ["Fall", "Spring", "Summer"].forEach(t => {
                const sid = `${cleanY}-${t}`;
                if (!SEM_ORDER.includes(sid)) SEM_ORDER.push(sid);
                semsHtml += `
                    <div class="semester-box" data-sid="${sid}" ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                        <div class="semester-header"><span>${t}</span><span class="sem-credits" id="cr-${sid}">0 cr</span></div>
                    </div>`;
            });
            row.innerHTML = `<h3 class="year-title"><span>${titleText}</span> ${yearCount > 4 ? `<button class="remove-btn" onclick="removeYear('${cleanY}')">Remove</button>` : ''}</h3><div class="semesters">${semsHtml}</div>`;
            document.getElementById('planner').appendChild(row);
        }

        function applyTemplate() {
            const key = document.getElementById('planTemplate').value;
            if (!key) return;
            if (!confirm("This will clear your current plan and apply the 4-year template. Proceed?")) return;
            
            document.querySelectorAll('.dropped-course').forEach(c => c.remove());
            // Ensure 4 years exist
            while(yearCount < 4) addYear();

            Object.entries(TEMPLATES[key]).forEach(([sid, courses]) => {
                const box = document.querySelector(`[data-sid="${sid}"]`);
                if (box) courses.forEach(c => createCourseDOM(c, box));
            });
            validateAll();
        }

        function validateAll() {
            const courseMap = {};
            document.querySelectorAll('.semester-box').forEach(box => {
                const sid = box.dataset.sid;
                const courses = Array.from(box.querySelectorAll('.dropped-course')).map(c => c.dataset.code);
                courseMap[sid] = courses;
                let semTotal = courses.reduce((sum, code) => sum + (CATALOG[code] || 0), 0);
                const counter = document.getElementById(`cr-${sid}`);
                if(counter) { counter.innerText = `${semTotal} cr`; counter.classList.toggle('overload', semTotal > 18); }
            });

            document.querySelectorAll('.dropped-course').forEach(pill => {
                const code = pill.dataset.code;
                const sid = pill.closest('.semester-box').dataset.sid;
                const myIndex = SEM_ORDER.indexOf(sid);
                const missingPre = (PREREQS[code] || []).filter(req => {
                    for (let i = 0; i < myIndex; i++) if (courseMap[SEM_ORDER[i]]?.includes(req)) return false;
                    return true;
                });
                pill.classList.toggle('prereq-error', missingPre.length > 0);
                pill.querySelector('.error-label').innerText = missingPre.length ? "⚠ Pre: " + missingPre.join(', ') : "";
            });
        }

        function createCourseDOM(code, box) {
            const div = document.createElement('div');
            div.className = 'dropped-course';
            div.id = 'c-' + Math.random().toString(36).substr(2, 9);
            div.draggable = true;
            div.dataset.code = code;
            div.ondragstart = (e) => e.dataTransfer.setData("application/json", JSON.stringify({elId: div.id, source: 'sem'}));
            div.innerHTML = `<div style="display:flex; justify-content:space-between"><strong>${code}</strong><button class="remove-btn" onclick="this.closest('.dropped-course').remove(); validateAll();">&times;</button></div><div class="error-label"></div>`;
            box.appendChild(div);
        }

        function handleDrop(ev) {
            ev.preventDefault();
            const data = JSON.parse(ev.dataTransfer.getData("application/json"));
            if (data.source === 'catalog') createCourseDOM(data.code, ev.currentTarget);
            else ev.currentTarget.appendChild(document.getElementById(data.elId));
            validateAll();
        }

        function renderCatalog() {
            const cat = document.getElementById('catalog');
            Object.keys(CATALOG).sort().forEach(code => {
                const div = document.createElement('div');
                div.className = 'course-pill';
                div.draggable = true;
                div.dataset.code = code;
                div.ondragstart = (e) => e.dataTransfer.setData("application/json", JSON.stringify({code, source: 'catalog'}));
                div.innerHTML = `<span>${code}</span> <span class="credits-badge">${CATALOG[code]} cr</span>`;
                cat.appendChild(div);
            });
        }

        function duplicatePlan() {
            const plan = {};
            document.querySelectorAll('.semester-box').forEach(box => {
                const courses = Array.from(box.querySelectorAll('.dropped-course')).map(c => c.dataset.code);
                if (courses.length) plan[box.dataset.sid] = courses;
            });
            window.open(`${window.location.origin}${window.location.pathname}?plan=${encodeURIComponent(JSON.stringify(plan))}`, '_blank');
        }

        function clearPlan() { if(confirm("Clear all?")) { document.querySelectorAll('.dropped-course').forEach(c => c.remove()); validateAll(); }}
        function handleDragOver(e) { e.preventDefault(); e.currentTarget.classList.add('drag-over'); }
        function handleDragLeave(e) { e.currentTarget.classList.remove('drag-over'); }
        function removeYear(id) { document.getElementById(`row-${id}`).remove(); SEM_ORDER = SEM_ORDER.filter(s => !s.startsWith(id)); validateAll(); }

        init();
    </script>
</body>
</html>