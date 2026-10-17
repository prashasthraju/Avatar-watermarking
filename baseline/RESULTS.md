# Baseline results: fingerprinting + post-hoc watermarking on LivePortrait renders

All numbers come from the scripts in `scripts/`; raw outputs are in `stage*/`. A combined machine-readable file is `results.json`.
Hardware: one local GPU. Dates: 2026-10-15/16.

## What was built and run

| Stage | Question | Data | Script(s) |
|---|---|---|---|
| 1 | How well does the AVAPrintDB landmark-graph model verify the *driver* of a LivePortrait render? | AVAPrintDB TEST, released landmarks, LIVE-trained graph checkpoints | `run_stage1.sh`, `evaluate_lowmem.py`, `analyze_stage1.py` |
| 2 | Does a post-hoc VideoSeal-1.0 (256-bit) watermark survive delivery + attacks on LivePortrait renders, and at what false-positive rate? | 150 subset videos × 14 attacks, watermarked + unwatermarked control | `gen_watermarked.py`, `stage2_robustness.py`, `analyze_stage2.py` |
| 2b | Can per-segment keyed payloads (HMAC per 16-frame segment) detect temporal edits? | 50 calibration + 100 test videos × 6 cases | `stage2b_temporal_v2.py`, `analyze_stage2b_v2.py` |
| 3 | Does watermarking erode the fingerprint? | 648 subset videos, 4 landmark conditions, same pairs | `run_stage3.sh`, `analyze_stage3.py` |

Not done (out of scope for this baseline, listed under Next steps): LoRA/decoder-integrated watermark, running LivePortrait ourselves, the live-latent setting, Stage-4 fusion verifier. No manifest/C2PA component was built.

### Protocol notes that affect how to read the numbers
- **Verification task.** Enrolment = self-reenactment X–X. Test = X–X (genuine) or Y–X (cross-reenactment impostor, same target X). Score = cosine similarity of mean window embeddings (70-frame windows, stride 35).
- **Pair dropping.** The official AVAPrintDB evaluation drops any pair where either video has < 70 frames. CREMA-D LIVE→LIVE therefore uses 160,545 of 371,952 pairs. We kept the official behaviour.
- **Memory fix only.** `evaluate_lowmem.py` is the official `evaluate.py` with the window-embedding chunk size reduced (1024 → 16) to fit GPU memory; the maths is unchanged.
- **Subset (Stages 2/3).** `make_subset.py`, `Random(0)`: 3 CREMA-D TEST targets **C1003, C1061, C1072**, all 648 LIVE videos with those targets, 46,656 pairs (15,552 genuine / 31,104 impostor) before length filtering. List in `subset/subset.json`.
- **Delivery codec.** "Delivered" = H.264 libx264 CRF 23, yuv420p. Watermarked (`videos/wm`) and control (`videos/ctrl`) videos go through the identical encode; the only difference is the watermark.

---

## Stage 1 — biometric baseline (AVAPrintDB graph model)

95% CIs: cluster bootstrap over test videos (pairs sharing a test video are correlated).

| Dataset | Train → Test generator | Pairs used | AUC (95% CI) | EER | TAR@FAR 1e-1 | 1e-2 | 1e-3 | Paper AUC |
|---|---|---|---|---|---|---|---|---|
| RAVDESS | LIVE → LIVE | 79,200 | **0.757** (0.739–0.777) | 0.306 | 0.422 | 0.129 | 0.041 | 76.5 |
| CREMA-D | LIVE → LIVE | 160,545 | **0.923** (0.917–0.928) | 0.160 | 0.759 | 0.373 | 0.155 | 90.8 |
| CREMA-D | LIVE → GAGA | 226,777 | **0.838** (0.830–0.848) | 0.240 | 0.565 | 0.202 | 0.063 | 76.5 |
| CREMA-D | LIVE → HUNY | 226,777 | **0.809** (0.798–0.819) | 0.268 | 0.484 | 0.154 | 0.046 | 73.9 |

- RAVDESS reproduces the paper (75.7 vs 76.5). CREMA-D in-domain is ~1.5 AUC points above the paper. We did not track down why (candidates: different pair filtering, checkpoint version).
- **Generator shift.** Paper values are from the AVAPrintDB README, CREMA-D graph model: 90.8 → 76.5 (GAGA, Δ −14.3) and 90.8 → 73.9 (HUNY, Δ −16.9).
  - Our cross-generator AUCs are about **7 points higher** than the paper's (83.8 vs 76.5; 80.9 vs 73.9). Our drops from in-domain are smaller: −8.5 and −11.4.
  - The paper's direction holds: HUNY is harder than GAGA. The size of the drop does not reproduce.
  - We have not explained this. Candidates:
    - The < 70-frame pair filter keeps different pair sets per generator (GAGA/HUNY keep 226,777 pairs vs 160,545 for LIVE).
    - The paper may use a different pair protocol or checkpoint for the cross-generator table.
  - Treat our cross-generator numbers as an upper bound until the protocol is matched.
