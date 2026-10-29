import os
import glob
import sys
import zipfile
import lxml.etree as ET
from collections import defaultdict
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

sys.stdout.reconfigure(encoding='utf-8')

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

def process_single_recording(xlsx_path):
    fname = os.path.basename(xlsx_path)
    trials_records = []
    
    try:
        with zipfile.ZipFile(xlsx_path, 'r') as z:
            with z.open('xl/worksheets/sheet1.xml') as f:
                headers = []
                is_first = True
                
                # Metadata
                participant_name = ""
                group_val = ""
                gender_val = ""
                calib_acc_deg = None
                
                # Column indices
                stim_idx = -1
                ts_idx = -1
                mov_idx = -1
                dur_idx = -1
                vl_idx = -1
                vr_idx = -1
                gx_idx = -1
                gy_idx = -1
                part_idx = -1
                grp_idx = -1
                gen_idx = -1
                cal_idx = -1
                
                # AOI map: col_idx -> (category, stimulus_label, item_name)
                aoi_cols = {}
                
                # Trial data buffers: stim_label -> list of sample dicts
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
                        vl_idx = headers.index('Validity left') if 'Validity left' in headers else -1
                        vr_idx = headers.index('Validity right') if 'Validity right' in headers else -1
                        gx_idx = headers.index('Gaze point X') if 'Gaze point X' in headers else -1
                        gy_idx = headers.index('Gaze point Y') if 'Gaze point Y' in headers else -1
                        part_idx = headers.index('Participant name') if 'Participant name' in headers else -1
                        grp_idx = headers.index('group') if 'group' in headers else -1
                        gen_idx = headers.index('gender') if 'gender' in headers else -1
                        cal_idx = headers.index('Average calibration accuracy (degrees)') if 'Average calibration accuracy (degrees)' in headers else -1
                        
                        for cidx, h in enumerate(headers):
                            if h.startswith('AOI hit ['):
                                # Format: AOI hit [cat_rep - item]
                                content = h.replace('AOI hit [', '').replace(']', '')
                                if ' - ' in content:
                                    stim_lbl, item = content.split(' - ')
                                    cat = stim_lbl.split('_')[0]
                                    aoi_cols[cidx] = (cat, stim_lbl, item)
                        continue
                        
                    if not participant_name and len(row) > part_idx:
                        participant_name = row[part_idx]
                        group_val = row[grp_idx] if len(row) > grp_idx else "unknown"
                        gender_val = row[gen_idx] if len(row) > gen_idx else "unknown"
                        if len(row) > cal_idx and row[cal_idx]:
                            try:
                                calib_acc_deg = float(row[cal_idx])
                            except ValueError:
                                calib_acc_deg = None
                                
                    stim = row[stim_idx] if len(row) > stim_idx else ""
                    # Check if this row belongs to one of the 21 test stimuli: 1_1 to 7_3
                    if stim and '_' in stim:
                        parts = stim.split('_')
                        if len(parts) == 2 and parts[0] in ['1','2','3','4','5','6','7'] and parts[1] in ['1','2','3']:
                            ts = int(row[ts_idx]) if len(row) > ts_idx and row[ts_idx] else 0
                            mov = row[mov_idx] if len(row) > mov_idx else ""
                            dur = float(row[dur_idx]) if len(row) > dur_idx and row[dur_idx] else 0.0
                            vl = row[vl_idx] if len(row) > vl_idx else ""
                            vr = row[vr_idx] if len(row) > vr_idx else ""
                            gx = float(row[gx_idx]) if len(row) > gx_idx and row[gx_idx] else np.nan
                            gy = float(row[gy_idx]) if len(row) > gy_idx and row[gy_idx] else np.nan
                            
                            # Check AOI hit for this stimulus
                            hit_item = None
                            is_hit_probe = False
                            for cidx, (cat, stim_lbl, item) in aoi_cols.items():
                                if stim_lbl == stim and len(row) > cidx and row[cidx] in ['1', 1]:
                                    hit_item = item
                                    is_hit_probe = is_probe_item(cat, item)
                                    break
                                    
                            trial_samples[stim].append({
                                'timestamp': ts,
                                'movement': mov,
                                'duration': dur,
                                'valid': (vl == "Valid" or vr == "Valid"),
                                'eyes_not_found': (mov == "EyesNotFound"),
                                'gaze_x': gx,
                                'gaze_y': gy,
                                'hit_item': hit_item,
                                'is_probe': is_hit_probe
                            })
                            
        # Now process each of the 21 test trials
        for stim_label, samples in trial_samples.items():
            if not samples:
                continue
                
            cat = stim_label.split('_')[0]
            rep = stim_label.split('_')[1]
            t0 = samples[0]['timestamp']
            total_samples = len(samples)
            
            # Quality metrics
            valid_samples = sum(1 for s in samples if s['valid'])
            missing_samples = sum(1 for s in samples if s['eyes_not_found'])
            valid_ratio = valid_samples / total_samples if total_samples > 0 else 0.0
            missing_ratio = missing_samples / total_samples if total_samples > 0 else 1.0
            
            # Windows
            # Window 1: 0-500ms
            early_samples = [s for s in samples if 0 <= (s['timestamp'] - t0) / 1000.0 <= 500.0]
            early_count = len(early_samples)
            
            # Window 2: 500-1000ms
            mid_samples = [s for s in samples if 500.0 < (s['timestamp'] - t0) / 1000.0 <= 1000.0]
            
            # Window 3: 1000-2000ms
            late_samples = [s for s in samples if 1000.0 < (s['timestamp'] - t0) / 1000.0 <= 2000.0]
            
            # Fixation duration on probe vs irrelevants in early window
            early_fix_probe_dur = sum(8.33 for s in early_samples if s['movement'] == 'Fixation' and s['is_probe'])
            early_fix_irrel_dur = sum(8.33 for s in early_samples if s['movement'] == 'Fixation' and s['hit_item'] and not s['is_probe']) / 3.0
            early_probe_diff = early_fix_probe_dur - early_fix_irrel_dur
            
            # Mid window
            mid_fix_probe_dur = sum(8.33 for s in mid_samples if s['movement'] == 'Fixation' and s['is_probe'])
            mid_fix_irrel_dur = sum(8.33 for s in mid_samples if s['movement'] == 'Fixation' and s['hit_item'] and not s['is_probe']) / 3.0
            mid_probe_diff = mid_fix_probe_dur - mid_fix_irrel_dur
            
            # Late window
            late_fix_probe_dur = sum(8.33 for s in late_samples if s['movement'] == 'Fixation' and s['is_probe'])
            late_fix_irrel_dur = sum(8.33 for s in late_samples if s['movement'] == 'Fixation' and s['hit_item'] and not s['is_probe']) / 3.0
            late_probe_diff = late_fix_probe_dur - late_fix_irrel_dur
            
            # Overall trial
            total_fix_probe_dur = sum(8.33 for s in samples if s['movement'] == 'Fixation' and s['is_probe'])
            total_fix_irrel_dur = sum(8.33 for s in samples if s['movement'] == 'Fixation' and s['hit_item'] and not s['is_probe']) / 3.0
            total_probe_diff = total_fix_probe_dur - total_fix_irrel_dur
            
            all_fix_durations = [s['duration'] for s in samples if s['movement'] == 'Fixation' and s['duration'] > 0]
            mean_fix_duration = float(np.mean(all_fix_durations)) if all_fix_durations else 0.0
            median_fix_duration = float(np.median(all_fix_durations)) if all_fix_durations else 0.0
            fixation_count = len(all_fix_durations)
            
            # Familiarity ground truth label:
            # 1 = familiar (guilty participant viewing crime probe)
            # 0 = unfamiliar (control participant or baseline)
            is_guilty = (group_val.lower().strip() == 'guilty')
            familiarity_label = 1 if is_guilty else 0
            
            trials_records.append({
                'participant_id': participant_name or fname.replace('.xlsx', ''),
                'filename': fname,
                'group': group_val,
                'gender': gender_val,
                'calibration_accuracy_deg': calib_acc_deg,
                'trial_id': f"{participant_name}_{stim_label}",
                'stimulus_name': stim_label,
                'category': int(cat),
                'repetition': int(rep),
                'total_samples': total_samples,
                'valid_sample_ratio': round(valid_ratio, 4),
                'missing_sample_ratio': round(missing_ratio, 4),
                'early_window_sample_count': early_count,
                # Primary temporal features
                'early_probe_fix_dur': round(early_fix_probe_dur, 2),
                'early_irrel_fix_dur': round(early_fix_irrel_dur, 2),
                'early_probe_diff': round(early_probe_diff, 2),
                'mid_probe_diff': round(mid_probe_diff, 2),
                'late_probe_diff': round(late_probe_diff, 2),
                'total_probe_diff': round(total_probe_diff, 2),
                'mean_fix_duration': round(mean_fix_duration, 2),
                'median_fix_duration': round(median_fix_duration, 2),
                'fixation_count': fixation_count,
                'familiarity_label': familiarity_label
            })
            
    except Exception as e:
        print(f"Error processing {fname}: {e}")
        
    return trials_records

