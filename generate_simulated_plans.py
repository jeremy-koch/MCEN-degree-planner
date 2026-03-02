import os
import json
import random
import hashlib
from datetime import datetime, timedelta

# Recreate the exact catalog from your web app
CATALOG = { 
    "APPM 1350": 4, "MCEN 1030": 4, "PHYS 1110": 4, "GEEN 1400": 3, 
    "COEN 1500": 1, "APPM 1360": 4, "MCEN 1024": 3, "MCEN 1025": 4, 
    "PHYS 1120": 4, "PHYS 1140": 1, "APPM 2350": 4, "MCEN 2000": 1, 
    "MCEN 2023": 3, "MCEN 2024": 3, "APPM 2360": 4, "MCEN 2043": 3, 
    "MCEN 2063": 3, "MCEN 3012": 3, "MCEN 3017": 3, "MCEN 3021": 3, 
    "MCEN 3025": 3, "MCEN 3030": 3, "MCEN 3022": 3, "MCEN 4026": 3, 
    "MCEN 4043": 3, "MCEN 3032": 3, "MCEN 3047": 4, "MCEN 4045": 3, 
    "MCEN 4085": 3
}

YEAR_LIST = ["First Year", "Sophomore Year", "Junior Year", "Senior Year"]

def generate_simulated_plans(count=1000):
    output_dir = "raw_jsons"
    os.makedirs(output_dir, exist_ok=True)
    
    courses = list(CATALOG.keys())
    
    for i in range(count):
        # 1. Determine Start Term & Base Year
        # Base years 2020 through 2025 (which covers up to Spring 2026 starts)
        base_year = random.randint(2020, 2025)
        
        # 5% chance of starting in Spring
        is_spring_start = random.random() < 0.05 
        
        # 2. Setup Student Metadata
        raw_id = f"student_{10000 + i}"
        student_hash = hashlib.sha256(raw_id.encode()).hexdigest()
        
        # Randomize timestamp slightly over the last 30 days
        random_days_ago = random.randint(0, 30)
        timestamp = (datetime.now() - timedelta(days=random_days_ago)).isoformat()
        
        # 3. Build the Planner
        planner = {"transfer": []}
        sems = ["transfer"]
        
        # Shuffle courses so everyone takes them in slightly different orders
        random.shuffle(courses)
        course_queue = courses.copy()
        
        for year in YEAR_LIST:
            clean_year = year.replace(" ", "")
            for term in ["Fall", "Spring", "Summer"]:
                sid = f"{clean_year}-{term}"
                sems.append(sid)
                planner[sid] = []
                
                # Logic to assign courses to terms
                if term == "Summer":
                    # Only a 10% chance a student takes 1 summer class
                    if random.random() < 0.10 and course_queue:
                        c_code = course_queue.pop(0)
                        planner[sid].append({"code": c_code, "credits": CATALOG[c_code]})
                    continue
                
                # If they are a Spring start, skip their very first Fall
                if is_spring_start and sid == "FirstYear-Fall":
                    continue
                
                # Assign 3 to 5 courses per Fall/Spring semester
                num_courses = random.randint(3, 5)
                for _ in range(num_courses):
                    if course_queue:
                        c_code = course_queue.pop(0)
                        planner[sid].append({"code": c_code, "credits": CATALOG[c_code]})

        # 4. Compile JSON payload
        data = {
            "student_hash": student_hash,
            "timestamp": timestamp,
            "base_year": base_year,
            "planner": planner,
            "sems": sems,
            "notes": {},
            "year_list": YEAR_LIST
        }
        
        # 5. Write to file
        filepath = os.path.join(output_dir, f"simulated_{raw_id}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
            
    print(f"Successfully generated {count} simulated student plans in '{output_dir}/'!")

if __name__ == "__main__":
    generate_simulated_plans(1000)