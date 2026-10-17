# Research log — key findings from each research thread

**Topic:** Watermarking and identity verification for cross-reenactment (talking-head avatars)
**Date:** 2026-10-16
**Final report:** `../reports/Watermarking for cross reenactment verification.md`
**Full notes (≈27,600 words total):** `../research_notes/Watermarking for cross reenactment verification/`

Five research threads ran in parallel, followed by one report-writing pass. This log records the most important findings each thread reported, as it reported them. Numbers marked *[secondary]* came from summaries, not the paper itself; *[unverified]* means the thread could not confirm it.

---

## Thread 1 — Driver biometrics / avatar fingerprinting

**Notes file:** `driver_biometrics.md` (≈5,000 words)

### Two lineages of work, 7 methods total

**Lineage A — avatar fingerprinting** (rendered video or landmarks; compares against enrolled reference videos of the claimed driver):

| Method | Approach | Result | Code |
|---|---|---|---|
| Prashnani et al., ECCV 2024 (NVIDIA), arXiv 2305.03713 | 126 landmarks → pairwise distances → temporal CNN | AUC 0.85; 0.83 unseen generators | Never released |
| Pedrouzo-Rodriguez et al., IJCB 2025, arXiv 2508.00748 | Graph network on MediaPipe landmarks, GAGAvatar only | AUC 69.9–83.3% | BiDAlab/GAGAvatar-Benchmark |
| AVAPrintDB, Pattern Recognition 179:114834 (2026), arXiv 2603.26934 | Benchmarks landmark GCN, DINOv2, CLIP, fusion | In-domain AUC 72–95%; generator shift up to −20.4 pts; dataset shift up to −28.9 pts | Public (GitHub + Zenodo) |
| Chapariniya et al., FG 2026 TrustFA *workshop*, arXiv 2604.23247 | Raw 128×128 grayscale frames, micro-expression backbone, inter-frame feature differencing | AUC 0.877 vs 0.853 baseline on NVFAIR; cross-generator 0.833–0.872 | Several tables contradict each other |
| Gerstner, arXiv 2603.20165 (audio) | Speaker-verification embeddings vs enrolled voice | ROC curves only, no AUC/EER | — |

- Systems trained on LivePortrait transfer worst; the landmark system is the most generator-robust.

**Lineage B — puppeteering detection** (transmitted pose-expression latent in AI video calls; no enrollment):
- **Vahdati et al., CVPRW 2023** (Media Forensics workshop), pp. 983–992. Its own numbers were not verified (PDF blocked).
- **Unmasking Puppeteers, NeurIPS 2025, arXiv 2510.03548** (v1 titled "…Disarm…"):
  - compares the live latent against the reference portrait sent at call setup;
  - AUC 0.968 (text says 0.971, Table 1 says 0.968) vs 0.944 for Vahdati; 0.925 on unseen datasets;
  - ~75 FPS on RTX 3090; generators: MCNet, 3DFaceShop, SDFR, EMOPortraits, LivePortrait;
  - repo is a README-only placeholder, PolyForm Noncommercial license.

### Datasets
- **NVFAIR:**
  - 161 identities (46 video-call subjects + RAVDESS + CREMA-D) and >650,000 synthetic videos from face-vid2vid, LIA and TPS.
  - LIA and TPS are released for the test set only.
  - Access is by NVIDIA request form; subjects can revoke their data; no explicit license.
- **AVAPrintDB:**
  - 109 identities from CREMA-D and RAVDESS; 66,069 videos across GAGAvatar, LivePortrait and HunyuanPortrait (22,680 self-reenactments, 43,389 cross-reenactments).
  - Trial lists and checkpoints are on GitHub and Zenodo (DOI 10.5281/zenodo.20548978).
  - No separate database license is stated.

### Failure modes
- Changes of generator or source dataset.
- Drivers with little facial expression, and generators that drop identifying expressions.
- Extreme yaw (performance peaks at a ±18° filter).
- Occlusion, poor lighting and motion blur.
- Performance gaps by age and ethnicity.