def main():
    processed_dir = r"E:\karthianna\data\processed"
    files = sorted(glob.glob(os.path.join(processed_dir, "CIT Recording*.xlsx")))
    print(f"Starting parallel extraction of {len(files)} Zenodo recordings across 8 workers...")
    
    t0 = time.time()
    all_trials = []
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_single_recording, f): f for f in files}
        completed = 0
        for future in as_completed(futures):
            fname = os.path.basename(futures[future])
            try:
                records = future.result()
                all_trials.extend(records)
                completed += 1
                print(f"[{completed}/{len(files)}] Processed {fname}: {len(records)} trials extracted")
            except Exception as e:
                print(f"Failed {fname}: {e}")
                
    elapsed = time.time() - t0
    print(f"\nAll files processed in {elapsed:.2f}s! Total trials extracted: {len(all_trials)}")
    
    df = pd.DataFrame(all_trials)
    out_csv = r"E:\karthianna\data\processed\zenodo_features.csv"
    out_parquet = r"E:\karthianna\data\processed\zenodo_features.parquet"
    
    df.to_csv(out_csv, index=False, encoding='utf-8')
    df.to_parquet(out_parquet, index=False)
    print(f"Saved extracted features dataset to:\n  - {out_csv}\n  - {out_parquet}")
    
    print("\nDataset Summary:")
    print(f"Participants: {df['participant_id'].nunique()}")
    print(f"Trials: {len(df)}")
    print("Class Balance (familiarity_label):")
    print(df['familiarity_label'].value_counts())
    print("\nMean early probe diff (0-500ms) by group:")
    print(df.groupby('group')['early_probe_diff'].describe())

if __name__ == '__main__':
    main()
