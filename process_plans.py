import os
import json
import csv
from collections import defaultdict
from datetime import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- Configuration ---
INPUT_DIR = "raw_jsons"
OUTPUT_DIR = "output"
HISTORICAL_CSV = "historical.csv"  # Place this next to the script
CSV_FILE = os.path.join(OUTPUT_DIR, "combined_enrollment.csv")
PLOT_FILE = os.path.join(OUTPUT_DIR, "enrollment_heatmap.png")

def get_actual_term(base_year, year_idx, term_name):
    """Translates relative blocks into actual academic terms."""
    y = base_year + year_idx
    if term_name in ["Spring", "Summer"]:
        y += 1
    return f"{term_name} {y}"

def term_sort_key(term_str):
    """Helper to sort terms chronologically (e.g., 'Spring 2024' -> (2024, 0))"""
    try:
        term, year = term_str.split(" ")
        order = {"Spring": 0, "Summer": 1, "Fall": 2}
        return (int(year), order.get(term, 3))
    except ValueError:
        return (9999, 99) # Fallback for unexpected column names

def process_enrollment():
    latest_files = {}
    
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Process JSON Predictions
    files_found = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    tally = defaultdict(lambda: defaultdict(int))
    
    if files_found:
        for filename in files_found:
            filepath = os.path.join(INPUT_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                student_hash = data.get("student_hash", f"anonymous_{filename}")
                timestamp_str = data.get("timestamp", "2000-01-01T00:00:00")
                file_time = datetime.fromisoformat(timestamp_str)
                
                if student_hash not in latest_files or file_time > latest_files[student_hash]['time']:
                    latest_files[student_hash] = {'path': filepath, 'time': file_time}
            except Exception as e:
                print(f"Error reading {filename}: {e}")

        for student_hash, file_info in latest_files.items():
            try:
                with open(file_info['path'], 'r') as f:
                    data = json.load(f)
                    
                planner, year_list, base_year = data.get("planner", {}), data.get("year_list", []), data.get("base_year", 2024)
                
                for year_idx, year_name in enumerate(year_list):
                    clean_year = year_name.replace(" ", "")
                    for term_name in ["Fall", "Spring", "Summer"]:
                        sid = f"{clean_year}-{term_name}"
                        if sid in planner:
                            actual_term = get_actual_term(base_year, year_idx, term_name)
                            for course in planner[sid]:
                                tally[actual_term][course["code"]] += 1
            except Exception as e:
                print(f"Error processing {file_info['path']}: {e}")
        print(f"Processed {len(latest_files)} predicted student plans.")

    # Convert predicted dict to DataFrame
    df_pred = pd.DataFrame.from_dict(tally, orient='columns').fillna(0)
    df_pred.index.name = "Course"
    
    # 2. Process Historical Data
    df_hist = pd.DataFrame()
    if os.path.exists(HISTORICAL_CSV):
        try:
            df_hist = pd.read_csv(HISTORICAL_CSV)
            df_hist.set_index("Course", inplace=True)
            print(f"Loaded historical data from {HISTORICAL_CSV}")
        except Exception as e:
            print(f"Error reading historical CSV: {e}")

    # 3. Merge and Sort
    # Combine historical and predicted. If a column exists in both, predicted takes precedence (or you can adjust logic here)
    if not df_hist.empty and not df_pred.empty:
        # Combine columns, preferring predictions if they overlap
        df_combined = df_pred.combine_first(df_hist).fillna(0)
        num_hist_cols = len([c for c in df_hist.columns if c not in df_pred.columns])
    elif not df_hist.empty:
        df_combined = df_hist.fillna(0)
        num_hist_cols = len(df_hist.columns)
    elif not df_pred.empty:
        df_combined = df_pred.fillna(0)
        num_hist_cols = 0
    else:
        print("No data available to process.")
        return

    # Sort columns chronologically
    sorted_cols = sorted(df_combined.columns, key=term_sort_key)
    df_combined = df_combined[sorted_cols]
    
    # Sort index (Course codes) alphabetically
    df_combined.sort_index(inplace=True)

    # 4. Write combined data to CSV
    df_combined.to_csv(CSV_FILE)
    print(f"Combined enrollment CSV saved to: {CSV_FILE}")

    # 5. Generate Heatmap
    plt.figure(figsize=(max(12, len(sorted_cols) * 0.8), max(8, len(df_combined) * 0.4)))
    
    # Draw the heatmap
    ax = sns.heatmap(df_combined, annot=True, cmap="YlOrRd", fmt="g", linewidths=.5, cbar_kws={'label': 'Student Count'})
    
    # Add a visual divider if we have both historical and predicted data
    if not df_hist.empty and not df_pred.empty:
        # Find where historical ends and predictions begin
        hist_cols_in_order = [c for c in sorted_cols if c in df_hist.columns and c not in df_pred.columns]
        if hist_cols_in_order:
            divider_idx = sorted_cols.index(hist_cols_in_order[-1]) + 1
            ax.axvline(x=divider_idx, color='blue', linewidth=3, linestyle='--')
            # Add text annotation
            plt.text(divider_idx, -0.5, 'PREDICTED ->', color='blue', va='bottom', ha='left', fontweight='bold')
            plt.text(divider_idx, -0.5, '<- ACTUAL', color='blue', va='bottom', ha='right', fontweight='bold')

    plt.title("Actual vs. Predicted Course Enrollment", fontsize=18, pad=30)
    plt.xlabel("Semester", fontsize=14)
    plt.ylabel("Course", fontsize=14)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    plt.savefig(PLOT_FILE, dpi=300)
    plt.close()
    print(f"Enrollment Heatmap saved to: {PLOT_FILE}")

if __name__ == "__main__":
    process_enrollment()