### Key gaps
- **No paper reports EER**; AUC only. Protocols differ, so results are not comparable across papers.
- **No adversarial testing** (mimicry, motion style transfer). AVAPrintDB and Chapariniya both say so explicitly.
- **No paper combines driver verification with watermarking or provenance.** Prashnani frames its method as an alternative to watermarking. The only joint idea found is in USPTO patents (blockchain hashes + watermark, no driver biometrics). Caveat: no Google Scholar "cited by" sweep was possible.

---

## Thread 2 — Generation-time and post-hoc video watermarking

**Notes file:** `video_watermarking.md` (≈6,500 words)

### Four families, each tied to a generator architecture
| Family | Methods | Requires |
|---|---|---|
| Post-hoc pixel | VideoSeal, LoT-Pass/I2VWM (32 bits; arXiv 2509.17773, now titled "LoT-Pass", ECCV 2026 per its comments field), WaTeRFlow (abstract only) | Any video |
| Decoder fine-tuning | Stable Signature (48 bits), VidSig, SPDMark | A learned decoder you control |
| Initial-noise | Tree-Ring, Gaussian Shading, VideoShield, VideoMark, SIGMark | Diffusion sampler + inversion at verification |
| Motion-latent | MoSign (arXiv 2609.29603) | Motion VAE |

### Key method facts
- **VideoSeal:** 96 bits (now "legacy"; v1.0 = 256 bits). About 0.42 s GPU per second of video. On SA-V: 0.85 bit accuracy under H.264/H.265, 0.73 under combined attacks.
- **SPDMark (CVPR 2026 per its arXiv comments field):**
  - LoRA in the VAE decoder; 28 bits/frame from HMAC-derived per-frame messages.
  - Bipartite matching recovers frame order: drop/insert localization F1 0.995–0.999; swap reordering 1.000.
  - ~8 GPU-hours on one A6000.
- **SIGMark (ICLR 2026 per its arXiv comments field):** 512 bits per frame group; recovers group order via optical flow.
- **MoSign:** keyed MAC in the motion latent of body/VR motion (not faces). A generic pose estimator strips the mark; only a keyed reader recovers it (0.96 on a projected 2D channel, 0.81 through a full render-to-video loop).
- **Frame-specific messages / tamper localization:** SPDMark, VideoMark, SIGMark, VideoShield. **VideoSeal and VidSig repeat one message per frame**, so they survive frame edits but cannot detect them.