- **The operating-point story matters more than AUC.** At FAR 1e-3, only 15% (CREMA-D) and 4% (RAVDESS) of genuine drivers are accepted. As a stand-alone authentication signal, landmark fingerprinting is weak at strict FARs. This is the motivation for adding a cryptographic or watermark signal.

---

## Stage 2 — VideoSeal-1.0 robustness on LivePortrait renders

Setup: VideoSeal 1.0, 256-bit message (one random message per video, seeded), default video embedding (chunk 32, step 4, JND attenuation). Decoding averages the per-frame bit logits over all frames, then thresholds at 0. Each attack is applied with the same randomness to the watermarked video and to its unwatermarked control. The control decodes are the **null distribution**.

### Imperceptibility (all 648 videos)

| Comparison | PSNR dB (mean ± sd, min) | SSIM | LPIPS |
|---|---|---|---|
| watermarked vs original, before codec | 50.4 ± 0.9 (min 49.0) | 0.9968 | — |
| delivered watermarked vs delivered control (watermark only) | 43.4 ± 0.7 (min 41.9) | 0.9828 | 0.0046 |
| delivered control vs original (codec only) | 41.9 ± 0.3 | — | — |
| delivered watermarked vs original (codec + watermark) | 41.4 ± 0.3 | — | — |

After delivery, the watermark costs about 0.5 dB PSNR relative to the codec alone.

### Detection thresholds (k = matching bits out of 256)

| Rule | k ≥ |
|---|---|
| Binomial(256, 0.5), FPR 1e-3 | 154 |
| Binomial, FPR 1e-6 | 167 |
| Binomial, FPR 1e-9 | 176 |
| Empirical: max over 2,100 null decodes + 1 | 153 |

- The null max (152/256 = 0.594) fits the binomial model.
- The 2,100 null decodes are 150 videos × 14 attacks, so they are correlated. Empirically they only support roughly the 1e-3 level.
- **The 1e-6 / 1e-9 thresholds rely on the binomial (independent fair-coin bits) assumption.** We have not verified it at those rates.
- Observed false positives at the 1e-6 threshold: 0 / 2,100.

### Robustness (n = 150 videos per row)

| Attack | Bit acc. mean | p10 | min | Null mean | TPR @ FPR 1e-6 | TPR @ FPR 1e-9 |
|---|---|---|---|---|---|---|
| none (delivered, CRF 23) | 0.894 | 0.828 | 0.805 | 0.505 | **1.00** | **1.00** |
| H.264 CRF 30 | 0.739 | 0.668 | 0.613 | 0.499 | 0.95 | 0.81 |
| H.264 CRF 40 | 0.550 | 0.504 | 0.477 | 0.502 | **0.01** | 0.00 |
| H.265 CRF 28 | 0.778 | 0.715 | 0.680 | 0.506 | 1.00 | 0.99 |
| resize 0.5× | 0.732 | 0.664 | 0.621 | 0.501 | 0.92 | 0.71 |
| center crop 80% | 0.763 | 0.672 | 0.606 | 0.489 | 0.97 | 0.85 |
| Gaussian noise σ = 0.05 | 0.786 | 0.731 | 0.684 | 0.490 | 1.00 | 0.99 |
| Gaussian noise σ = 0.15 | 0.607 | 0.566 | 0.516 | 0.502 | **0.08** | 0.01 |
| brightness +0.2 | 0.847 | 0.773 | 0.738 | 0.510 | 1.00 | 1.00 |
| drop 50% of frames | 0.842 | 0.766 | 0.734 | 0.501 | 1.00 | 1.00 |
| shuffle frames | 0.829 | 0.746 | 0.711 | 0.507 | 1.00 | 1.00 |
| keep first 25% of frames | 0.837 | 0.765 | 0.723 | 0.500 | 1.00 | 1.00 |
| fps 29 → 15 | 0.856 | 0.781 | 0.758 | 0.501 | 1.00 | 1.00 |
| crop 80% + brightness + CRF 30 | 0.616 | 0.504 | 0.453 | 0.498 | **0.32** | 0.28 |

**Findings**
1. **Detection ("this video carries our watermark") is reliable for delivery and moderate attacks.** It fails under heavy compression (CRF 40), strong noise (σ = 0.15) and the combined crop + brightness + CRF 30 chain.
2. **The full 256-bit payload is never recovered exactly**, not even on the plain delivered video (0/150; mean bit accuracy 0.894). Detection works because the verifier *knows* the expected message and only checks agreement. A design that must *read an unknown ID* out of the watermark (e.g. a manifest pointer) needs error-correcting codes and far fewer effective bits than 256. This is a concrete constraint for the research plan.
3. **A single video-level message is blind to temporal edits.** Dropping half the frames, shuffling them, or keeping only the first 25% all still decode as 100% "authentic". This motivates Stage 2b.
4. Population numbers: an earlier one-video smoke test gave 0.98 bit accuracy after CRF 23. That video was not representative; use the 150-video figures above.

