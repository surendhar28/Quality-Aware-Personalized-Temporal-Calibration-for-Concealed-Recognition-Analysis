import zipfile
import lxml.etree as ET
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

xlsx_path = r'E:\karthianna\data\processed\CIT Recording1.xlsx'

with zipfile.ZipFile(xlsx_path, 'r') as z:
    with z.open('xl/worksheets/sheet1.xml') as f:
        headers = []
        is_first = True
        video_events = []
        for event, elem in ET.iterparse(f, tag='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
            row = [''.join(c.itertext()) for c in elem]
            elem.clear()
            if is_first:
                headers = row
                is_first = False
                event_idx = headers.index('Event')
                stim_idx = headers.index('Presented Stimulus name')
                media_idx = headers.index('Presented Media name')
                continue
                
            e = row[event_idx] if len(row) > event_idx else ''
            if e in ['VideoStimulusStart', 'ImageStimulusStart']:
                video_events.append({
                    'event': e,
                    'stimulus': row[stim_idx] if len(row) > stim_idx else '',
                    'media': row[media_idx] if len(row) > media_idx else ''
                })

with open(r'E:\karthianna\data\cit_stimuli_events.json', 'w', encoding='utf-8') as out:
    json.dump(video_events, out, indent=2, ensure_ascii=False)

print(f'Found {len(video_events)} media start events. Saved to cit_stimuli_events.json')