### Talking-head specific
- **No paper has watermarked a talking-head or face-reenactment generator** → open gap, possible novelty.
- **Source-portrait marks:** LampMark drops to ~73–75% bit accuracy after GAN reenactment vs 92–99.9% after face swap. Exact payload is lost, but presence detection probably still works (thread's own binomial estimate: p ≈ 1e-8 at 128 bits).
- **LivePortrait pastes the animated face back onto the source image by default** (`flag_pasteback=True`), so a source mark likely survives in the background. That proves only which photo was used, not genuine vs puppeteered.

### Recommendation for LivePortrait
- **Primary:** SPDMark-style fine-tuning of the SPADE decoder (rest frozen, keyed per-frame message). Fits the 12.8 ms/frame pipeline. The training-cost estimate is by analogy only.
- **Baseline:** post-hoc VideoSeal (cheap, but no frame-order or tamper checks).
- **Not recommended:** perturbing implicit keypoints (low capacity, exposed to MoSign's recapture problem).
- **Not applicable:** noise methods (LivePortrait and GAGAvatar have no noise latent). GAGAvatar → decoder approach on its neural renderer.
- **HunyuanPortrait** is built on SVD, so SPDMark/VideoShield/VidSig SVD results transfer most directly. But verification must invert with conditioning the verifier may not have, which is untested.
- **Core limit:** with open weights, anyone can load the original decoder or skip the post-hoc step. An in-model mark protects a specific deployed build, not the open model.

### Cross-paper conflicts (reported, not resolved)
- VideoSeal's clean accuracy is measured as ~0.999 (SPDMark), 0.975/0.979 (VidSig) and 0.964/0.982 (VideoMark). VideoMark also measures it at 0.565 under resolution compression.
- VideoMark scores ~1.000 in its own paper but 0.85 clean and ~0.51 under frame edits in SIGMark's tests on HunyuanVideo.
- In SIGMark's own table VideoShield beats SIGMark on most columns. SIGMark's real advantage is blind extraction at constant cost.

### Gaps
- No survival tests on LivePortrait, FOMM, GAGAvatar or diffusion portrait models.
- No code found for VidSig, WaTeRFlow, MoSign or LampMark (Thread 3 later found LampMark's code).
- "21 LivePortrait keypoints" is an inference, not a stated figure.

---

## Thread 3 — Identity-, landmark- and source-conditioned face watermarks

**Notes file:** `identity_face_watermarks.md` (≈5,800 words)

### Landscape
- About **20 proactive face-watermarking methods**. All are single-image except GIFGuard (10-frame GIFs) and TaintedPixels (video).
- Almost all are tested on CelebA-HQ (+ LFW/FFHQ) at 128–512 px.
- "Identity" means three different things:
  - **Face identity:** Zhao WACV23, 2311.01357, CMark, SVS-WM, One-Identity-One-Key.
  - **Source/provenance ID:** LIDMark, SepMark, SAiW, SIDT, Dual Defense.
  - **Landmark geometry:** LampMark, LIDMark.
- **LIDMark's 16-bit "ID" is a SHA-256 hash of the image filename**, not a person's identity. It uses 136-D landmarks + 16-D ID; tested against SimSwap, UniFace, CSCS, StarGAN-v2 and InfoSwap (held out). No reenactment test; video is future work.

### The LampMark figure is miscited
| | 128 px | 256 px |
|---|---|---|
| Face-swap recovery | 97.44% | 96.46% |
| "Reenactment" recovery | 73.61% | 74.89% |

- FractalForensics' "96.46 vs 73.61" pairs the 256-px swap figure with the 128-px reenactment figure.
- Both papers count StarGAN v2 as "reenactment"; the only real reenactment methods in that set are StyleMask and HyperReenact.
- LampMark trained only on SimSwap, so the other swaps were unseen too, not "trained with".
- LampMark's *detection* AUC on HyperReenact is still ~99%.

### Who actually tested reenactment (six methods)
- LampMark, FractalForensics: StyleMask, HyperReenact.
- DiffMark: FSRT (CVPR 2024), apparently unseen; BER 0.12% (128 px), 4.05% (256 px).
- DeepForgeSeal: HyperReenact; bit recovery 0.06 (semi-fragile mark breaks as intended).
- Watermarking Matters (CVPR 2026 Findings): Face2Face, unseen; 90.53% accuracy.
- SepMark: GANimation (seen in training).
- **No watermarking paper evaluates LivePortrait, EMOPortraits, X-Portrait or HunyuanPortrait** (20 full texts searched). The newest generator used is FSRT. TaintedPixels (arXiv 2608.27492) is the only proactive defense tested on current tools (MuseTalk, Roop, FaceFusion), and it uses a perturbation that becomes visible, not a recoverable watermark.

### Novelty
- **No paper binds a driver claim to a target identity, or separates self- vs cross-reenactment.** That is done only passively (NVIDIA avatar fingerprinting, the FG 2026 follow-up).
- Closest analogs:
  - SIDT: hides the source face in a face-swap provider's output.
  - SAiW: attributes images to the generator that made them.
  - SVS-WM (ACM MM 2025): paired identity + attribute marks of the same face.
- Not searched: patents, C2PA-style industry schemes.

### Citation check
- All listed citations exist.
- SIDT is IEEE ICME 2022 (DOI 10.1109/ICME52920.2022.9859600): provider-side, post-generation.
- Venue corrections:
  - DiffMark: Information Fusion 2026.
  - FaceSigns: ACM TOMM 2024.
  - Dual Defense: IEEE TIFS 2024.
  - DeepForgeSeal: accepted to IEEE TPAMI.
- Still arXiv-only: 2311.01357, CMark, SAiW.
- Added: One-Identity-One-Key (IEEE TCSVT 2026), SVS-WM, Synth-Tracker (IEEE SPL 2025).
- Code confirmed: LIDMark, GIFGuard, DiffMark, FractalForensics, LampMark, SepMark, FaceSigns demo, EditGuard.

### Evidence-quality warnings
- DiffMark's re-implementation of LampMark gets 16.53% BER on SimSwap; LampMark's own paper reports ~0.05%.
- LIDMark's baseline rows are identical to DiffMark's (same lab group), so the baselines were copied, not re-run.

---

## Thread 4 — Attacks and evaluation

**Notes file:** `attacks_and_evaluation.md` (≈4,800 words)

### Removal
- **VideoMarkBench (arXiv 2505.21620):** with access to the extractor, white-box PGD drives **FNR = FPR = 1** for all four methods tested (REVMark, StegaStamp, VideoSeal, VideoShield).
  - JPEG and MPEG-4 compression raise missed detections for all four (notably MPEG-4 quality 40).
  - Gaussian noise σ = 0.15 nearly removes VideoSeal; VideoSeal is also the weakest to score-based black-box removal.
- **Image-only results:** Zhao et al. (VAE/diffusion regeneration removes >99% of pixel-level watermarks), WAVES, UnMarker.
- **"Removing the Watermark Is Not Enough" (arXiv 2605.09203), images only:** detectors built for a specific removal attack catch ≥99% of its outputs at 1% FPR. Only 1 of 750 outputs removed the mark, stayed within the quality budget *and* went undetected.
- **RobustSora (arXiv 2512.10248)** concerns visible commercial watermarks and AI-video detectors (−9.4 to +1.6 pt shifts), not invisible-watermark robustness.

### Forgery
- In VideoMarkBench's white-box setting, **forging needs smaller perturbations than removal**.
- Müller et al. (CVPR 2025) forge semantic watermarks using an unrelated public model and one watermarked image.
- Content-bound defenses (design patterns, not shown on video/reenactment):
  - MetaSeal (content-dependent cryptographic; images);
  - CSGuard (secret matrix; attack success 100% → 28.12%);
  - LIDMark (landmarks interwoven with ID).

### Open-source generator
- Video Seal's paper concedes post-hoc marking is "less secure" when the generator is open-sourced.
- Fine-tuning removes in-weight watermarks (Hu et al. 2405.07145; RoboSignature 2412.19834).
- Thread's inference: with LivePortrait and the VideoSeal extractor both public, white-box is the realistic case.
  - A missing mark proves nothing.
  - A payload not tied to the content can be forged onto any video.
  - The watermark can therefore support only positive attestation, and only if the payload is cryptographically content-bound.

### Temporal
- All four VideoMarkBench methods *survive* frame averaging, swapping and removal, which means they cannot *detect* those edits.
- Only VideoShield localizes swapped, inserted or dropped frames (its accuracy was not verified).
- Video Seal does not evaluate frame-rate changes or frame removal.
- Recommendation: signed segment indices or a hash chain over segments.

### Attacks on driver biometrics
- None evaluated in the literature.
- Inferred attacks: replay or retargeting of the victim's real motion, mimicry, adversarial latents.
- **Replay means motion biometrics do not prove liveness.**

### Metrics and protocol
- **Fidelity baselines** from LivePortrait: CSIM (ArcFace), AED/APD (SMIRK), gaze error (L2CS-Net).
- **Binomial thresholds** (independent-bit assumption):
  - 67/96 bits → FPR ≈ 6.6e-5;
  - 27/32 → ≈ 5.7e-5;
  - FPR < 1e-6 needs ≥ 72/96.
- **Calibration and reporting:** confirm FPR on real clean videos; report Clopper–Pearson intervals; use the rule of three.
- **Aggregation:** combine per-frame scores by median or at logit level.
- A six-part evaluation protocol is in the notes.

### Discrepancies flagged
- Video Seal's combined-attack log10 p: −6.1 in the text vs −8.1 in Table 4.
- UnMarker's ">50%" success and SynthID claim come from press; Google DeepMind disputes the SynthID figure.
- VideoShield's PSNR of 7.9 in VideoMarkBench reflects in-generation marking and isn't comparable to post-hoc methods.

### Biggest gaps
1. No regeneration/purification attacks have been tested on *video* watermarks.
2. No collusion or residual-estimation (copy) tests exist.
3. No frame-rate conversion or interpolation tests exist.
4. No adversarial evaluation of driver-verification systems exists.

---

## Thread 5 — Provenance, payload design, privacy and regulation

**Notes file:** `provenance_payload_privacy.md` (≈5,400 words)

### Design conclusion
- **Watermark = pointer.** A short random ID (~48–64 bits) + optional truncated MAC (16–32 bits) that resolves to a **signed C2PA manifest** holding all claims:
  - target and driver commitments;
  - generator;
  - session and nonce/epoch;
  - consent reference.
- **Authenticity comes from the manifest signature, not the bits.** A MAC only helps a verifier who holds the key.
- **Verifiers must re-check the content** (hash binding or fingerprint + face/identity check), because a valid watermark can be copied or replayed onto other content.
- **Nonces and session data go in the manifest.** C2PA's live-video segment assertion already provides a stream ID, a sequence number and a chain to the previous manifest.
- **Never derive identity from face embeddings.** Templates can be inverted (Keller et al.) or recovered across multiple uses (IronMask attack, PoPETs 2025). Instead use:
  - a random pseudonymous ID issued at enrollment;
  - a per-video salted, keyed commitment;
  - tiered, access-controlled resolution.

### C2PA facts
- **C2PA 2.4 (April 2026) is current** (verified from the spec page). It adds a new AI-disclosure assertion and recommends that the "watermarked" action reference its soft-binding assertion.
- Live video arrived in 2.3 (Dec 2025): ISO BMFF and CMAF, not MPEG-TS.
- The soft-binding assertion supports per-block time spans (ms) and regions, which suits per-segment video watermarks.
- AI-generated media is declared via a "created" action + IPTC `trainedAlgorithmicMedia`.
- The approved soft-binding list has 28 entries, 13 supporting video. **Meta's VideoSeal is not on it.**
- VideoSeal: 96-bit = legacy; v1.0 = 256 bits; PixelSeal 256; ChunkySeal 1024.

### Regulation (as of 2026-10-16)
- **India:**
  - IT Rules SGI amendments notified 10 Feb 2026, effective 20 Feb 2026 *[from law-firm/MediaNama summaries; Gazette text not read]*:
    - prominent labels;
    - permanent metadata or a unique identifier "where feasible";
    - removal of labels or metadata forbidden;
    - takedown windows: 3 h for court/government orders, 2 h for impersonation and morphed images.
  - Draft amendment (MeitY notice 21 Apr 2026, primary) requiring the label to stay visible for the whole video: comments closed 7 May 2026, not known to be finalised.
  - An 8 Oct 2026 advisory widening labelling is reported only by MediaNama.
  - DPDP Rules notified Nov 2025; consent and notice duties apply from ~May 2027.
- **EU:**
  - AI Act Article 50 applies from 2 Aug 2026.
  - Voluntary Code of Practice ~10 Jun 2026 *[date secondary]*: at least two machine-readable marks + a free detection tool.
  - Commission guidelines (20 Jul 2026) are a separate instrument.
  - AI Omnibus deferrals (to 2 Dec 2026 / 2 Feb 2027): sources conflict on whether they are enacted.
- **US:**
  - FTC enforcement of the TAKE IT DOWN Act from 19 May 2026 (48-hour removal).
  - NO FAKES Act still proposed (reportedly reintroduced May 2026; SAG-AFTRA is the only source).
  - California AB 2602 and New York's digital-replica law cover performer consent.
- **China:** Labeling Measures + GB 45438-2025 since 1 Sep 2025 (explicit labels + implicit metadata labels). Issuance date reported as 7, 14 or 17 Mar 2025.

### Unconfirmed
- ISO/IEC 24745 wording.
- Fields of the new C2PA AI-disclosure assertion.
- Details of C2PA's live-video "Verifiable Segment Info".
- MoSign beyond its abstract.
- US state laws beyond CA/NY.
- Any NVIDIA policy document (the "authorized use" framing comes only from its ECCV paper).

---

## Report-writing pass — synthesis highlights

The report writer combined all five note files and, where they disagreed, used the version read from the primary paper.

### Seven corrections to the original plan
1. **Channel independence is broken:** the estimated driver feeds the watermark. Use an authenticated declaration instead.
2. **Driver-vs-target comparison** works only on the transmitted latent (live calls). On published video it needs **enrolled motion of the claimed driver**.
3. **"Same vs different" is the wrong output.** Ask whether the biometric agrees with the declared driver and whether that driver is within the target's consent.
4. **Landmark-bound marks** would flag *every* reenactment; **face-identity marks** can't see reenactment at all.
5. **Noise-inversion methods** (SIGMark, VideoShield, VideoMark, Tree-Ring, Gaussian Shading) can't run on LivePortrait or GAGAvatar.
6. **No threat model:**
   - with an open generator, a missing mark proves nothing;
   - with a public extractor, white-box attacks break the methods tested and forgery is cheaper than removal;
   - claims need content binding to stop transplanting.
7. **Payload:**
   - claims go in a signed manifest, not in 96–256 bits;
   - no face-embedding commitments;
   - VideoSeal's single repeated message can't detect frame tampering;
   - VideoSeal isn't on C2PA's approved list.

### Recommended B.Tech design
| Choice | Recommendation |
|---|---|
| Generator | LivePortrait (GAGAvatar as second) |
| Watermark, phase 1 | Post-hoc VideoSeal v1.0 (256-bit) with per-segment keyed payloads (untested configuration; must be measured) |
| Watermark, phase 2 | SPDMark-style LoRA in LivePortrait's SPADE decoder (compute estimate by analogy) |
| Payload | Random ID + truncated MAC + ECC + segment index → signed C2PA manifest |
| Biometric | AVAPrintDB's public landmark-graph model |
| Scope | Offline verification of video from a cooperating service, not live videoconferencing |

### Gaps ranked by novelty per unit effort
1. Benchmark released watermarks (LampMark, LIDMark, DiffMark, FractalForensics, SepMark, VideoSeal) against LivePortrait, GAGAvatar and HunyuanPortrait.
2. Test whether watermarking lowers AVAPrintDB fingerprinting AUC.
3. Keyed per-frame watermark inside a non-diffusion reenactment decoder.
4. Declared-claim binding + biometric cross-check (the plan's real contribution; complementarity must be shown empirically).
5. Adversarial attacks on the biometric (replay, mimicry, adversarial latents).
6. Report EER and TAR@FAR, with self and cross results separate.

### Still hedged in the report
- Fine-tuning removal attacks (Hu et al., RoboSignature) came from summaries.
- EU deferral dates are unconfirmed.
- The 8 Oct 2026 Indian advisory has a single source.
- The novelty claim needs these read in full before saying "first": One-Identity-One-Key, SVS-WM, Synth-Tracker, ACM CSUR survey; plus Scholar "cited by" sweeps and a patent search.

### Correction to an earlier in-chat answer
The "LampMark 96.5% vs 73.6%" figure quoted early in the conversation mixes two resolutions. The like-for-like gap is **97.44% vs 73.61% at 128 px**.
