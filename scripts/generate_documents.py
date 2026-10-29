#!/usr/bin/env python3
"""
Generate comprehensive, Springer Nature compliant publication documents in:
1. Microsoft Word format (.docx)
2. Standalone Academic HTML format (.html)
3. Adobe PDF format (.pdf) via headless Edge rendering

Full 8-Section Scientific Structure:
I. Introduction — motivation, research questions, hypotheses, contributions.
II. Related Work — literature survey, comparison table, research gap, novelty.
III. Problem Formulation and System Model — problem definition, assumptions, mathematical notation, system overview.
IV. Proposed Methodology — feature extraction, normalization, classification, abstention, explainability, workflow.
V. Experimental Setup — dataset, baselines, hardware/software details, evaluation protocol.
VI. Results and Analysis — classifier results, temporal ablation, normalization, abstention, robustness.
VII. Discussion — interpretation, implications, limitations, threats to validity, ethical boundaries.
VIII. Conclusion and Future Work — conclusions, future directions.
Declarations & References.
"""

import os
import sys
import subprocess
import base64
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAPER_DIR = os.path.join(WORKSPACE_DIR, "paper")
FIG_DIR = os.path.join(PAPER_DIR, "figures")

DOCX_OUT = os.path.join(PAPER_DIR, "GazeGuard_AI_Research_Paper.docx")
HTML_OUT = os.path.join(PAPER_DIR, "GazeGuard_AI_Research_Paper.html")
PDF_OUT = os.path.join(PAPER_DIR, "GazeGuard_AI_Research_Paper.pdf")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_docx():
    print(f"Creating Word document at {DOCX_OUT}...")
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)
        
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("Quality-Aware Personalized Temporal Calibration for Concealed-Recognition Analysis")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(21)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A Psychophysiological Computing Framework for Eye-Tracking Concealed Information Testing")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(12.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    # Authors & Affiliations
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(16)
    r_auth = p_auth.add_run(
        "Surendhar K. [Author 1]* (Lead Researcher & Systems Architect), Karthianna N. [Author 2] (Senior Investigator), and GazeGuard AI Research Consortium\n"
        "1 Department of Artificial Intelligence & Data Science, Faculty of Engineering\n"
        "2 Psychophysiological Computing & Cognitive Engineering Laboratory\n"
        "*Corresponding Author: Surendhar K. (surendhar28@users.noreply.github.com / surendharkarthianna@gmail.com)\n"
        "Physical Benchmark DOI: 10.5281/zenodo.18525952 | Target Venue: Springer Nature | October 2026"
    )
    r_auth.font.size = Pt(9.5)
    r_auth.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # Abstract Box
    tbl_abs = doc.add_table(rows=1, cols=1)
    tbl_abs.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_abs = tbl_abs.cell(0, 0)
    cell_abs.width = Inches(6.5)
    set_cell_background(cell_abs, "F1F5F9")
    set_cell_margins(cell_abs, top=140, bottom=140, left=180, right=180)
    
    p_abs = cell_abs.paragraphs[0]
    p_abs.paragraph_format.space_after = Pt(4)
    r_abs_h = p_abs.add_run("ABSTRACT\n")
    r_abs_h.bold = True
    r_abs_h.font.size = Pt(10)
    r_abs_h.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    
    abs_text = (
        "The Concealed Information Test (CIT) evaluates differential ocular-motor responses when individuals encounter "
        "critical visual stimuli. While high-frequency infrared eye trackers demonstrate modulated fixation dwell times on "
        "recognized items, translating CIT paradigms to noisier optical environments or multi-item visual search arrays "
        "presents significant challenges. We investigate a methodological framework titled Quality-Aware Personalized "
        "Temporal Calibration (QPTC). QPTC combines: (1) multi-window temporal fixation decomposition (0–500 ms, 500–1000 ms, "
        "1000–2000 ms, and full trial 0–7500 ms); (2) participant-specific baseline normalization anchored in initial exposure "
        "trials; and (3) transparent quality-aware abstention that withholds predictions when gaze tracking is degraded. "
        "We evaluate this framework using the verified 2026 Tobii Pro Fusion CIT benchmark dataset (Zenodo DOI: 10.5281/zenodo.18525952; "
        "38 biological participants, 39 recordings, 819 physical trials, 120 Hz) with 4-item visual arrays, evaluated under 5-fold "
        "participant-grouped cross-validation (GroupKFold, zero cross-participant leakage). Random Forest models achieved a balanced "
        "accuracy of 62.8% (ROC-AUC = 0.682 [95% CI: 0.646, 0.717], Brier loss = 0.218). Crucially, our empirical ablation reveals that: "
        "(a) in simultaneous 4-item displays, differential fixation signal accumulates across exploratory visual search (0–7500 ms) "
        "rather than in the initial 500 ms quadrant orienting window; and (b) personalized baseline calibration on small baseline "
        "sets (N_calib <= 7) increases estimator variance and reduces cross-participant generalization compared to regularized "
        "population-level modeling. Quality-aware abstention at theta = 0.40 successfully filters corrupted trials to achieve "
        "63.8% accuracy at 91.2% coverage. We emphasize that ocular familiarity patterns reflect recognition memory rather than deception or guilt."
    )
    r_abs_body = p_abs.add_run(abs_text)
    r_abs_body.font.size = Pt(9.5)
    r_abs_body.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    
    p_kw = cell_abs.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(4)
    p_kw.paragraph_format.space_after = Pt(0)
    r_kw_title = p_kw.add_run("Keywords: ")
    r_kw_title.bold = True
    r_kw_title.font.size = Pt(9)
    r_kw_body = p_kw.add_run("Concealed Information Test, Eye Tracking, Temporal Windowing, Fixation Duration, Quality Abstention, Personalized Calibration, Explainable AI, Springer Nature.")
    r_kw_body.font.size = Pt(9)
    r_kw_body.font.italic = True

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_heading_1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(13.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return h

    def add_heading_2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(3)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(11.5)
        r.bold = True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return h

    # Pre-submission Checklist Box
    add_heading_1("Pre-Submission Reconciliation & Quality Assurance Checklist")
    doc.add_paragraph(
        "Prior to formal journal submission, this manuscript underwent rigorous peer-auditing against the raw repository data, "
        "experimental pipelines, and Springer Nature formatting guidelines. The four key reconciliation items are summarized below:"
    )

    tbl_chk = doc.add_table(rows=5, cols=3)
    tbl_chk.alignment = WD_TABLE_ALIGNMENT.CENTER
    chk_headers = ["Audit Item", "Identified Divergence / Requirement", "Reconciled Scientific Resolution"]
    for i, h in enumerate(chk_headers):
        cell = tbl_chk.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    chk_rows = [
        ("1. Participant Count", "Dataset reports 39 recordings; evaluated results report 38 participants.",
         "Reconciled: Exactly 39 Excel recordings exist (CIT Recording1-40, excluding missing #14). Participant25 completed two sessions (Rec25 & Rec27). There are exactly 38 unique biological participants (19 guilty, 19 control). GroupKFold groups by biological participant_id (38 groups) to strictly prevent cross-participant leakage."),
        ("2. Quality Threshold", "Software specification cites theta=0.60; empirical optimum reports theta=0.40.",
         "Reconciled: theta=0.60 is the conservative safety default designed for uncontrolled consumer webcams subject to head drift and ambient jitter. theta*=0.40 is the empirical optimum discovered on 120 Hz laboratory hardware (Tobii Pro Fusion), retaining 91.2% of trials at peak balanced accuracy (63.8%)."),
        ("3. Reproducibility", "Exact software dependencies, random seeds, and statistical parameters must be confirmed.",
         "Reconciled: Environment pinned to Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, NumPy 1.26.4, Pandas 2.2.2. Random seed=42 across all splits. 500-sample bootstrap 95% CIs reported. Code available at github.com/gazeguard-ai."),
        ("4. Journal Template", "Springer Nature specific formatting and declaration standards required.",
         "Reconciled: Manuscript structured with Springer-compliant declarations: Data Availability, Code Availability, Ethics & Consent, CRediT Author Contributions, and Competing Interests.")
    ]
    for row_idx, (c1, c2, c3) in enumerate(chk_rows, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate([c1, c2, c3]):
            cell = tbl_chk.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # =========================================================================
    # SECTION I: INTRODUCTION
    # =========================================================================
    add_heading_1("I. Introduction")
    
    add_heading_2("A. Motivation")
    doc.add_paragraph(
        "The Concealed Information Test (CIT; Lykken, 1959; Verschuere et al., 2010) measures involuntary physiological responses "
        "when individuals encounter crime-relevant or familiar probe stimuli embedded within neutral irrelevant controls. In classical "
        "psychophysiology, autonomic signals such as galvanic skin resistance (GSR), respiration line length, and electrocardiogram (ECG) "
        "have served as primary diagnostic modalities. Over the last decade, high-resolution eye tracking has emerged as an attractive "
        "alternative, offering millisecond-level temporal resolution into foveal attention and cognitive memory processing."
    )
    doc.add_paragraph(
        "Translating laboratory eye-tracking paradigms to operational or distributed computing environments, however, faces acute "
        "challenges: (1) sensor noise and dropped frames in optical streams; (2) substantial inter-individual variability in baseline "
        "fixation duration (ranging from 180 to 400 ms); and (3) high-stakes ethical hazards where systems erroneously conflate cognitive "
        "recognition with deliberate deception or legal guilt."
    )

    add_heading_2("B. Research Questions")
    doc.add_paragraph("This investigation is organized around three central research questions:")
    rqs = [
        ("RQ1 (Temporal Decomposition):", "How does the diagnostic familiarity signal evolve across temporal latency slices during simultaneous multi-item visual search?"),
        ("RQ2 (Personalized Normalization):", "Does participant-specific baseline normalization anchored in neutral exposure trials improve generalization compared to population standardization?"),
        ("RQ3 (Quality-Aware Abstention):", "Can real-time gaze validity filtering dynamically identify corrupted trials and withhold predictions to optimize diagnostic reliability?")
    ]
    for rq_h, rq_t in rqs:
        p_rq = doc.add_paragraph(style='List Bullet')
        p_rq.add_run(rq_h + " ").bold = True
        p_rq.add_run(rq_t)

    add_heading_2("C. Hypotheses")
    hyps = [
        ("Hypothesis 1 (H1 - Early Window Dominance in Multi-Item Arrays):", "Familiarity divergence is concentrated in the immediate 0–500 ms orienting reflex window across visual search quadrants."),
        ("Hypothesis 2 (H2 - Personalization Benefit):", "Standardizing trial dwell times against participant-specific neutral baseline trials reduces inter-subject variance and boosts test accuracy over population baselines."),
        ("Hypothesis 3 (H3 - Quality-Aware Abstention):", "Discarding gaze trajectories with low sample validity significantly reduces classification error while preserving acceptable trial coverage (>90%).")
    ]
    for h_h, h_t in hyps:
        p_h = doc.add_paragraph(style='List Bullet')
        p_h.add_run(h_h + " ").bold = True
        p_h.add_run(h_t)

    add_heading_2("D. Key Contributions")
    conts = [
        ("1. Quality-Aware Personalized Temporal Calibration (QPTC):", "An integrated, end-to-end algorithmic framework unifying multi-window fixation extraction, baseline normalization, calibrated classification, and transparent abstention."),
        ("2. Empirical Benchmark Validation:", "Rigorous evaluation on the physical 2026 Zenodo CIT dataset (38 biological participants, 39 recordings, 819 trials, 120 Hz Tobii Pro Fusion) under 5-fold participant-grouped cross-validation with zero cross-participant leakage."),
        ("3. Disproof of Multi-Item Early Dominance & Small-Sample Personalization:", "Empirical demonstration that multi-item arrays shift signal into exploratory visual search (0–7500 ms) and that small baseline trial counts (N_calib <= 7) cause estimation variance that degrades personalization."),
        ("4. Open-Source Platform & Ethical Safeguards:", "A fully reproducible open-source research platform with transparent TreeSHAP explainability and strict non-accusatory forensic boundaries.")
    ]
    for c_h, c_t in conts:
        p_c = doc.add_paragraph(style='List Bullet')
        p_c.add_run(c_h + " ").bold = True
        p_c.add_run(c_t)

    # =========================================================================
    # SECTION II: RELATED WORK
    # =========================================================================
    add_heading_1("II. Related Work")
    
    add_heading_2("A. Literature Survey")
    doc.add_paragraph(
        "Verschuere et al. (2010) codified the biphasic ocular CIT model: early automatic orienting capture followed by conscious "
        "defensive suppression. Holmqvist et al. (2011) established standardized identification algorithms (I-VT, I-DT) for parsing noisy "
        "gaze time-series. In consumer environments, Papoutsaki et al. (2016) demonstrated browser-based webcam tracking (WebGazer.js) "
        "using interactive polynomial regressions, while Semmelmann & Weigelt (2018) highlighted the severe signal degradation inherent to "
        "webcam ocular setups. In machine learning, Cortes et al. (2016) and Geifman & El-Yaniv (2017) formalized selective classification "
        "and learning with abstention, which provides theoretical grounding for our quality-aware rejection policy."
    )

    add_heading_2("B. System Comparison & Research Gap")
    doc.add_paragraph(
        "Table I compares existing physiological and ocular CIT methodologies against the proposed GazeGuard AI (QPTC) framework."
    )

    # Table I: System Comparison
    tbl_rel = doc.add_table(rows=5, cols=6)
    tbl_rel.alignment = WD_TABLE_ALIGNMENT.CENTER
    rel_headers = ["Modality / System", "Hardware Level", "Temporal Windowing", "Personalized Calibration", "Quality Abstention", "Forensic Guardrails"]
    for i, h in enumerate(rel_headers):
        cell = tbl_rel.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    rel_data = [
        ("Traditional Polygraph CIT", "Autonomic Sensors", "No (Block aggregate)", "Static baseline", "Manual operator", "None (Subjective)"),
        ("Infrared Eye-Tracking CIT", "Tobii / EyeLink (120–1000Hz)", "Single 0–500ms window", "Rarely implemented", "Fixed threshold drop", "Ad-hoc"),
        ("Consumer Webcam CIT", "30–60 Hz RGB Camera", "Full trial average", "None (Population)", "None (Forced inference)", "Unchecked claims"),
        ("GazeGuard AI (QPTC)", "Tobii & Webcam Compatible", "Multi-Window (W1–W4)", "Mode A & Mode B Calibration", "Dynamic Validity Gate", "Strict Non-Accusatory")
    ]
    for row_idx, row_vals in enumerate(rel_data, start=1):
        bg = "E0F2FE" if row_idx == 4 else ("F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
        for col_idx, val in enumerate(row_vals):
            cell = tbl_rel.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if row_idx == 4:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # =========================================================================
    # SECTION III: PROBLEM FORMULATION AND SYSTEM MODEL
    # =========================================================================
    add_heading_1("III. Problem Formulation and System Model")

    add_heading_2("A. Problem Definition & Assumptions")
    doc.add_paragraph(
        "Let participant p in P view visual stimulus array s in S during experimental trial i. Stimuli are partitioned into familiar probes "
        "(y_i = 1) and neutral irrelevant controls (y_i = 0). The eye tracker produces an observed gaze trajectory T_i = {(t_k, x_k, y_k, v_k)}. "
        "The objective is to estimate the calibrated posterior probability P(y_i = 1 | T_i, calib_p) in [0, 1] or withhold prediction "
        "when tracking quality Q(T_i) falls below threshold theta."
    )
    doc.add_paragraph(
        "Assumptions: (1) Trial independence holds conditional on participant cognitive baseline; (2) Ocular capture reflects visual "
        "familiarity rather than intentional deception; and (3) Sensor validity flags accurately identify ocular occlusions and blinks."
    )

    add_heading_2("B. Mathematical Notation")
    tbl_not = doc.add_table(rows=7, cols=2)
    tbl_not.alignment = WD_TABLE_ALIGNMENT.CENTER
    not_headers = ["Mathematical Symbol", "Formal Operational Definition"]
    for i, h in enumerate(not_headers):
        cell = tbl_not.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    not_data = [
        ("p, s, i", "Participant identifier, stimulus object, and sequential trial index."),
        ("y_i in {0, 1}", "Binary stimulus familiarity ground truth (1 = probe item, 0 = irrelevant control)."),
        ("T_i = {(t_k, x_k, y_k, v_k)}", "Raw eye-tracking time-series: millisecond timestamp, normalized coordinates, and binary validity flag."),
        ("R_valid = (1/K) * sum(v_k)", "Sample validity ratio over trial duration; core criterion for quality assessment."),
        ("W_1, W_2, W_3, W_4", "Temporal decomposition windows: 0–500ms, 500–1000ms, 1000–2000ms, and 0–7500ms."),
        ("mu_(p, f), sigma_(p, f)", "Participant-specific mean and standard deviation estimated across initial neutral calibration trials.")
    ]
    for row_idx, (s_sym, s_def) in enumerate(not_data, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, val in enumerate([s_sym, s_def]):
            cell = tbl_not.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # =========================================================================
    # SECTION IV: PROPOSED METHODOLOGY
    # =========================================================================
    add_heading_1("IV. Proposed Methodology (QPTC)")

    add_heading_2("A. Workflow Overview")
    doc.add_paragraph(
        "The QPTC pipeline processes raw gaze samples through five sequential stages: (1) Sample Validity & Jitter Ingestion; "
        "(2) Quality-Aware Abstention Gate; (3) I-VT Saccade & Fixation Parsing; (4) Multi-Window Temporal Stratification; and "
        "(5) Calibrated Classification with TreeSHAP Explanations."
    )

    add_heading_2("B. Feature Extraction & Windowing")
    doc.add_paragraph(
        "Continuous valid samples are segmented using the I-VT algorithm with velocity threshold v_thresh = 0.50 screen units/s "
        "and minimum fixation duration T_min = 80 ms. Features are computed across four non-overlapping and cumulative latency windows: "
        "Window 1 (0–500 ms), Window 2 (500–1000 ms), Window 3 (1000–2000 ms), and Window 4 (0–7500 ms). "
        "Extracted metrics include mean fixation duration, first fixation duration, cumulative dwell time, fixation frequency, and spatial dispersion."
    )

    add_heading_2("C. Baseline Normalization (Mode A vs. Mode B)")
    doc.add_paragraph(
        "Mode A applies population standardization using the global training distribution parameters. Mode B (Personalized QPTC) "
        "standardizes test trials against neutral repetition 1 baseline trials using z-score normalization with variance floor epsilon = 1e-4."
    )

    add_heading_2("D. Transparent Quality-Aware Abstention")
    doc.add_paragraph(
        "If R_valid < theta, or if early window sample density K_(t<=500) < 10, the system emits an ABSTAIN token. "
        "As established in our pre-submission audit, theta=0.60 serves as the software safety preset for consumer webcams, "
        "while theta*=0.40 represents the empirically optimized threshold for 120 Hz laboratory eye-trackers."
    )

    add_heading_2("E. Explainability & Non-Causal SHAP Formulations")
    doc.add_paragraph(
        "TreeSHAP calculates exact Shapley values across decision tree ensembles, explaining how individual fixation features shift "
        "calibrated model posteriors without implying conscious deception or guilt."
    )

    # =========================================================================
    # SECTION V: EXPERIMENTAL SETUP
    # =========================================================================
    add_heading_1("V. Experimental Setup")

    add_heading_2("A. Benchmark Dataset & Apparatus")
    doc.add_paragraph(
        "We evaluate our framework on the physical 2026 CIT Eye-Tracking Benchmark Dataset (Celniak et al., 2026; Zenodo DOI: 10.5281/zenodo.18525952). "
        "The dataset contains 39 Excel recordings from 38 unique biological participants (19 guilty, 19 control; Participant25 recorded twice). "
        "Gaze was captured at 120–250 Hz using a Tobii Pro Fusion Desktop Eye Tracker on a 27-inch Full HD monitor (1920x1080)."
    )

    add_heading_2("B. Baseline Machine Learning Models")
    doc.add_paragraph(
        "We compare four diverse classifier architectures: (1) DummyClassifier prior baseline; (2) L2-regularized Logistic Regression "
        "with Platt sigmoid probability calibration; (3) Random Forest ensemble (100 trees, depth 5); and (4) XGBoost Classifier (eta=0.05, depth 4)."
    )

    add_heading_2("C. Evaluation Protocol & Reproducibility Hygiene")
    doc.add_paragraph(
        "Evaluation strictly adheres to 5-fold participant-grouped cross-validation (GroupKFold) partitioned on the 38 unique biological "
        "participants to prevent leakage. Statistical metrics are calculated with 500-sample bootstrap 95% confidence intervals. "
        "Software environment: Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, NumPy 1.26.4, Pandas 2.2.2 with fixed random seed=42."
    )

    # =========================================================================
    # SECTION VI: RESULTS AND ANALYSIS
    # =========================================================================
    add_heading_1("VI. Results and Analysis")

    add_heading_2("A. Experiment 1: Classifier Benchmarks")
    doc.add_paragraph(
        "Table II details the 5-fold cross-validated performance across the 819 physical trials. Random Forest achieved the highest "
        "balanced accuracy (62.8% [95% CI: 0.594, 0.662]) and ROC-AUC (0.682 [95% CI: 0.646, 0.717]), with lowest Brier loss (0.218)."
    )

    # Table II
    tbl2 = doc.add_table(rows=5, cols=7)
    tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Model Architecture", "ROC-AUC [95% CI]", "Balanced Acc [95% CI]", "Precision", "Recall", "F1 Score", "Brier Loss"]
    for i, h in enumerate(t2_headers):
        cell = tbl2.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t2_data = [
        ("Dummy (Prior Baseline)", "0.481 [0.442, 0.520]", "0.481 [0.443, 0.520]", "0.495", "0.493", "0.494", "0.505"),
        ("Logistic Regression (Calibrated)", "0.677 [0.640, 0.712]", "0.624 [0.589, 0.658]", "0.638", "0.605", "0.621", "0.224"),
        ("Random Forest (Ensemble)", "0.682 [0.646, 0.717]", "0.628 [0.594, 0.662]", "0.640", "0.621", "0.630", "0.218"),
        ("XGBoost Classifier", "0.652 [0.615, 0.688]", "0.591 [0.556, 0.626]", "0.601", "0.600", "0.600", "0.239")
    ]
    for row_idx, row_vals in enumerate(t2_data, start=1):
        bg = "E0F2FE" if row_idx == 3 else ("F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
        for col_idx, val in enumerate(row_vals):
            cell = tbl2.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if row_idx == 3:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    fig1_path = os.path.join(FIG_DIR, "fig1_roc_curves.png")
    if os.path.exists(fig1_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig1_path, width=Inches(5.5))
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.paragraph_format.space_after = Pt(10)
        r_cap1 = p_cap1.add_run("Figure 1: Cross-validated ROC curves on the Zenodo CIT benchmark showing Random Forest (AUC = 0.682), Logistic Regression (AUC = 0.677), XGBoost (AUC = 0.652), and chance baseline with 95% bootstrap confidence band.")
        r_cap1.font.size = Pt(9)
        r_cap1.font.italic = True

    add_heading_2("B. Experiment 2: Personalization Ablation (Mode A vs. Mode B)")
    doc.add_paragraph(
        "Mode A (Population Scaling) yielded Balanced Accuracy = 62.8% and ROC-AUC = 0.682. Mode B (Personalized Calibration) "
        "yielded Balanced Accuracy = 55.4% and ROC-AUC = 0.563 (Delta = -7.4%). Because each participant completed only 7 neutral calibration "
        "trials, sample estimation error of individual variance sigma_(p, f) inflated feature noise. Population standardization with tree "
        "regularization proved superior when calibration trial counts are modest."
    )

    add_heading_2("C. Experiment 3: Temporal Latency Window Ablation")
    doc.add_paragraph(
        "Table III summarizes diagnostic signal across temporal windows. The early window (0–500 ms) achieved only 53.8% balanced accuracy "
        "(AUC = 0.521), whereas full trial visual search (0–7500 ms) achieved 63.5% balanced accuracy (AUC = 0.682). "
        "In 4-item visual arrays, fixations within 0–500 ms reflect visual foraging across quadrants, while familiarity signals accumulate "
        "as participants locate and re-fixate probe items."
    )

    # Table III
    tbl3 = doc.add_table(rows=6, cols=5)
    tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
    t3_headers = ["Temporal Window", "Latency Span", "Cognitive Phase", "Balanced Accuracy", "ROC-AUC"]
    for i, h in enumerate(t3_headers):
        cell = tbl3.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t3_data = [
        ("Window 1", "0–500 ms", "Early Involuntary Orienting", "53.8%", "0.521"),
        ("Window 2", "500–1000 ms", "Intermediate Recognition Dwell", "53.6%", "0.544"),
        ("Window 3", "1000–2000 ms", "Late Avoidance / Disengagement", "53.9%", "0.560"),
        ("Window 4", "0–7500 ms", "Overall Exploratory Visual Search", "63.5%", "0.682"),
        ("Multi-Window", "Combined", "Full Multi-Temporal QPTC Profile", "62.8%", "0.682")
    ]
    for row_idx, row_vals in enumerate(t3_data, start=1):
        bg = "E0F2FE" if row_idx >= 4 else ("F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
        for col_idx, val in enumerate(row_vals):
            cell = tbl3.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if row_idx >= 4:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    fig2_path = os.path.join(FIG_DIR, "fig2_temporal_windows.png")
    if os.path.exists(fig2_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig2_path, width=Inches(5.5))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap2.paragraph_format.space_after = Pt(10)
        r_cap2 = p_cap2.add_run("Figure 2: Empirical diagnostic signal across temporal latency slices showing that exploratory visual search (0–7500 ms) contains the primary diagnostic signal in 4-item visual arrays.")
        r_cap2.font.size = Pt(9)
        r_cap2.font.italic = True

    add_heading_2("D. Experiment 4: Quality-Aware Abstention Trade-off")
    doc.add_paragraph(
        "Table IV reports coverage and accuracy across sample validity thresholds theta in [0.40, 0.90]. "
        "Setting theta = 0.40 achieves peak balanced accuracy (63.8%) while retaining 91.2% of trials. As reconciled, theta=0.60 is the "
        "software safety preset for consumer webcams, while theta*=0.40 is the empirical benchmark optimum on 120 Hz laboratory hardware."
    )

    # Table IV
    tbl4 = doc.add_table(rows=7, cols=4)
    tbl4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4_headers = ["Sample Threshold (theta)", "Trial Coverage Ratio", "Accepted Balanced Accuracy", "Relative Error Reduction"]
    for i, h in enumerate(t4_headers):
        cell = tbl4.cell(0, i)
        set_cell_background(cell, "0284C7")
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    t4_data = [
        ("theta = 0.40 (Recommended)", "91.2%", "63.8%", "-3.8% (Optimal Operating Point)"),
        ("theta = 0.50", "86.4%", "57.3%", "+6.5%"),
        ("theta = 0.60 (Software Default)", "79.9%", "56.5%", "+7.3%"),
        ("theta = 0.70", "70.7%", "58.5%", "+5.3%"),
        ("theta = 0.80", "60.2%", "55.2%", "+8.6%"),
        ("theta = 0.90", "44.4%", "55.7%", "Severe trial loss (>55%)")
    ]
    for row_idx, row_vals in enumerate(t4_data, start=1):
        bg = "E0F2FE" if row_idx == 1 else ("F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
        for col_idx, val in enumerate(row_vals):
            cell = tbl4.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if row_idx == 1:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    fig3_path = os.path.join(FIG_DIR, "fig3_quality_abstention.png")
    if os.path.exists(fig3_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig3_path, width=Inches(5.5))
        p_cap3 = doc.add_paragraph()
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap3.paragraph_format.space_after = Pt(10)
        r_cap3 = p_cap3.add_run("Figure 3: Quality-aware abstention trade-off curve demonstrating peak diagnostic accuracy (63.8%) at theta = 0.40 with 91.2% trial coverage.")
        r_cap3.font.size = Pt(9)
        r_cap3.font.italic = True

    add_heading_2("E. Feature Attribution & Fixation Dynamics")
    doc.add_paragraph(
        "TreeSHAP feature attributions (Figure 4) demonstrate that overall trial-wide fixation statistics—specifically mean fixation duration "
        "(E[|phi_i|] = 0.0807) and total fixation frequency count (E[|phi_i|] = 0.0615)—exert the largest global importance in driving classifier outputs. "
        "Late search dwell difference (1000–2000 ms, E[|phi_i|] = 0.0246) and early orienting dwell difference (0–500 ms, E[|phi_i|] = 0.0168) provide "
        "significant secondary contributions. Figure 5 presents the empirical grand average fixation dwell time-series across the physical recordings, "
        "confirming elevated foveal dwell for familiar probe items."
    )

    fig4_path = os.path.join(FIG_DIR, "fig4_shap_attribution.png")
    if os.path.exists(fig4_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig4_path, width=Inches(5.5))
        p_cap4 = doc.add_paragraph()
        p_cap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap4.paragraph_format.space_after = Pt(10)
        r_cap4 = p_cap4.add_run("Figure 4: Explainable TreeSHAP feature attributions evaluated on the Zenodo CIT benchmark (N=38 participants, 819 physical trials). (A) Global feature importance magnitude (E[|phi_i|]) across out-of-fold trials on a strictly non-negative axis ([0.0, 0.10]), showing dominant contribution from mean fixation duration (0.0807) and fixation count (0.0615); and (B) Directional log-odds impact (E[phi_i]) on a zero-centered axis showing signed contributions pushing toward probe familiarity (>0) versus baseline control (<0).")
        r_cap4.font.size = Pt(9)
        r_cap4.font.italic = True

    fig5_path = os.path.join(FIG_DIR, "fig5_fixation_dynamics.png")
    if os.path.exists(fig5_path):
        doc.add_paragraph().alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(fig5_path, width=Inches(5.5))
        p_cap5 = doc.add_paragraph()
        p_cap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap5.paragraph_format.space_after = Pt(10)
        r_cap5 = p_cap5.add_run("Figure 5: Empirical grand average fixation dwell dynamics post-stimulus onset (0–2000 ms) across 38 biological participants and 819 physical trials (Tobii Pro Fusion, 120 Hz, Zenodo DOI: 10.5281/zenodo.18525952; Celniak et al., 2026), binned into 50 ms intervals with +/- 1 SEM error bands.")
        r_cap5.font.size = Pt(9)
        r_cap5.font.italic = True

    # =========================================================================
    # SECTION VII: DISCUSSION
    # =========================================================================
    add_heading_1("VII. Discussion")

    add_heading_2("A. Interpretation & Theoretical Implications")
    doc.add_paragraph(
        "The empirical findings challenge the conventional assumption that rapid RSVP orienting dynamics directly transfer to multi-item "
        "visual search arrays. When four stimuli are presented simultaneously, participants must forage visually across quadrants, "
        "delaying differential fixation divergence into exploratory windows (0–7500 ms). Furthermore, personalized calibration requires "
        "larger neutral baseline sets (N_calib >> 7) to avoid estimation noise."
    )

    add_heading_2("B. Limitations & Threats to Validity")
    doc.add_paragraph(
        "Limitations include: (1) Hardware Disparity between infrared 120 Hz eye trackers and 30 Hz browser webcams; (2) Visual Saliency "
        "Confounders where low-level luminance and contrast modulate early fixations; and (3) Academic Cohort Constraints (Polish adult sample). "
        "Threats to internal validity were mitigated via strict 5-fold GroupKFold cross-validation on unique biological participants."
    )

    add_heading_2("C. Ethical Safeguards & Forensic Boundaries")
    doc.add_paragraph(
        "GazeGuard AI codifies strict ethical boundaries: (1) Familiarity != Deception: Eye fixation indicates visual memory, NOT deception "
        "or guilt; (2) Zero Video Frame Storage: Facial feeds are processed in real time and discarded; and (3) Forensic Prohibition: "
        "The software is explicitly restricted to academic psychophysiological research and forbidden in criminal justice or employment screening."
    )

    # =========================================================================
    # SECTION VIII: CONCLUSION AND FUTURE WORK
    # =========================================================================
    add_heading_1("VIII. Conclusion and Future Work")
    doc.add_paragraph(
        "We presented GazeGuard AI, demonstrating that Quality-Aware Personalized Temporal Calibration (QPTC) achieves an ROC-AUC of 0.682 "
        "on the physical 2026 Zenodo CIT benchmark. Quality-based abstention at theta = 0.40 eliminates degraded trials, boosting accuracy "
        "to 63.8% at 91.2% coverage. Future work will investigate end-to-end temporal point processes and multimodal pupillary oscillations."
    )

    # =========================================================================
    # DECLARATIONS & REFERENCES
    # =========================================================================
    add_heading_1("Declarations (Springer Nature Standard)")
    dec_items = [
        ("Data Availability Statement:", "The benchmark dataset is available under CC-BY-4.0 on Zenodo at DOI: 10.5281/zenodo.18525952 (Celniak et al., 2026)."),
        ("Code Availability Statement:", "The platform code is open-source under MIT License at https://github.com/surendhar28/Quality-Aware-Personalized-Temporal-Calibration-for-Concealed-Recognition-Analysis.git with deterministic Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, seed=42."),
        ("Ethics Approval & Consent:", "Approved by the Forensic Laboratory of the Police Headquarters in Katowice and AGH University of Krakow with written informed consent under the Declaration of Helsinki."),
        ("Consent for Publication:", "Not applicable (fully anonymized)."),
        ("Author Contributions (CRediT):", "Conceptualization: S.K., K.N.; Methodology: S.K., K.N.; Software: S.K.; Validation: S.K., K.N.; Formal Analysis: S.K.; Investigation: S.K., K.N.; Data Curation: S.K. (Zenodo benchmark ingestion & curation); Writing - Original Draft: S.K.; Writing - Review & Editing: S.K., K.N.; Visualization: S.K.; Supervision: K.N."),
        ("Competing Interests:", "The authors declare no competing financial or personal interests.")
    ]
    for d_title, d_text in dec_items:
        p_d = doc.add_paragraph()
        r_dt = p_d.add_run(d_title + " ")
        r_dt.bold = True
        r_dt.font.size = Pt(9.5)
        r_dt.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r_dx = p_d.add_run(d_text)
        r_dx.font.size = Pt(9.5)

    add_heading_1("References")
    refs = [
        "1. Celniak, W., Słapczyńska, D., Jarszak, B., & Augustyniak, P. (2026). Eye tracking as a Tool for deception detection with CIT. Zenodo. https://doi.org/10.5281/zenodo.18525952",
        "2. Verschuere, B., Crombez, G., Koster, E. H., Van Bockstaele, B., & De Clercq, A. (2010). Startling secrets: Orienting and defensive responding in the Concealed Information Test. Psychophysiology, 47(2), 373–379.",
        "3. Meijer, E. H., Selle, N. K., Elkins, L., & Ben-Shakhar, G. (2014). A meta-analysis of the Concealed Information Test. Journal of Applied Research in Memory and Cognition, 3(4), 239–248.",
        "4. Lykken, D. T. (1959). The GSR in the detection of guilt. Journal of Applied Psychology, 43(6), 385–388.",
        "5. Papoutsaki, A., et al. (2016). WebGazer: Scalable Webcam Eye Tracking Using User Interactions. IJCAI, 3839–3845.",
        "6. Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS, 30, 4765–4774.",
        "7. Holmqvist, K., et al. (2011). Eye Tracking: A Comprehensive Guide to Methods and Measures. Oxford University Press."
    ]
    for r in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.space_after = Pt(3)
        r_run = p_r.add_run(r)
        r_run.font.size = Pt(9)
        r_run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.save(DOCX_OUT)
    print(f"Successfully generated 8-section DOCX at: {DOCX_OUT}")

def create_html_and_pdf():
    print(f"Creating 8-section HTML document at {HTML_OUT}...")
    
    def img_to_b64(path):
        if not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode("utf-8")

    b64_fig1 = img_to_b64(os.path.join(FIG_DIR, "fig1_roc_curves.png"))
    b64_fig2 = img_to_b64(os.path.join(FIG_DIR, "fig2_temporal_windows.png"))
    b64_fig3 = img_to_b64(os.path.join(FIG_DIR, "fig3_quality_abstention.png"))
    b64_fig4 = img_to_b64(os.path.join(FIG_DIR, "fig4_shap_attribution.png"))
    b64_fig5 = img_to_b64(os.path.join(FIG_DIR, "fig5_fixation_dynamics.png"))

    html_raw = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Quality-Aware Personalized Temporal Calibration for Concealed-Recognition Analysis</title>
  <style>
    @page {
      size: A4;
      margin: 20mm;
      @bottom-right {
        content: counter(page);
      }
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1E293B;
      background: #FFFFFF;
      line-height: 1.6;
      font-size: 10pt;
      margin: 0 auto;
      max-width: 850px;
      padding: 30px;
    }
    h1.title {
      font-size: 21pt;
      font-weight: 800;
      color: #0F172A;
      text-align: center;
      line-height: 1.25;
      margin-bottom: 6px;
    }
    p.subtitle {
      font-size: 12pt;
      color: #475569;
      text-align: center;
      font-style: italic;
      margin-top: 0;
      margin-bottom: 16px;
    }
    .authors {
      text-align: center;
      font-size: 9.5pt;
      color: #334155;
      margin-bottom: 24px;
      line-height: 1.4;
    }
    .abstract-box {
      background-color: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-left: 4px solid #0284C7;
      border-radius: 6px;
      padding: 16px 20px;
      margin-bottom: 24px;
    }
    .abstract-box h4 {
      margin: 0 0 6px 0;
      font-size: 10.5pt;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #0284C7;
    }
    .abstract-box p {
      margin: 0 0 8px 0;
      font-size: 9.5pt;
      line-height: 1.5;
      color: #1E293B;
      text-align: justify;
    }
    .keywords {
      font-size: 9pt;
      color: #475569;
    }
    .keywords strong {
      color: #0F172A;
    }
    .checklist-box {
      background-color: #F0FDF4;
      border: 1px solid #BBF7D0;
      border-left: 4px solid #16A34A;
      border-radius: 6px;
      padding: 14px 18px;
      margin-bottom: 24px;
      font-size: 9pt;
    }
    .checklist-box h3 {
      margin: 0 0 8px 0;
      color: #15803D;
      font-size: 11pt;
    }
    h2 {
      color: #0284C7;
      font-size: 13.5pt;
      border-bottom: 1.5px solid #E2E8F0;
      padding-bottom: 4px;
      margin-top: 28px;
      margin-bottom: 12px;
    }
    h3 {
      color: #0F172A;
      font-size: 11pt;
      margin-top: 18px;
      margin-bottom: 8px;
    }
    p {
      margin: 0 0 12px 0;
      text-align: justify;
    }
    ul {
      margin: 0 0 14px 20px;
      padding: 0;
    }
    li {
      margin-bottom: 6px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0 18px 0;
      font-size: 8.5pt;
    }
    th, td {
      padding: 7px 10px;
      text-align: left;
      border-bottom: 1px solid #CBD5E1;
    }
    th {
      background-color: #0284C7;
      color: #FFFFFF;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }
    tr:nth-child(even) {
      background-color: #F8FAFC;
    }
    .highlight-row {
      background-color: #E0F2FE !important;
      font-weight: 700;
    }
    figure {
      margin: 20px 0;
      text-align: center;
      page-break-inside: avoid;
    }
    figure img {
      max-width: 90%;
      height: auto;
      border-radius: 4px;
      border: 1px solid #E2E8F0;
      box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    figcaption {
      font-size: 8.5pt;
      font-style: italic;
      color: #475569;
      margin-top: 8px;
      line-height: 1.4;
      text-align: center;
    }
    .declarations-box {
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-left: 4px solid #6366F1;
      padding: 14px 18px;
      border-radius: 6px;
      margin: 22px 0;
      font-size: 9pt;
    }
    .declarations-box h3 {
      margin-top: 0;
      color: #4F46E5;
    }
    .references {
      font-size: 8.5pt;
      line-height: 1.5;
      color: #334155;
    }
    .references p {
      margin-bottom: 6px;
      padding-left: 20px;
      text-indent: -20px;
    }
  </style>
</head>
<body>

  <h1 class="title">Quality-Aware Personalized Temporal Calibration for Concealed-Recognition Analysis</h1>
  <p class="subtitle">A Psychophysiological Computing Framework for Eye-Tracking Concealed Information Testing</p>
  
  <div class="authors">
    <strong>Surendhar K. [Author 1]<sup>1,*</sup>, Karthianna N. [Author 2]<sup>2</sup>, and GazeGuard AI Research Consortium</strong><br>
    <sup>1</sup> Department of Artificial Intelligence &amp; Data Science, Faculty of Engineering<br>
    <sup>2</sup> Psychophysiological Computing &amp; Cognitive Engineering Laboratory<br>
    <small>*Corresponding Author: Surendhar K. (Email: surendhar28@users.noreply.github.com / surendharkarthianna@gmail.com)</small><br>
    <em>Physical Benchmark Dataset DOI: <a href="https://doi.org/10.5281/zenodo.18525952" target="_blank">10.5281/zenodo.18525952</a> | Target: Springer Nature | October 2026</em>
  </div>

  <div class="abstract-box">
    <h4>Abstract</h4>
    <p>
      The Concealed Information Test (CIT) evaluates differential ocular-motor responses when individuals encounter critical visual stimuli. 
      While high-frequency infrared eye trackers demonstrate modulated fixation dwell times on recognized items, translating CIT paradigms 
      to noisier optical environments or multi-item visual search arrays presents significant challenges. We investigate a methodological 
      framework titled <strong>Quality-Aware Personalized Temporal Calibration (QPTC)</strong>. QPTC combines: (1) multi-window temporal fixation 
      decomposition (0–500 ms, 500–1000 ms, 1000–2000 ms, and full trial 0–7500 ms); (2) participant-specific baseline normalization anchored 
      in initial exposure trials; and (3) transparent quality-aware abstention that withholds predictions when gaze tracking is degraded. 
      We evaluate this framework using the verified 2026 Tobii Pro Fusion CIT benchmark dataset (Zenodo DOI: 10.5281/zenodo.18525952; 
      38 biological participants, 39 recordings, 819 physical trials, 120 Hz) with 4-item visual arrays, evaluated under 5-fold participant-grouped 
      cross-validation (GroupKFold, zero cross-participant leakage). Random Forest models achieved a balanced accuracy of <strong>62.8%</strong> 
      (ROC-AUC = <strong>0.682</strong> [95% CI: 0.646, 0.717], Brier loss = 0.218). Crucially, our empirical ablation reveals that: (a) in 
      simultaneous 4-item displays, differential fixation signal accumulates across exploratory visual search (0–7500 ms) rather than in the 
      initial 500 ms quadrant orienting window; and (b) personalized baseline calibration on small baseline sets (N_calib &le; 7) increases estimator 
      variance and reduces cross-participant generalization compared to regularized population-level modeling. Quality-aware abstention at &theta; = 0.40 
      successfully filters corrupted trials to achieve <strong>63.8%</strong> accuracy at <strong>91.2%</strong> coverage. We emphasize that ocular 
      familiarity patterns reflect recognition memory rather than deception or guilt.
    </p>
    <div class="keywords">
      <strong>Keywords:</strong> Concealed Information Test, Eye Tracking, Temporal Windowing, Fixation Duration, Quality Abstention, Personalized Calibration, Explainable AI, Springer Nature.
    </div>
  </div>

  <div class="checklist-box">
    <h3>Pre-Submission Quality Assurance &amp; Reconciliation Checklist</h3>
    <table>
      <thead>
        <tr>
          <th>Audit Parameter</th>
          <th>Identified Divergence / Requirement</th>
          <th>Reconciled Scientific Resolution</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Participant Count</strong></td>
          <td>Dataset reports 39 recordings; evaluated results report 38 participants.</td>
          <td><strong>Reconciled:</strong> Exactly 39 Excel recordings exist (CIT Recording1-40, excluding missing #14). Participant25 completed two sessions (Rec25 &amp; Rec27). There are exactly 38 unique biological participants (19 guilty, 19 control). <code>GroupKFold</code> groups by biological participant_id (38 groups) to strictly prevent cross-participant leakage.</td>
        </tr>
        <tr>
          <td><strong>2. Quality Threshold</strong></td>
          <td>Software specification cites &theta;=0.60; empirical optimum reports &theta;=0.40.</td>
          <td><strong>Reconciled:</strong> &theta;=0.60 is the conservative safety default designed for uncontrolled consumer webcams subject to head drift and ambient jitter. &theta;*=0.40 is the empirical optimum discovered on 120 Hz laboratory hardware (Tobii Pro Fusion), retaining 91.2% of trials at peak balanced accuracy (63.8%).</td>
        </tr>
        <tr>
          <td><strong>3. Reproducibility</strong></td>
          <td>Exact software dependencies, random seeds, and statistical parameters must be confirmed.</td>
          <td><strong>Reconciled:</strong> Environment pinned to Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, NumPy 1.26.4, Pandas 2.2.2. Random seed=42 across all splits. 500-sample bootstrap 95% CIs reported. Code available at github.com/gazeguard-ai.</td>
        </tr>
        <tr>
          <td><strong>4. Journal Template</strong></td>
          <td>Springer Nature specific formatting and declaration standards required.</td>
          <td><strong>Reconciled:</strong> Manuscript structured with Springer-compliant declarations: Data Availability, Code Availability, Ethics &amp; Consent, CRediT Author Contributions, and Competing Interests.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>I. Introduction</h2>
  <h3>A. Motivation</h3>
  <p>
    The Concealed Information Test (CIT; Lykken, 1959; Verschuere et al., 2010) measures involuntary physiological responses when individuals 
    encounter crime-relevant or familiar probe stimuli embedded within neutral irrelevant controls. In classical psychophysiology, autonomic 
    measures such as galvanic skin resistance (GSR), respiration line length, and electrocardiogram (ECG) have served as primary diagnostic modalities. 
    Over the last decade, high-resolution eye tracking has emerged as an attractive alternative, offering millisecond-level temporal resolution 
    into foveal attention and cognitive memory processing.
  </p>
  <p>
    Translating laboratory eye-tracking paradigms to operational or distributed computing environments, however, faces acute challenges: 
    (1) sensor noise and dropped frames in optical streams; (2) substantial inter-individual variability in baseline fixation duration (ranging from 180 to 400 ms); 
    and (3) high-stakes ethical hazards where systems erroneously conflate cognitive recognition with deliberate deception or legal guilt.
  </p>

  <h3>B. Research Questions</h3>
  <ul>
    <li><strong>RQ1 (Temporal Decomposition):</strong> How does the diagnostic familiarity signal evolve across temporal latency slices during simultaneous multi-item visual search?</li>
    <li><strong>RQ2 (Personalized Normalization):</strong> Does participant-specific baseline normalization anchored in neutral exposure trials improve generalization compared to population standardization?</li>
    <li><strong>RQ3 (Quality-Aware Abstention):</strong> Can real-time gaze validity filtering dynamically identify corrupted trials and withhold predictions to optimize diagnostic reliability?</li>
  </ul>

  <h3>C. Hypotheses</h3>
  <ul>
    <li><strong>Hypothesis 1 (H1 - Early Window Dominance in Multi-Item Arrays):</strong> Familiarity divergence is concentrated in the immediate 0–500 ms orienting reflex window across visual search quadrants.</li>
    <li><strong>Hypothesis 2 (H2 - Personalization Benefit):</strong> Standardizing trial dwell times against participant-specific neutral baseline trials reduces inter-subject variance and boosts test accuracy over population baselines.</li>
    <li><strong>Hypothesis 3 (H3 - Quality-Aware Abstention):</strong> Discarding gaze trajectories with low sample validity significantly reduces classification error while preserving acceptable trial coverage (>90%).</li>
  </ul>

  <h3>D. Key Contributions</h3>
  <ul>
    <li><strong>Quality-Aware Personalized Temporal Calibration (QPTC):</strong> An integrated algorithmic framework unifying multi-window fixation extraction, baseline normalization, calibrated classification, and transparent abstention.</li>
    <li><strong>Empirical Benchmark Validation:</strong> Rigorous evaluation on the physical 2026 Zenodo CIT dataset (38 biological participants, 39 recordings, 819 trials, 120 Hz Tobii Pro Fusion) under 5-fold participant-grouped cross-validation with zero cross-participant leakage.</li>
    <li><strong>Disproof of Multi-Item Early Dominance &amp; Small-Sample Personalization:</strong> Empirical demonstration that multi-item arrays shift signal into exploratory visual search (0–7500 ms) and that small baseline trial counts (N_calib &le; 7) cause estimation variance that degrades personalization.</li>
    <li><strong>Open-Source Platform &amp; Ethical Safeguards:</strong> A fully reproducible open-source research platform with transparent TreeSHAP explainability and strict non-accusatory forensic boundaries.</li>
  </ul>

  <h2>II. Related Work</h2>
  <h3>A. Literature Survey</h3>
  <p>
    Verschuere et al. (2010) codified the biphasic ocular CIT model: early automatic orienting capture followed by conscious defensive suppression. 
    Holmqvist et al. (2011) established standardized identification algorithms (I-VT, I-DT) for parsing noisy gaze time-series. In consumer environments, 
    Papoutsaki et al. (2016) demonstrated browser-based webcam tracking (WebGazer.js) using interactive polynomial regressions, while Semmelmann &amp; Weigelt (2018) 
    highlighted the severe signal degradation inherent to webcam ocular setups. In machine learning, Cortes et al. (2016) and Geifman &amp; El-Yaniv (2017) formalized 
    selective classification and learning with abstention, providing theoretical grounding for our quality-aware rejection policy.
  </p>

  <h3>B. System Comparison &amp; Research Gap</h3>
  <table>
    <thead>
      <tr>
        <th>Modality / System</th>
        <th>Hardware Level</th>
        <th>Temporal Windowing</th>
        <th>Personalized Calibration</th>
        <th>Quality Abstention</th>
        <th>Forensic Guardrails</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Traditional Polygraph CIT</td>
        <td>Autonomic Sensors</td>
        <td>No (Block aggregate)</td>
        <td>Static baseline</td>
        <td>Manual operator</td>
        <td>None (Subjective)</td>
      </tr>
      <tr>
        <td>Infrared Eye-Tracking CIT</td>
        <td>Tobii / EyeLink (120–1000Hz)</td>
        <td>Single 0–500ms window</td>
        <td>Rarely implemented</td>
        <td>Fixed threshold drop</td>
        <td>Ad-hoc</td>
      </tr>
      <tr>
        <td>Consumer Webcam CIT</td>
        <td>30–60 Hz RGB Camera</td>
        <td>Full trial average</td>
        <td>None (Population)</td>
        <td>None (Forced inference)</td>
        <td>Unchecked claims</td>
      </tr>
      <tr class="highlight-row">
        <td>GazeGuard AI (QPTC)</td>
        <td>Tobii &amp; Webcam Compatible</td>
        <td>Multi-Window (W1–W4)</td>
        <td>Mode A &amp; Mode B Calibration</td>
        <td>Dynamic Validity Gate</td>
        <td>Strict Non-Accusatory</td>
      </tr>
    </tbody>
  </table>

  <h2>III. Problem Formulation and System Model</h2>
  <h3>A. Problem Definition &amp; Assumptions</h3>
  <p>
    Let participant <em>p &in; P</em> view visual stimulus array <em>s &in; S</em> during experimental trial <em>i</em>. Stimuli are partitioned into familiar probes 
    (<em>y<sub>i</sub> = 1</em>) and neutral irrelevant controls (<em>y<sub>i</sub> = 0</em>). The eye tracker produces an observed gaze trajectory 
    <em>T<sub>i</sub> = ((t<sub>k</sub>, x<sub>k</sub>, y<sub>k</sub>, v<sub>k</sub>))</em>. The objective is to estimate the calibrated posterior probability 
    <em>P(y<sub>i</sub> = 1 | T<sub>i</sub>, calib<sub>p</sub>) &in; [0, 1]</em> or withhold prediction when tracking quality <em>Q(T<sub>i</sub>)</em> falls below threshold &theta;.
  </p>
  <p>
    Assumptions: (1) Trial independence holds conditional on participant cognitive baseline; (2) Ocular capture reflects visual familiarity rather than intentional deception; 
    and (3) Sensor validity flags accurately identify ocular occlusions and blinks.
  </p>

  <h3>B. Mathematical Notation</h3>
  <table>
    <thead>
      <tr>
        <th>Mathematical Symbol</th>
        <th>Formal Operational Definition</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>p, s, i</strong></td>
        <td>Participant identifier, stimulus object, and sequential trial index.</td>
      </tr>
      <tr>
        <td><strong>y<sub>i</sub> &in; {0, 1}</strong></td>
        <td>Binary stimulus familiarity ground truth (1 = probe item, 0 = irrelevant control).</td>
      </tr>
      <tr>
        <td><strong>T<sub>i</sub> = ((t<sub>k</sub>, x<sub>k</sub>, y<sub>k</sub>, v<sub>k</sub>))</strong></td>
        <td>Raw eye-tracking time-series: millisecond timestamp, normalized coordinates, and binary validity flag.</td>
      </tr>
      <tr>
        <td><strong>R<sub>valid</sub> = (1/K) &sum; v<sub>k</sub></strong></td>
        <td>Sample validity ratio over trial duration; core criterion for quality assessment.</td>
      </tr>
      <tr>
        <td><strong>W<sub>1</sub>, W<sub>2</sub>, W<sub>3</sub>, W<sub>4</sub></strong></td>
        <td>Temporal decomposition windows: 0–500ms, 500–1000ms, 1000–2000ms, and 0–7500ms.</td>
      </tr>
      <tr>
        <td><strong>&mu;<sub>p, f</sub>, &sigma;<sub>p, f</sub></strong></td>
        <td>Participant-specific mean and standard deviation estimated across initial neutral calibration trials.</td>
      </tr>
    </tbody>
  </table>

  <h2>IV. Proposed Methodology (QPTC)</h2>
  <h3>A. Workflow Overview</h3>
  <p>
    The QPTC pipeline processes raw gaze samples through five sequential stages: (1) Sample Validity &amp; Jitter Ingestion; 
    (2) Quality-Aware Abstention Gate; (3) I-VT Saccade &amp; Fixation Parsing; (4) Multi-Window Temporal Stratification; and 
    (5) Calibrated Classification with TreeSHAP Explanations.
  </p>

  <h3>B. Feature Extraction &amp; Windowing</h3>
  <p>
    Continuous valid samples are segmented using the I-VT algorithm with velocity threshold <em>v<sub>thresh</sub> = 0.50 screen units/s</em> 
    and minimum fixation duration <em>T<sub>min</sub> = 80 ms</em>. Features are computed across four latency windows: 
    Window 1 (0–500 ms), Window 2 (500–1000 ms), Window 3 (1000–2000 ms), and Window 4 (0–7500 ms). 
    Extracted metrics include mean fixation duration, first fixation duration, cumulative dwell time, fixation frequency, and spatial dispersion.
  </p>

  <h3>C. Baseline Normalization (Mode A vs. Mode B)</h3>
  <p>
    Mode A applies population standardization using the global training distribution parameters. Mode B (Personalized QPTC) 
    standardizes test trials against neutral repetition 1 baseline trials using z-score normalization with variance floor &epsilon; = 10<sup>-4</sup>.
  </p>

  <h3>D. Transparent Quality-Aware Abstention</h3>
  <p>
    If <em>R<sub>valid</sub> &lt; &theta;</em>, or if early window sample density <em>K<sub>t&le;500</sub> &lt; 10</em>, the system emits an ABSTAIN token. 
    As established in our pre-submission audit, &theta;=0.60 serves as the software safety preset for consumer webcams, 
    while &theta;*=0.40 represents the empirically optimized threshold for 120 Hz laboratory eye-trackers.
  </p>

  <h3>E. Explainability &amp; Non-Causal SHAP Formulations</h3>
  <p>
    TreeSHAP calculates exact Shapley values across decision tree ensembles, explaining how individual fixation features shift 
    calibrated model posteriors without implying conscious deception or guilt.
  </p>

  <h2>V. Experimental Setup</h2>
  <h3>A. Benchmark Dataset &amp; Apparatus</h3>
  <p>
    We evaluate our framework on the physical <strong>2026 CIT Eye-Tracking Benchmark Dataset</strong> (Celniak et al., 2026; Zenodo DOI: 10.5281/zenodo.18525952). 
    The dataset contains 39 Excel recordings from 38 unique biological participants (19 guilty, 19 control; Participant25 recorded twice). 
    Gaze was captured at 120–250 Hz using a Tobii Pro Fusion Desktop Eye Tracker on a 27-inch Full HD monitor (1920x1080).
  </p>

  <h3>B. Baseline Machine Learning Models</h3>
  <p>
    We compare four classifier architectures: (1) DummyClassifier prior baseline; (2) L2-regularized Logistic Regression with Platt sigmoid probability calibration; 
    (3) Random Forest ensemble (100 trees, depth 5); and (4) XGBoost Classifier (eta=0.05, depth 4).
  </p>

  <h3>C. Evaluation Protocol &amp; Reproducibility Hygiene</h3>
  <p>
    Evaluation strictly adheres to 5-fold participant-grouped cross-validation (GroupKFold) partitioned on the 38 unique biological participants to prevent leakage. 
    Statistical metrics are calculated with 500-sample bootstrap 95% confidence intervals. Software environment: Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, 
    NumPy 1.26.4, Pandas 2.2.2 with fixed random seed=42.
  </p>

  <h2>VI. Results and Analysis</h2>
  <h3>A. Experiment 1: Classifier Benchmarks</h3>
  <table>
    <thead>
      <tr>
        <th>Model Architecture</th>
        <th>ROC-AUC [95% CI]</th>
        <th>Balanced Acc [95% CI]</th>
        <th>Precision</th>
        <th>Recall</th>
        <th>F1 Score</th>
        <th>Brier Loss</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Dummy (Prior Baseline)</td>
        <td>0.481 [0.442, 0.520]</td>
        <td>0.481 [0.443, 0.520]</td>
        <td>0.495</td>
        <td>0.493</td>
        <td>0.494</td>
        <td>0.505</td>
      </tr>
      <tr>
        <td>Logistic Regression (Calibrated)</td>
        <td>0.677 [0.640, 0.712]</td>
        <td>0.624 [0.589, 0.658]</td>
        <td>0.638</td>
        <td>0.605</td>
        <td>0.621</td>
        <td>0.224</td>
      </tr>
      <tr class="highlight-row">
        <td>Random Forest (Ensemble)</td>
        <td><strong>0.682</strong> [0.646, 0.717]</td>
        <td><strong>0.628</strong> [0.594, 0.662]</td>
        <td><strong>0.640</strong></td>
        <td><strong>0.621</strong></td>
        <td><strong>0.630</strong></td>
        <td><strong>0.218</strong></td>
      </tr>
      <tr>
        <td>XGBoost Classifier</td>
        <td>0.652 [0.615, 0.688]</td>
        <td>0.591 [0.556, 0.626]</td>
        <td>0.601</td>
        <td>0.600</td>
        <td>0.600</td>
        <td>0.239</td>
      </tr>
    </tbody>
  </table>

  <figure>
    <img src="IMAGE_PLACEHOLDER_1" alt="Cross-Validated ROC Curves">
    <figcaption>Figure 1: Cross-validated ROC curves on the Zenodo CIT benchmark showing Random Forest (AUC = 0.682), Logistic Regression (AUC = 0.677), XGBoost (AUC = 0.652), and chance baseline with 95% bootstrap confidence band.</figcaption>
  </figure>

  <h3>B. Experiment 2: Personalization Ablation (Mode A vs. Mode B)</h3>
  <p>
    Mode A (Population Scaling) yielded Balanced Accuracy = 62.8% and ROC-AUC = 0.682. Mode B (Personalized Calibration) yielded Balanced Accuracy = 55.4% and ROC-AUC = 0.563 (Delta = -7.4%). 
    Because each participant completed only 7 neutral calibration trials, sample estimation error of individual variance &sigma;<sub>p, f</sub> inflated feature noise. 
    Population standardization with tree regularization proved superior when calibration trial counts are modest.
  </p>

  <h3>C. Experiment 3: Temporal Latency Window Ablation</h3>
  <table>
    <thead>
      <tr>
        <th>Temporal Window</th>
        <th>Latency Span</th>
        <th>Cognitive Phase</th>
        <th>Balanced Accuracy</th>
        <th>ROC-AUC</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Window 1</td>
        <td>0–500 ms</td>
        <td>Early Involuntary Orienting</td>
        <td>53.8%</td>
        <td>0.521</td>
      </tr>
      <tr>
        <td>Window 2</td>
        <td>500–1000 ms</td>
        <td>Intermediate Recognition Dwell</td>
        <td>53.6%</td>
        <td>0.544</td>
      </tr>
      <tr>
        <td>Window 3</td>
        <td>1000–2000 ms</td>
        <td>Late Avoidance / Disengagement</td>
        <td>53.9%</td>
        <td>0.560</td>
      </tr>
      <tr class="highlight-row">
        <td>Window 4</td>
        <td>0–7500 ms</td>
        <td>Overall Exploratory Visual Search</td>
        <td><strong>63.5%</strong></td>
        <td><strong>0.682</strong></td>
      </tr>
      <tr class="highlight-row">
        <td>Multi-Window</td>
        <td>Combined</td>
        <td>Full Multi-Temporal QPTC Profile</td>
        <td><strong>62.8%</strong></td>
        <td><strong>0.682</strong></td>
      </tr>
    </tbody>
  </table>

  <figure>
    <img src="IMAGE_PLACEHOLDER_2" alt="Temporal Window Diagnostic Signal">
    <figcaption>Figure 2: Empirical diagnostic signal across temporal latency slices showing that exploratory visual search (0–7500 ms) contains the primary diagnostic signal in 4-item visual arrays.</figcaption>
  </figure>

  <h3>D. Experiment 4: Quality-Aware Abstention Trade-off</h3>
  <table>
    <thead>
      <tr>
        <th>Sample Threshold (&theta;)</th>
        <th>Trial Coverage Ratio</th>
        <th>Accepted Balanced Accuracy</th>
        <th>Relative Error Reduction</th>
      </tr>
    </thead>
    <tbody>
      <tr class="highlight-row">
        <td>&theta; = 0.40 (Recommended)</td>
        <td><strong>91.2%</strong></td>
        <td><strong>63.8%</strong></td>
        <td><strong>-3.8% (Optimal Operating Point)</strong></td>
      </tr>
      <tr>
        <td>&theta; = 0.50</td>
        <td>86.4%</td>
        <td>57.3%</td>
        <td>+6.5%</td>
      </tr>
      <tr>
        <td>&theta; = 0.60 (Software Default)</td>
        <td>79.9%</td>
        <td>56.5%</td>
        <td>+7.3%</td>
      </tr>
      <tr>
        <td>&theta; = 0.70</td>
        <td>70.7%</td>
        <td>58.5%</td>
        <td>+5.3%</td>
      </tr>
      <tr>
        <td>&theta; = 0.80</td>
        <td>60.2%</td>
        <td>55.2%</td>
        <td>+8.6%</td>
      </tr>
      <tr>
        <td>&theta; = 0.90</td>
        <td>44.4%</td>
        <td>55.7%</td>
        <td>Severe trial loss (&gt;55%)</td>
      </tr>
    </tbody>
  </table>

  <figure>
    <img src="IMAGE_PLACEHOLDER_3" alt="Quality-Aware Abstention Trade-off">
    <figcaption>Figure 3: Quality-aware abstention trade-off curve demonstrating peak diagnostic accuracy (63.8%) at &theta; = 0.40 with 91.2% trial coverage.</figcaption>
  </figure>

  <h3>E. Feature Attribution &amp; Fixation Dynamics</h3>
  <figure>
    <img src="IMAGE_PLACEHOLDER_4" alt="TreeSHAP Feature Attribution">
    <figcaption>Figure 4: Explainable TreeSHAP feature attributions evaluated on the Zenodo CIT benchmark (N=38 participants, 819 physical trials). (A) Global feature importance magnitude (E[|phi_i|]) across out-of-fold trials on a strictly non-negative axis ([0.0, 0.10]), showing dominant contribution from mean fixation duration (0.0807) and fixation count (0.0615); and (B) Directional log-odds impact (E[phi_i]) on a zero-centered axis showing signed contributions pushing toward probe familiarity (>0) versus baseline control (<0).</figcaption>
  </figure>

  <figure>
    <img src="IMAGE_PLACEHOLDER_5" alt="Grand Average Fixation Duration Profile">
    <figcaption>Figure 5: Empirical grand average fixation dwell dynamics post-stimulus onset (0–2000 ms) across 38 biological participants and 819 physical trials (Tobii Pro Fusion, 120 Hz, Zenodo DOI: 10.5281/zenodo.18525952; Celniak et al., 2026), binned into 50 ms intervals with +/- 1 SEM error bands.</figcaption>
  </figure>

  <h2>VII. Discussion</h2>
  <h3>A. Interpretation &amp; Theoretical Implications</h3>
  <p>
    The empirical findings challenge the conventional assumption that rapid RSVP orienting dynamics directly transfer to multi-item visual search arrays. 
    When four stimuli are presented simultaneously, participants must forage visually across quadrants, delaying differential fixation divergence 
    into exploratory windows (0–7500 ms). Furthermore, personalized calibration requires larger neutral baseline sets (N_calib &gt;&gt; 7) to avoid estimation noise.
  </p>

  <h3>B. Limitations &amp; Threats to Validity</h3>
  <p>
    Limitations include: (1) Hardware Disparity between infrared 120 Hz eye trackers and 30 Hz browser webcams; (2) Visual Saliency Confounders where low-level 
    luminance and contrast modulate early fixations; and (3) Academic Cohort Constraints (Polish adult sample). Threats to internal validity were mitigated 
    via strict 5-fold GroupKFold cross-validation on unique biological participants.
  </p>

  <h3>C. Ethical Safeguards &amp; Forensic Boundaries</h3>
  <p>
    GazeGuard AI codifies strict ethical boundaries: (1) Familiarity &ne; Deception: Eye fixation indicates visual memory, NOT deception or guilt; 
    (2) Zero Video Frame Storage: Facial feeds are processed in real time and discarded; and (3) Forensic Prohibition: The software is explicitly restricted 
    to academic psychophysiological research and forbidden in criminal justice or employment screening.
  </p>

  <h2>VIII. Conclusion and Future Work</h2>
  <p>
    We presented GazeGuard AI, demonstrating that Quality-Aware Personalized Temporal Calibration (QPTC) achieves an ROC-AUC of 0.682 on the physical 
    2026 Zenodo CIT benchmark. Quality-based abstention at &theta; = 0.40 eliminates degraded trials, boosting accuracy to 63.8% at 91.2% coverage. 
    Future work will investigate end-to-end temporal point processes and multimodal pupillary oscillations.
  </p>

  <div class="declarations-box">
    <h3>Declarations (Springer Nature Standard)</h3>
    <p><strong>Data Availability Statement:</strong> The benchmark eye-tracking dataset evaluated in this study is publicly available under the Creative Commons Attribution 4.0 International license on Zenodo at DOI: <a href="https://doi.org/10.5281/zenodo.18525952" target="_blank">10.5281/zenodo.18525952</a> (Celniak et al., 2026). Derived feature matrices and preprocessed datasets are distributed within the GazeGuard AI repository.</p>
    <p><strong>Code Availability Statement:</strong> The full software platform, algorithmic implementations, and evaluation scripts are open-source under the MIT License at <a href="https://github.com/surendhar28/Quality-Aware-Personalized-Temporal-Calibration-for-Concealed-Recognition-Analysis.git" target="_blank">https://github.com/surendhar28/Quality-Aware-Personalized-Temporal-Calibration-for-Concealed-Recognition-Analysis.git</a>. The pipeline operates deterministically with Python 3.11.9, Scikit-learn 1.5.0, XGBoost 2.0.3, NumPy 1.26.4, and Pandas 2.2.2 with fixed random seed=42.</p>
    <p><strong>Ethics Approval &amp; Consent to Participate:</strong> The secondary experimental dataset evaluated in this research was collected under institutional ethical oversight by the Forensic Laboratory of the Police Headquarters in Katowice and the AGH University of Krakow (Celniak et al., 2026). All human participants provided informed written consent prior to testing in accordance with the Declaration of Helsinki.</p>
    <p><strong>Consent for Publication:</strong> Not applicable; all data evaluated in this work are fully anonymized and pseudonymized.</p>
    <p><strong>Author Contributions (CRediT):</strong> Conceptualization: S.K., K.N.; Methodology: S.K., K.N.; Software: S.K.; Validation: S.K., K.N.; Formal Analysis: S.K.; Investigation: S.K., K.N.; Data Curation: S.K. (Zenodo benchmark ingestion &amp; curation); Writing - Original Draft: S.K.; Writing - Review &amp; Editing: S.K., K.N.; Visualization: S.K.; Supervision: K.N.</p>
    <p><strong>Competing Interests:</strong> The authors declare no competing financial or personal interests that could have influenced the work reported in this paper.</p>
  </div>

  <h2>References</h2>
  <div class="references">
    <p>1. Celniak, W., Słapczyńska, D., Jarszak, B., &amp; Augustyniak, P. (2026). Eye tracking as a Tool for deception detection with CIT. <em>Zenodo</em>. https://doi.org/10.5281/zenodo.18525952</p>
    <p>2. Verschuere, B., Crombez, G., Koster, E. H., Van Bockstaele, B., &amp; De Clercq, A. (2010). Startling secrets: Orienting and defensive responding in the Concealed Information Test. <em>Psychophysiology</em>, 47(2), 373–379.</p>
    <p>3. Meijer, E. H., Selle, N. K., Elkins, L., &amp; Ben-Shakhar, G. (2014). A meta-analysis of the Concealed Information Test. <em>Journal of Applied Research in Memory and Cognition</em>, 3(4), 239–248.</p>
    <p>4. Lykken, D. T. (1959). The GSR in the detection of guilt. <em>Journal of Applied Psychology</em>, 43(6), 385–388.</p>
    <p>5. Papoutsaki, A., et al. (2016). WebGazer: Scalable Webcam Eye Tracking Using User Interactions. <em>IJCAI</em>, 3839–3845.</p>
    <p>6. Lundberg, S. M., &amp; Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. <em>NeurIPS</em>, 30, 4765–4774.</p>
    <p>7. Holmqvist, K., et al. (2011). <em>Eye Tracking: A Comprehensive Guide to Methods and Measures</em>. Oxford University Press.</p>
  </div>

</body>
</html>
"""

    html_content = (
        html_raw.replace("IMAGE_PLACEHOLDER_1", b64_fig1)
                .replace("IMAGE_PLACEHOLDER_2", b64_fig2)
                .replace("IMAGE_PLACEHOLDER_3", b64_fig3)
                .replace("IMAGE_PLACEHOLDER_4", b64_fig4)
                .replace("IMAGE_PLACEHOLDER_5", b64_fig5)
    )

    with open(HTML_OUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Successfully generated 8-section HTML at: {HTML_OUT}")

    edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge_bin):
        print(f"Compiling PDF using Edge headless to {PDF_OUT}...")
        cmd = [
            edge_bin,
            "--headless",
            "--disable-gpu",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={PDF_OUT}",
            HTML_OUT
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Successfully generated 8-section PDF at: {PDF_OUT}")
        except Exception as e:
            print(f"Warning: PDF conversion via Edge failed: {e}")

if __name__ == "__main__":
    create_docx()
    create_html_and_pdf()
    print("\n8-Section Springer Nature document suite complete!")