---

## Stage 2b — per-segment keyed payloads for temporal integrity

> **Simulation.** This is an offline verifier script, not a deployed system. It uses a hard-coded demo key (`btp-demo-key-not-secret`), and the verifier is handed `video_id` and K out of band (in a real system these would come from a signed manifest, which was not built).

**Idea under test** (an untested configuration from the research report): each 16-frame segment s carries its own 256-bit payload `m_s = HMAC-SHA256(key, video_id | s)`. A verifier that knows the key, `video_id` and the expected segment count K matches every frame against the K expected messages. It then checks that segments appear complete and in order, with no foreign content.

**Setup (v2, `stage2b_temporal_v2.py` + `analyze_stage2b_v2.py`)**
- Tamper cases: drop one segment, swap two segments, insert a validly watermarked segment from another video, shuffle frames.
- Every tamper case is re-encoded once more at CRF 23. The false-alarm control is the clean video given the same extra re-encode (`none_reencode`), and is reported next to the once-encoded clean video (`none`).
- Per-frame logits are saved, so verifier rules are fit offline.
- **Calibration and test are disjoint:** 50 calibration videos, 100 test videos.
- Rule parameters were picked on calibration: smoothing window, per-frame confidence threshold, minimum run length, minimum length of a foreign stretch, and whether the short trailing segment is exempt. The goal was ≤ 2% false alarms on both clean cases.
- **No setting met the 2% budget on `none_reencode`.** The minimum-false-alarm setting was frozen: 8-frame smoothing, confidence ≥ 0.58, runs ≥ 4 frames, foreign stretch ≥ 12 frames, trailing partial segment exempt.

**Test results (n = 100 videos per row)**

| Case | Flagged | ORDER | MISSING | FOREIGN |
|---|---|---|---|---|
| clean, delivered once (`none`) | **0.00** | 0.00 | 0.00 | 0.00 |
| clean + one extra re-encode (`none_reencode`) | **0.30** | 0.21 | 0.18 | 0.01 |
| drop one segment | 0.98 | 0.21 | 0.98 | 0.00 |
| swap two segments | 0.88 | 0.85 | 0.15 | 0.01 |
| insert foreign segment | 0.90 | 0.24 | 0.20 | 0.80 |
| shuffle frames | 1.00 | 0.98 | 0.86 | 0.05 |

**Findings**
1. **Only the FOREIGN criterion is reliable once re-encoding is involved.** Every tamper case had the extra re-encode, so the codec-matched control is `none_reencode`. Each tamper's own criterion against that control:
   - FOREIGN on insert: **80%** vs 1% on re-encoded clean. Specific.
   - MISSING on drop: 98% vs 18%.
   - ORDER on swap: 85% vs 21%.

   ORDER and MISSING detect their tampers, but they are only weakly specific: about 1 in 5 benign re-encodes trips each of them.
2. **Overall false alarms are 30% after one benign re-encode.** The once-encoded clean video gives 0%, but 88–100% detection at 0% false alarms was **not** measured, because the tampered cases were all re-encoded.
   - As configured (16-frame segments, 256-bit payloads), the verifier cannot reliably tell "re-encoded" from "reordered or dropped".
   - Single-message VideoSeal (Stage 2) cannot see any of these edits at all.
3. **Diagnosis: the codec, not the embedder** (separate check on n = 4 videos):
   - Raw embedded frames: every segment decodes perfectly (per-frame agreement 1.00).
   - After a standard CRF 23 encode: the first segment stays strong (≈ 0.95), later segments fall to ≈ 0.80, and the short last segment to 0.62–0.73. On 2 of the 4 videos, that last segment's frames match the *previous* segment's message better than their own.
   - After an **all-intra** CRF 23 encode (`-g 1`): every segment sits at a uniform ≈ 0.82, and per-frame segment assignment is **100% correct for every segment, including the short last one, on all 4 videos**.
   - So standard GOP encoding causes the failure and all-intra encoding does not. The likely mechanism is inter-frame prediction carrying one segment's watermark into the next segment's frames, compounding with each further encode.
4. **Security gap introduced by the fix.** Exempting the short trailing segment is what brings the clean false-alarm rate to 0%. It also means truncating the last < 16 frames is not detected.
5. **What would likely fix it** (not tested):
   - **First:** put segment boundaries on codec keyframes (force an IDR frame at each segment start). The all-intra check above is direct evidence for this.
   - Longer segments, plus ECC or fewer bits per segment.
   - Sequence alignment (DP/Viterbi over the expected monotone segment order) instead of per-frame argmax.
   - Segment messages chained to the previous one.

