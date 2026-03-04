import os
import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import re

# --- Configuration ---
INPUT_DIR = "raw_jsons"
OUTPUT_DIR = "output"
HISTORICAL_CSV = "historical.csv"
CSV_FILE = os.path.join(OUTPUT_DIR, "combined_enrollment.csv")
PLOT_FILE = os.path.join(OUTPUT_DIR, "enrollment_heatmap.png")

def get_actual_term(base_year, year_idx, term_name):
    y = base_year + year_idx
    if term_name in ["Spring", "Summer"]: 
        y += 1
    return f"{term_name} {y}"

def term_sort_key(term_str):
    try:
        parts = term_str.split(" ")
        term, year = parts[0], parts[1]
        order = {"Spring": 0, "Summer": 1, "Fall": 2}
        return (int(year), order.get(term, 3))
    except: 
        return (9999, 99)

def clean_key(course_code):
    return re.sub(r'\s+', '', str(course_code)).upper()

def format_display_name(key):
    match = re.match(r"([A-Z]+)([0-9]+)", key)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return key

def course_sort_priority(course_key):
    """Sorts MCEN courses to the top, then everything else alphabetically."""
    is_mcen = course_key.startswith("MCEN")
    # Priority 0 for MCEN, 1 for others. Then sorted alphabetically.
    return (0 if is_mcen else 1, course_key)

def process_enrollment():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. LOAD PREDICTIONS
    latest_files = {}
    files_found = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    pred_data = defaultdict(lambda: defaultdict(int))
    pred_cols = set()
    
    for filename in files_found:
        filepath = os.path.join(INPUT_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            sid = data.get("student_hash", filename)
            ts = datetime.fromisoformat(data.get("timestamp", "2000-01-01T00:00:00"))
            if sid not in latest_files or ts > latest_files[sid]['ts']:
                latest_files[sid] = {'data': data, 'ts': ts}
        except: continue

    for sid, info in latest_files.items():
        d = info['data']
        planner, year_list, base_year = d.get("planner", {}), d.get("year_list", []), d.get("base_year", 2024)
        for y_idx, y_name in enumerate(year_list):
            for t_name in ["Fall", "Spring", "Summer"]:
                key = f"{y_name.replace(' ', '')}-{t_name}"
                if key in planner:
                    actual_term = get_actual_term(base_year, y_idx, t_name)
                    pred_cols.add(actual_term)
                    for course in planner[key]:
                        c_code = clean_key(course["code"])
                        pred_data[c_code][actual_term] += 1

    # 2. LOAD HISTORICAL
    hist_data = defaultdict(lambda: defaultdict(int))
    hist_cols = set()
    if os.path.exists(HISTORICAL_CSV):
        try:
            df_h_raw = pd.read_csv(HISTORICAL_CSV)
            course_col = df_h_raw.columns[0]
            hist_cols = set(df_h_raw.columns[1:])
            for _, row in df_h_raw.iterrows():
                c_code = clean_key(row[course_col])
                for term in hist_cols:
                    val = row[term]
                    try:
                        hist_data[c_code][term] += int(float(val)) if pd.notnull(val) else 0
                    except: continue
        except Exception as e:
            print(f"Historical CSV Error: {e}")

    # 3. CONSOLIDATE MASTER LISTS WITH CUSTOM SORT
    # Here is the magic: Sorting based on the priority function
    unique_clean_keys = sorted(list(set(list(pred_data.keys()) + list(hist_data.keys()))), key=course_sort_priority)
    all_terms = sorted(list(set(list(pred_cols) + list(hist_cols))), key=term_sort_key)

    # 4. BUILD DATASETS
    display_names = [format_display_name(k) for k in unique_clean_keys]
    annot_rows = []
    color_rows = []

    for c_key in unique_clean_keys:
        a_row = []
        c_row = []
        for term in all_terms:
            p = pred_data[c_key][term]
            h = hist_data[c_key][term]
            in_pred = term in pred_cols
            in_hist = term in hist_cols

            if in_pred and in_hist:
                a_row.append(f"{p} ({h})")
                c_row.append(max(p, h))
            elif in_pred:
                a_row.append(f"{p}")
                c_row.append(p)
            elif in_hist:
                a_row.append(f"({h})")
                c_row.append(h)
            else:
                a_row.append("")
                c_row.append(0)
                
        annot_rows.append(a_row)
        color_rows.append(c_row)

    df_final_annot = pd.DataFrame(annot_rows, index=display_names, columns=all_terms)
    df_final_color = pd.DataFrame(color_rows, index=display_names, columns=all_terms)

    # 5. EXPORT AND PLOT
    df_final_annot.to_csv(CSV_FILE)
    
    plt.figure(figsize=(max(14, len(all_terms)*1.2), max(8, len(display_names)*0.5)))
    ax = sns.heatmap(df_final_color, annot=df_final_annot.values, fmt="", cmap="YlOrRd", 
                     linewidths=.5, cbar_kws={'label': 'Student Count'})
    
    if hist_cols and pred_cols:
        last_hist_only = ""
        for t in all_terms:
            if t in hist_cols and t not in (pred_cols - hist_cols):
                last_hist_only = t
        if last_hist_only:
            divider_idx = all_terms.index(last_hist_only) + 1
            ax.axvline(x=divider_idx, color='blue', linewidth=3, linestyle='--')
            plt.text(divider_idx, -0.2, 'PREDICTED ->', color='blue', va='bottom', ha='left', fontweight='bold')
            plt.text(divider_idx, -0.2, '<- ACTUAL', color='blue', va='bottom', ha='right', fontweight='bold')

    plt.title("Actual vs. Predicted Enrollment: MCEN Prioritized\nFormat: Predicted (Actual)", fontsize=18, pad=25)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(PLOT_FILE, dpi=300)
    plt.close()
    
    print(f"Success! {len(display_names)} courses processed. MCEN core courses are at the top.")

if __name__ == "__main__":
    process_enrollment()