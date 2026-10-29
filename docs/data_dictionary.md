# GazeGuard AI — Data Dictionary & Canonical Schema Specification

## 1. Verified Primary Benchmark Dataset
- **Title**: Eye tracking as a Tool for deception detection with CIT
- **Persistent DOI**: `10.5281/zenodo.18525952`
- **Authors**: Weronika Celniak, Dominika Słapczyńska, Beata Jarszak, Piotr Augustyniak
- **Publisher**: Zenodo (February 8, 2026)
- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Cohort**: 39 participants (20 experimental guilty group, 19 innocent control group).
- **Apparatus**: Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz) on 27-inch Full HD Monitor.
- **Experimental Protocol**: 4-item stimulus array (1 critical probe item, 3 neutral irrelevant items) presented for 7.5 seconds per trial, repeated 3 times with randomized spatial positions.

## 2. Canonical Ingestion Schema Mappings

| Canonical Field Name | Type | Description | Source Mapping (Tobii CIT Recording) |
|---|---|---|---|
| `participant_id` | String | Pseudonymous participant identifier (e.g., `P01`) | Parsed from file name `CIT Recording*.xlsx` |
| `trial_id` | String | Unique trial identifier (e.g., `P01_T01`) | Derived trial index |
| `stimulus_id` | String | Identifier of presented visual stimulus | Column `Stimulus Name` or `Media Name` |
| `stimulus_name` | String | Human-readable name of visual item | Column `Presented Stimulus name` |
| `condition` | Enum | `probe`, `irrelevant`, `target`, `calibration` | Mapped from stimulus metadata |
| `familiarity_ground_truth` | Int (0/1) | Ground truth familiarity (1=familiar, 0=unfamiliar) | Assigned strictly based on experimental condition |
| `timestamp_ms` | Float | Milliseconds elapsed from stimulus onset | Column `Recording timestamp` |
| `gaze_x` | Float | Normalized horizontal gaze coordinate $[0.0, 1.0]$ | Column `Gaze point X` normalized by display width (1920) |
| `gaze_y` | Float | Normalized vertical gaze coordinate $[0.0, 1.0]$ | Column `Gaze point Y` normalized by display height (1080) |
| `valid` | Boolean | True if gaze point was successfully acquired | Derived from coordinate range and tracking validity |
| `event_type` | String | Fixation, saccade, or unclassified | Column `Eye movement type` (when precomputed) |

## 3. Derived Multi-Window Feature Dictionary

Features extracted per temporal window ($W \in \{\text{w0\_500}, \text{w500\_1000}, \text{w1000\_2000}, \text{w\_overall}\}$):

| Feature Key | Type | Unit | Definition |
|---|---|---|---|
| `{W}_fix_count` | Int | Count | Total number of discrete fixation events overlapping window $W$ |
| `{W}_total_dur` | Float | Milliseconds | Cumulative duration of all fixations inside window $W$ |
| `{W}_mean_dur` | Float | Milliseconds | Arithmetic mean of fixation durations inside window $W$ |
| `{W}_median_dur` | Float | Milliseconds | Median fixation duration inside window $W$ |
| `{W}_first_dur` | Float | Milliseconds | Duration of the very first fixation initiated or overlapping window $W$ |
| `{W}_first_latency` | Float | Milliseconds | Time elapsed from stimulus onset ($t=0$) to start of first fixation |
| `{W}_valid_ratio` | Float | $[0.0, 1.0]$ | Ratio of valid gaze samples acquired within window $W$ |
| `{W}_mean_dur_z` | Float | Z-Score | Participant-baseline normalized mean fixation difference |

## 4. Methodological Assumptions & Boundary Conditions
1. **Four-Item Array vs. Single-Item Presentation**: The Zenodo primary dataset presents 4-item visual arrays over 7.5 seconds, while browser CIT protocols often present single isolated stimuli over 2.0 seconds. The adapter isolates stimulus onset intervals to support comparison.
2. **Dedicated Hardware vs. Webcam Spatial Resolution**: Tobii Pro Fusion provides spatial accuracy of ~0.4°–0.8° visual angle at 120–250 Hz. Browser webcam estimation achieves ~1.5°–3.0° at 30–60 Hz with higher noise and blink artifacts.
3. **Absence of Ground Truth Fabrications**: Labels are derived strictly from experimental design assignments; stimulus familiarity ground truth is never inferred from gaze measurements.
