import openpyxl
import collections
import json

def analyze_file(filepath):
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb['Data']
    
    header = None
    stim_names = collections.Counter()
    media_names = collections.Counter()
    events = collections.Counter()
    movements = collections.Counter()
    aoi_hits = collections.Counter()
    
    total_rows = 0
    stim_col = None
    media_col = None
    event_col = None
    mov_col = None
    aoi_cols = []
    
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            header = [str(c) if c is not None else '' for c in row]
            stim_col = header.index('Presented Stimulus name')
            media_col = header.index('Presented Media name')
            event_col = header.index('Event')
            mov_col = header.index('Eye movement type')
            for col_idx, col_name in enumerate(header):
                if col_name.startswith('AOI hit'):
                    aoi_cols.append((col_idx, col_name))
            continue
            
        total_rows += 1
        
        s = row[stim_col]
        if s:
            stim_names[str(s)] += 1
            
        m = row[media_col]
        if m:
            media_names[str(m)] += 1
            
        e = row[event_col]
        if e:
            events[str(e)] += 1
            
        mov = row[mov_col]
        if mov:
            movements[str(mov)] += 1
            
        for cidx, cname in aoi_cols:
            val = row[cidx]
            if val == 1 or val == '1':
                aoi_hits[cname] += 1
                
    wb.close()
    
    return {
        "filepath": filepath,
        "total_rows": total_rows,
        "stimulus_counts": dict(stim_names.most_common(20)),
        "media_counts": dict(media_names.most_common(20)),
        "events": dict(events),
        "eye_movements": dict(movements),
        "top_aoi_hits": dict(aoi_hits.most_common(15))
    }

if __name__ == "__main__":
    import sys
    res = analyze_file(r"E:\karthianna\data\processed\CIT Recording1.xlsx")
    with open(r"E:\karthianna\data\cit_recording1_analysis.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Done analysis!")
