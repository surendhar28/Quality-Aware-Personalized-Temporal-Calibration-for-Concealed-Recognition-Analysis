# GazeGuard AI — Data Dictionary & Canonical Schema Specification (Revision 12)

## 1. Verified Primary Benchmark Dataset Provenance
- **Title**: Eye tracking as a Tool for deception detection with CIT
- **Persistent DOI**: `10.5281/zenodo.18525952`
- **Authors**: Weronika Celniak, Dominika Słapczyńska, Beata Jarszak, Piotr Augustyniak
- **Publisher**: Zenodo (February 8, 2026)
- **License**: Creative Commons Attribution 4.0 International (`CC-BY-4.0`)
- **Hardware Apparatus**: Tobii Pro Fusion Desktop Eye Tracker (120–250 Hz) on 27-inch Full HD Monitor (1920×1080).
- **Physical Protocol**: 4-item visual array (1 critical probe item, 3 neutral irrelevant items) presented for 7.5 seconds (7,500 ms) per trial, repeated across 3 exposures with randomized spatial arrangements.
- **Participant Mapping**: 39 recording workbooks (`CIT Recording1.xlsx` to `CIT Recording40.xlsx`, omitting #14). Recording files 25 and 27 both correspond to `Participant25`, yielding **38 processed biological participants** (20 guilty, 18 control).

---

## 2. Evaluated Feature Dictionary (11 Baseline Features)

The authoritative baseline experiment uses the following 11 numeric predictors from `data/processed/zenodo_features.csv`:

| Feature Name | Type | Unit | Formula / Source | Provenance & Validation Notes |
| :--- | :--- | :--- | :--- | :--- |
| `valid_sample_ratio` | Float | Ratio $[0.0, 1.0]$ | $N_{\text{valid}} / N_{\text{total}}$ | Proportion of eye tracker samples marked valid by Tobii tracker during the trial. |
| `early_window_sample_count` | Int | Count | $\sum_{t=0}^{500\text{ ms}} 1_{[\text{sample acquired}]}$ | Number of raw samples recorded in the first 500 ms post-stimulus onset. |
| `early_probe_fix_dur` | Float | Milliseconds (ms) | $\sum \text{Dur}(\text{Fixations}_{\text{Probe}}, 0\text{–}500\text{ ms})$ | Cumulative fixation duration inside the probe Area of Interest (AOI) during 0–500 ms. |
| `early_irrel_fix_dur` | Float | Milliseconds (ms) | $\frac{1}{3} \sum_{k=1}^3 \text{Dur}(\text{Fixations}_{\text{Irrel}_k}, 0\text{–}500\text{ ms})$ | Mean fixation duration across the three irrelevant control AOIs during 0–500 ms. |
| `early_probe_diff` | Float | Milliseconds (ms) | $\text{early\_probe\_fix\_dur} - \text{early\_irrel\_fix\_dur}$ | Divergence in visual orienting dwell between critical and irrelevant items (0–500 ms). |
| `mid_probe_diff` | Float | Milliseconds (ms) | $\text{Dur}(\text{Fix}_{\text{Probe}}, 500\text{–}1000) - \text{Dur}(\text{Fix}_{\text{Irrel}}, 500\text{–}1000)$ | Dwell difference during intermediate appraisal window (500–1000 ms). |
| `late_probe_diff` | Float | Milliseconds (ms) | $\text{Dur}(\text{Fix}_{\text{Probe}}, 1000\text{–}2000) - \text{Dur}(\text{Fix}_{\text{Irrel}}, 1000\text{–}2000)$ | Dwell difference during late conscious exploration window (1000–2000 ms). |
| `total_probe_diff` | Float | Milliseconds (ms) | $\text{Dur}(\text{Fix}_{\text{Probe}}, 0\text{–}7500) - \text{Dur}(\text{Fix}_{\text{Irrel}}, 0\text{–}7500)$ | Total dwell difference across the entire 7.5-second trial presentation. |
| `mean_fix_duration` | Float | Milliseconds (ms) | $\frac{1}{N_{\text{fix}}} \sum_{i=1}^{N_{\text{fix}}} \text{Dur}_i$ | Mean duration of all parsed fixation events in trial. Depends on upstream Tobii I-VT filter parameters. |
| `median_fix_duration` | Float | Milliseconds (ms) | $\text{Median}(\{\text{Dur}_i\}_{i=1}^{N_{\text{fix}}})$ | Median duration of all parsed fixation events in trial. |
| `fixation_count` | Int | Count | $N_{\text{fix}}$ | Total count of discrete fixation events parsed across the entire trial duration. |

---

## 3. Metadata & Contextual Trial Attributes

| Field Name | Type | Unit / Format | Description & Scientific Constraints |
| :--- | :--- | :--- | :--- |
| `participant_id` | String | Categorical | Anonymized participant identifier (`Participant1` to `Participant40`, excluding #14). |
| `filename` | String | Filename | Source recording workbook in `data/processed/` (`CIT Recording*.xlsx`). |
| `group` | String | `guilty` / `control` | Experimental mock-crime condition assigned to participant. |
| `gender` | String | `Female` / `Male` | Participant self-reported demographic gender. |
| `calibration_accuracy_deg` | Float | Degrees (°) | Visual angle calibration error measured prior to recording session (Mean: ~0.26°). |
| `trial_id` | String | String | Compound key: `{Participant}_{Stimulus}_{Repetition}` (e.g., `Participant1_1_1`). |
| `stimulus_name` | String | Code | Identifier for stimulus item configuration (e.g., `1_1`, `2_1`). |
| `category` | Int | $1 \dots 6$ | Stimulus category code (1 = Probe Target, 2..6 = Irrelevant Controls). |
| `repetition` | Int | $1, 2, 3$ | Repetition exposure index for the visual stimulus array. |
| `familiarity_label` | Int | $0$ or $1$ | Supervised ground truth: 1 for Guilty group (probe familiar), 0 for Control group (all unfamiliar). **Constant within each participant.** |
