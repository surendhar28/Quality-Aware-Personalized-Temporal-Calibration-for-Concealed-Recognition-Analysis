#!/usr/bin/env python3
"""
Extract grand average empirical fixation dynamics from raw Zenodo physical eye-tracking recordings.
Binned in 50 ms increments from 0 to 2000 ms post-stimulus onset across all 38 biological participants.
Saves empirical time-series to data/processed/fixation_dynamics_real.json.
"""

import os
import glob
import json
import time
import zipfile
import lxml.etree as ET
from collections import defaultdict
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

PROBES = {
    '1': ['rękawiczki', 'rekawiczki'],
    '2': ['klucz'],
    '3': ['asystent'],
    '4': ['outlook', 'poczta'],
    '5': ['egzamin'],
    '6': ['maska'],
    '7': ['torba']
}

def is_probe_item(cat, item_name):
    target_probes = PROBES.get(str(cat), [])
    item_lower = item_name.lower().strip()
    return any(p in item_lower for p in target_probes)

def process_file_dynamics(xlsx_path):
    fname = os.path.basename(xlsx_path)
    # Bins: 40 bins of 50ms from 0 to 2000ms
    # For each bin, count total trials present, probe fixations, irrel fixations
    # Accumulate fixation durations (or dwell fraction)
    n_bins = 40
    bin_probe_dwell = np.zeros(n_bins, dtype=np.float64)
    bin_irrel_dwell = np.zeros(n_bins, dtype=np.float64)
    bin_trial_counts = np.zeros(n_bins, dtype=np.int32)
    
    try:
        with zipfile.ZipFile(xlsx_path, 'r') as z:
            with z.open('xl/worksheets/sheet1.xml') as f:
                headers = []
                is_first = True
                stim_idx = -1
                ts_idx = -1
                mov_idx = -1
                dur_idx = -1
                grp_idx = -1
                group_val = "unknown"
                aoi_cols = {}
                trial_samples = defaultdict(list)
                
                for event, elem in ET.iterparse(f, tag='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
                    row = [''.join(c.itertext()) for c in elem]
                    elem.clear()
                    
                    if is_first:
                        headers = row
                        is_first = False
                        stim_idx = headers.index('Presented Stimulus name') if 'Presented Stimulus name' in headers else -1
                        ts_idx = headers.index('Recording timestamp') if 'Recording timestamp' in headers else 0
                        mov_idx = headers.index('Eye movement type') if 'Eye movement type' in headers else -1
                        dur_idx = headers.index('Gaze event duration') if 'Gaze event duration' in headers else -1
                        grp_idx = headers.index('group') if 'group' in headers else -1
                        
                        for cidx, h in enumerate(headers):
                            if h.startswith('AOI hit ['):
                                content = h.replace('AOI hit [', '').replace(']', '')
                                if ' - ' in content:
                                    stim_lbl, item = content.split(' - ')
                                    cat = stim_lbl.split('_')[0]
                                    aoi_cols[cidx] = (cat, stim_lbl, item)
                        continue
                        
                    if group_val == "unknown" and len(row) > grp_idx and grp_idx != -1:
                        group_val = row[grp_idx].lower().strip()
                        
                    stim = row[stim_idx] if len(row) > stim_idx else ""
                    if stim and '_' in stim:
                        parts = stim.split('_')
                        if len(parts) == 2 and parts[0] in ['1','2','3','4','5','6','7'] and parts[1] in ['1','2','3']:
                            ts = int(row[ts_idx]) if len(row) > ts_idx and row[ts_idx] else 0
                            mov = row[mov_idx] if len(row) > mov_idx else ""
                            dur = float(row[dur_idx]) if len(row) > dur_idx and row[dur_idx] else 0.0
                            
                            is_hit_probe = False
                            is_hit_irrel = False
                            for cidx, (cat, stim_lbl, item) in aoi_cols.items():
                                if stim_lbl == stim and len(row) > cidx and row[cidx] in ['1', 1]:
                                    if is_probe_item(cat, item):
                                        is_hit_probe = True
                                    else:
                                        is_hit_irrel = True
                                    break
                                    
                            trial_samples[stim].append((ts, mov, dur, is_hit_probe, is_hit_irrel))
                            
        # Aggregate across trials in this recording
        for stim_lbl, samples in trial_samples.items():
            if not samples:
                continue
            t0 = samples[0][0]
            # Track which bins are covered
            seen_bins = set()
            for ts, mov, dur, is_probe, is_irrel in samples:
                t_rel = (ts - t0) / 1000.0  # ms
                if 0 <= t_rel < 2000.0:
                    b = int(t_rel // 50)
                    if 0 <= b < n_bins:
                        seen_bins.add(b)
                        if mov == 'Fixation':
                            # Each sample at 120Hz represents ~8.33ms of fixation dwell
                            if is_probe:
                                bin_probe_dwell[b] += 8.33
                            elif is_irrel:
                                bin_irrel_dwell[b] += 8.33 / 3.0  # Normalized for 3 irrelevant distractors
                                
            for b in seen_bins:
                bin_trial_counts[b] += 1
                
        return {
            "fname": fname,
            "group": group_val,
            "probe_dwell": bin_probe_dwell.tolist(),
            "irrel_dwell": bin_irrel_dwell.tolist(),
            "trial_counts": bin_trial_counts.tolist(),
            "n_trials": len(trial_samples)
        }
    except Exception as e:
        print(f"Error processing {fname}: {e}")
        return None

def main():
    processed_dir = r"E:\karthianna\data\processed"
    xlsx_files = sorted(glob.glob(os.path.join(processed_dir, "CIT Recording*.xlsx")))
    print(f"Starting dynamics extraction across {len(xlsx_files)} physical recording files...")
    
    t0 = time.time()
    n_bins = 40
    time_bins_ms = [int(i * 50 + 25) for i in range(n_bins)]
    
    total_probe_dwell = np.zeros(n_bins, dtype=np.float64)
    total_irrel_dwell = np.zeros(n_bins, dtype=np.float64)
    total_trial_counts = np.zeros(n_bins, dtype=np.float64)
    
    # Store per-file data for error bars (SEM)
    file_probe_means = []
    file_irrel_means = []
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file_dynamics, f): f for f in xlsx_files}
        for future in as_completed(futures):
            res = future.result()
            if res and res.get("n_trials", 0) > 0:
                p_dwell = np.array(res["probe_dwell"])
                i_dwell = np.array(res["irrel_dwell"])
                counts = np.array(res["trial_counts"])
                
                valid_mask = counts > 0
                rates_p = np.zeros(n_bins)
                rates_i = np.zeros(n_bins)
                rates_p[valid_mask] = p_dwell[valid_mask] / counts[valid_mask]
                rates_i[valid_mask] = i_dwell[valid_mask] / counts[valid_mask]
                
                file_probe_means.append(rates_p)
                file_irrel_means.append(rates_i)
                
                total_probe_dwell += p_dwell
                total_irrel_dwell += i_dwell
                total_trial_counts += counts
                print(f"  Processed {res['fname']} ({res['group']}) with {res['n_trials']} trials.")
                
    # Grand average curves
    grand_probe_rate = total_probe_dwell / np.maximum(total_trial_counts, 1)
    grand_irrel_rate = total_irrel_dwell / np.maximum(total_trial_counts, 1)
    
    # Convert dwell rate (ms per 50ms bin) into average fixation duration equivalent (ms)
    # Average fixation duration in active fixating intervals:
    # Scale dwell rate to fixation duration profile:
    probe_arr = np.array(file_probe_means)
    irrel_arr = np.array(file_irrel_means)
    
    probe_sem = np.std(probe_arr, axis=0) / np.sqrt(len(file_probe_means))
    irrel_sem = np.std(irrel_arr, axis=0) / np.sqrt(len(file_irrel_means))
    
    output_data = {
        "metadata": {
            "source_dataset": "Zenodo DOI 10.5281/zenodo.18525952",
            "authors": "Celniak, Slapczynska, Jarszak, Augustyniak (2026)",
            "n_recordings": len(file_probe_means),
            "n_bins": n_bins,
            "bin_width_ms": 50,
            "timeline_ms": [0, 2000],
            "extracted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        },
        "time_ms": time_bins_ms,
        "grand_average": {
            "probe_mean_ms": [round(float(v), 2) for v in grand_probe_rate],
            "probe_sem_ms": [round(float(v), 2) for v in probe_sem],
            "irrel_mean_ms": [round(float(v), 2) for v in grand_irrel_rate],
            "irrel_sem_ms": [round(float(v), 2) for v in irrel_sem]
        }
    }
    
    out_json = r"E:\karthianna\data\processed\fixation_dynamics_real.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"\n[DONE] Saved empirical fixation dynamics to {out_json} in {time.time()-t0:.1f}s.")

if __name__ == "__main__":
    main()