The first run (`stage2b_temporal.py`, `temporal_raw.csv`) is **superseded**. It had no re-encoded clean control, and it flagged 73% of clean videos, mainly through the trailing-segment failure above.

---

## Stage 3 — does watermarking erode fingerprinting?

Four landmark sets for the same 648 subset videos, all scored with the CREMA-D LIVE graph checkpoint on the **same 26,759 pairs** (9,830 genuine / 16,929 impostor), i.e. the subset pairs that survive the < 70-frame filter in every condition.

| Condition | Landmarks from | AUC | EER | TAR@FAR 1e-1 | 1e-2 | 1e-3 |
|---|---|---|---|---|---|---|
| (a) released | AVAPrintDB released `.npy` | 0.9004 | 0.1828 | 0.704 | 0.287 | 0.096 |
| (b) re-extract | our MediaPipe run on original mp4 | 0.9016 | 0.1828 | 0.708 | 0.284 | 0.098 |
| (c) control | original re-encoded CRF 23, no watermark | 0.8976 | 0.1863 | 0.693 | 0.285 | 0.099 |
| (d) watermarked | VideoSeal + CRF 23 | 0.9000 | 0.1847 | 0.700 | 0.296 | 0.101 |

Deltas use a cluster bootstrap over test videos (ΔAUC: 1,000 resamples; ΔEER: 300). "Flips" = pairs whose accept/reject decision changes at the reference condition's EER threshold.

| Effect | ΔAUC (95% CI) | ΔEER (95% CI) | Score Pearson r | Mean \|Δscore\| | Flips |
|---|---|---|---|---|---|
| **Watermark (d − c)** | **+0.0024** (+0.0008, +0.0039) | −0.0015 (−0.0045, +0.0007) | 0.9984 | 0.0017 | 1.8% |
| Re-encode (c − b) | −0.0039 (−0.0056, −0.0024) | +0.0035 (+0.0009, +0.0057) | 0.9984 | 0.0017 | 1.7% |
| MediaPipe drift (b − a) | +0.0011 (+0.0002, +0.0021) | −0.0000 (−0.0023, +0.0014) | 0.9994 | 0.0010 | 0.9% |
| Total vs released (d − a) | −0.0004 (−0.0024, +0.0012) | +0.0019 (−0.0017, +0.0036) | 0.9979 | 0.0020 | 2.0% |

**Finding:** VideoSeal does **not** erode landmark-based fingerprinting.
- The watermark effect is tiny, and nominally slightly positive (the CI excludes 0 on AUC, but it is +0.2 points).
- It is smaller than the effect of the CRF 23 re-encode itself.
- Net of everything, the deployed pipeline (d) matches the released-landmark baseline (a); the CI includes 0.
- About 2% of decisions flip near the EER threshold. This is the same order as codec-only flips, so it is noise-level.

Caveats:
- Only 3 targets, so the CIs are over test videos within those targets and do not cover target-to-target variation.
- Landmark (graph) model only. Appearance-based fingerprinting (DINO/CLIP features) is more likely to be affected by a pixel-domain watermark and was not tested.
- LivePortrait only.
- Post-hoc watermark only; a decoder-integrated (LoRA) watermark changes the render itself and must be re-tested.

---

## Disk / housekeeping
- Baseline folder ≈ 1 GB, including `.venv_vs` (284 MB, VideoSeal installed in isolation so the main conda env's protobuf/opencv are untouched) and `ckpts` (218 MB).
- The runs shared the GPU with a separate `avafp.train_feat_diff` training job. That affected run time, not results.
- Free space on `/home` was 5.4 GB at the time of writing, down from ~18 GB earlier. The drop is not from this folder.

## Next steps
0. **Stage 2b re-run with an IDR frame forced at every segment boundary**, then re-calibrate. This is the cheapest high-value follow-up.
1. **Decoder-integrated watermark** (LoRA fine-tune of the LivePortrait decoder, as in the plan), then re-run Stages 2 and 3 against it.
2. **Run LivePortrait ourselves** so watermarking happens at render time and the live-latent setting can be tested.
3. **Appearance fingerprinting** (DINO/CLIP feature models from AVAPrintDB) under conditions (a)–(d).
4. **More targets** (all CREMA-D TEST targets) and RAVDESS, so the Stage 3 CIs cover target variation.
5. **Payload design.** Use ECC with a short ID if the payload must be read; keep keyed matching if the verifier always knows the expected ID.
6. **Stronger attacks**: regeneration/diffusion purification, re-rendering through another reenactment model, screen capture.
7. **Stage 4 fusion verifier**: combine watermark presence, segment integrity and fingerprint score, and report the joint operating points. Any manifest/verifier demo must be labelled a simulation.
