# GazeGuard AI — Measurement Limitations, Confounders, and Generalizability

## 1. Hardware and Measurement Differences

### Dedicated Hardware vs. Webcam Gaze Estimation
| Parameter | Tobii Pro Fusion (Primary Dataset) | Browser Webcam (WebGazer / MediaPipe) |
|---|---|---|
| **Sampling Rate** | 120–250 Hz | 30–60 Hz (hardware and browser throttled) |
| **Spatial Precision** | ~0.4° – 0.8° visual angle (~15–30 px) | ~1.5° – 3.5° visual angle (~60–140 px) |
| **Illumination Robustness** | Infrared illumination (independent of room lighting) | Visible light RGB (highly sensitive to glare/shadows) |
| **Head Motion Tolerance** | Large 3D tracking box with parallax compensation | Sensitive to head movement, yaw, pitch, and roll |
| **Timestamp Precision** | Sub-millisecond hardware clock | Browser event-loop timing subject to thread jitter |

> [!WARNING]
> Models trained strictly on dedicated infrared hardware data cannot be assumed to transfer to webcam measurements without domain adaptation and degradation modeling.

## 2. Psychophysiological Confounders
1. **Visual Saliency vs. Cognitive Familiarity**: A neutral control stimulus that has higher visual contrast, brighter colors, or complex textures can attract early fixations regardless of memory status.
2. **Fatigue and Vigilance Decrement**: Prolonged CIT trial batteries induce saccadic slowing, increased blink rates, and reduced fixation durations as cognitive stamina decreases.
3. **Anxiety and Novelty Effects**: Being tested can elicit generalized hyper-vigilance or visual avoidance, altering baseline fixation durations.

## 3. Generalizability Boundaries
- The primary dataset reflects an undergraduate and staff cohort (N=39) in Poland performing a standardized mock theft task.
- Results cannot be assumed to generalize across varied age demographics, neurological conditions (e.g., nystagmus, strabismus), corrective eyewear (thick lenses, bifocals), or non-laboratory emotional contexts.
