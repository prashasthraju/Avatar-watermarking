# Research Plan: Watermarking and Identity Verification for Cross-Reenactment

## 1. Problem statement

The goal is to develop a system that can determine whether an AI-generated facial reenactment is authentic with respect to its **source identity, driving identity, and generation history**.

In a talking-head reenactment system, a driving person provides facial expressions, head pose, and motion, while a target person provides the appearance and identity to be rendered.

Two cases must be distinguished:

- **Self-reenactment:** the driver and target are the same person, so `ID_driver = ID_target`.
- **Cross-reenactment:** one person's motion drives another person's appearance, so `ID_driver != ID_target`.

The research question is:

> **Can identity-conditioned, temporally robust watermarks be embedded into a facial-reenactment generation pipeline and combined with independent biometric verification to identify AI-generated content, trace its provenance, and distinguish self-reenactment from cross-reenactment?**

The goal is not merely to detect deepfakes. It is to establish who drove the motion, whose identity was rendered, which system generated the content, and whether those claims can be independently verified.

**Important distinction:** cross-reenactment is not inherently malicious. The system should identify the driver–target relationship, not automatically classify different identities as fraud.

## 2. Break the problem into separate tasks

| Task | Question | Candidate techniques |
|---|---|---|
| AI-origin detection | Was this output produced by a known AI-generation system? | Invisible watermarks, generator fingerprints, forensic detectors |
| Provenance verification | Is the origin/edit-history claim verifiable? | C2PA Content Credentials, signatures, robust watermarking |
| Generator attribution | Which model or generator produced the output? | Generator fingerprints, source-attribution methods |
| Manipulation detection | Was the face or video altered after generation? | Fragile/semi-fragile watermarks, landmark checks, forensic models |
| Driver–target verification | Is the person driving the motion the same as the rendered identity? | Avatar fingerprinting, motion-latent biometrics, identity-conditioned watermarking |
| Temporal integrity | Were frames removed, duplicated, replaced, or reordered? | Frame-specific payloads, temporal codes, sequence verification |

These objectives overlap, but they are not interchangeable. A watermark can establish that content carries a valid claim; it does not, by itself, prove that the claim is true.

## 3. Main approaches

### A. Robust neural video watermarking

Embed a hidden signal in generated frames and train a decoder to recover it after common transformations such as compression, resizing, and re-encoding.

**Use it for:** a baseline for AI-origin and provenance watermarking.

**Starting point:** [VideoSeal — Open and Efficient Video Watermarking](https://ai.meta.com/research/publications/video-seal-open-and-efficient-video-watermarking/).

**Limitations:** a generic payload does not necessarily identify the driver or target, and may not survive strong generative editing or face reenactment.

### B. Watermarking during generation

Instead of watermarking the final RGB frames, modify the generation process so the signal is embedded in the noise, latent representation, decoder, or selected model parameters.

Relevant strategies include:

- Latent/noise-space watermarking.
- Fine-tuning or modifying a generator/decoder.
- Parameter-efficient watermarking, such as LoRA-based parameter displacements.
- Frame-specific messages and temporal coding.

**Starting points:**

- [SIGMark (2026)](https://arxiv.org/abs/2603.02882)
- [SPDMark (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/html/Fares_SPDMark_Selective_Parameter_Displacement_for_Robust_Video_Watermarking_CVPR_2026_paper.html)
- [Video Signature / VIDSIG](https://arxiv.org/abs/2506.00652)
- [VideoShield](https://arxiv.org/abs/2501.14195)
- [VideoMark](https://arxiv.org/abs/2504.16359)

**Use it for:** placing provenance closer to the source of generation rather than adding it only after synthesis.

**Implementation caveat:** these methods are not drop-in solutions for every talking-head generator. Diffusion-specific methods generally require a compatible diffusion pipeline. For non-diffusion reenactment models, embedding may need to occur in motion features, intermediate representations, or the image decoder.

### C. Identity- and landmark-conditioned watermarking

Associate a hidden signal with identity-related information or facial structure. A detector can recover a source identifier and compare expected facial landmarks with those observed in the output.

**Starting point:** [LIDMark — joint deepfake detection, tampering localization, and source tracing (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_All_in_One_Unifying_Deepfake_Detection_Tampering_Localization_and_Source_CVPR_2026_paper.html).

Other relevant work:

- [Proactive Deepfake Defence via Identity Watermarking (WACV 2023)](https://openaccess.thecvf.com/content/WACV2023/html/Zhao_Proactive_Deepfake_Defence_via_Identity_Watermarking_WACV_2023_paper.html)
- [SIDT — Source-ID-Tracker](https://ieeexplore.ieee.org/document/9859600/)
- [LampMark](https://arxiv.org/abs/2411.17209)
- [SAiW](https://arxiv.org/abs/2603.23178)
- [DiffMark](https://arxiv.org/abs/2507.01428)

**Use it for:** tracing source identity, detecting inconsistencies, and potentially localizing facial manipulation.

### D. Driver identity fingerprinting

Estimate who is driving a generated avatar by analyzing facial motion, landmarks, head pose, expressions, or pose-expression latents. This channel should be independent of the watermark decoder wherever possible.

**Starting points:**

- [Avatar Fingerprinting / AVAPrintDB](https://arxiv.org/abs/2603.26934)
- [Unmasking Puppeteers (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a34308d616e3193199cfc7e82801a19f-Abstract-Conference.html)

**Use it for:** answering the central question—whether the motion-driving person and rendered target are the same.

**Why it matters:** a watermark could carry a false or spoofed claim. Independent biometric evidence provides a second channel for checking whether the declared driver is plausible.

### E. Cryptographic provenance

Use signed provenance metadata alongside invisible watermarking. C2PA Content Credentials can record signed assertions about media origin and editing history, using hard bindings such as cryptographic hashes and soft bindings such as watermarks or fingerprints.

**Starting point:** [C2PA Specification 2.3](https://spec.c2pa.org/specifications/2.3/).

**Use it for:** verifying a documented generation/editing workflow. It complements rather than replaces biometric verification or a robust watermark.

## 4. Recommended system architecture

The most promising design is a **dual-channel system**: (1) an identity-conditioned watermark embedded during generation and (2) an independent driver-identity verifier.

```text
Driving video                         Target identity/image
      |                                        |
      v                                        |
Motion / pose / expression encoder             |
      |                                        |
      v                                        v
Estimated driver identity              Reenactment generator
              \                               /
               \                             /
                +-- identity-conditioned ----+
                    watermark module
                          |
                          v
                  Generated video
                          |
             +------------+-------------+
             |                          |
             v                          v
     Watermark extraction       Driver biometric analysis
             |                          |
             v                          v
     Payload/authentication      Estimated driver identity
             |                          |
             +------------+-------------+
                          v
                 Consistency verifier
                          |
                          v
          Same / different / uncertain
          + provenance and frame-integrity report
```

### Potential watermark payload

A protected payload could carry or reference:

- Pseudonymous target identity commitment.
- Pseudonymous driver identity commitment or declared driver claim.
- Generator/model identifier.
- Session nonce.
- Frame or sequence information.
- Integrity/authentication data and error-correcting redundancy.

The actual identity commitments should be designed carefully. Avoid putting raw biometric templates or personally identifying information directly into the payload. Use a protected key and authenticated encoding so that a person cannot simply write an arbitrary driver ID into the watermark.

### Verification logic

The system should assess at least three things separately:

1. **Watermark validity:** Can the message be extracted, and does its authentication check pass?
2. **Driver–target consistency:** Does the independently estimated driving identity match the rendered target identity, within the calibrated operating threshold?
3. **Temporal integrity:** Are the frame sequence and any frame-specific payloads consistent?

Possible outcomes:

| Watermark | Driver–target result | Interpretation |
|---|---|---|
| Valid | Same identity | Consistent with declared self-reenactment |
| Valid | Different identities | Consistent with cross-reenactment if declared/authorized; not automatically malicious |
| Invalid/missing | Either | Provenance cannot be confirmed; this alone does not prove malicious manipulation |
| Valid | Biometric evidence contradicts declared driver | Potential mismatch, spoofing, model failure, or out-of-distribution input; flag for further analysis |

A valid watermark proves only that a recognized signal and authenticated claim were present. It does not prove that the underlying claim is true, so independent verification remains necessary.

## 5. Suggested research plan

### Stage 1 — Establish the biometric baseline

1. Obtain the AVAPrintDB dataset and reproduce an avatar-fingerprinting baseline.
2. Evaluate self- versus cross-reenactment.
3. Test whether performance holds across different identities, generators, and recording conditions.
4. Report failures on unseen generators rather than relying only on random train/test splits.

**Deliverable:** a reproducible driver–target verification baseline.

### Stage 2 — Establish a watermark baseline

1. Implement or evaluate VideoSeal on the video outputs.
2. Measure extraction reliability under compression, resizing, frame-rate changes, and re-encoding.
3. Measure visual quality and temporal consistency.
4. Add face manipulation and reenactment transformations to the test set.

**Deliverable:** a robust watermark baseline and an attack/evaluation harness.

### Stage 3 — Test identity-conditioned embedding

1. Choose an embedding location supported by the generator: latent, intermediate feature, decoder, or post-generation video.
2. Bind the payload to target, driver claim, generator, and session.
3. Where feasible, compare frame-specific encoding against repeated frame-independent messages.
4. Measure identity preservation, watermark recovery, expression fidelity, and temporal coherence.
5. Compare generation-time embedding with post-generation embedding.

**Deliverable:** a watermarking module integrated into the selected reenactment pipeline.

### Stage 4 — Combine the two channels

Compare these configurations:

- No watermark, biometric verifier only.
- Watermark only.
- Biometric verifier only.
- Watermark plus biometric verifier.
- Combined system plus temporal verification and signed provenance metadata.

Evaluate whether combining the signals actually improves reliability. Do not assume that adding a watermark automatically improves driver–target classification.

**Deliverable:** an ablation study that shows the contribution of each component.

## 6. Evaluation matrix

| Objective | Suggested metrics/tests |
|---|---|
| Driver–target verification | ROC-AUC, equal error rate (EER), false-accept rate, false-reject rate |
| Watermark recovery | Bit accuracy, message recovery rate, false-positive rate |
| Provenance verification | Authenticated vs unauthenticated output; valid/missing/invalid watermark cases |
| Temporal robustness | Frame deletion, insertion, duplication, reordering, and frame-rate conversion |
| Manipulation localization | Frame-level and spatial precision/recall, where localization is supported |
| Visual quality | Perceptual quality, identity similarity, expression fidelity, temporal consistency |
| Generalization | Unseen generators, identities, datasets, compression settings, and attacks |

Include clean/self-reenactment, declared cross-reenactment, manipulated output, missing watermark, invalid signature, and out-of-distribution cases. Calibrate thresholds on held-out data and report uncertainty; avoid treating every biometric mismatch as proof of malicious activity.

## 7. Threats and failure modes to test

- H.264/H.265 compression, resizing, cropping, blur, noise, color adjustments, and re-encoding.
- Frame deletion, insertion, duplication, reordering, and changes to frame rate.
- Face swapping, reenactment, inpainting, and generative regeneration.
- Watermark removal, copying, or spoofed payloads.
- Unseen generators and changes in the driving video or capture conditions.
- False biometric matches, poor landmark tracking, occlusion, and low-resolution faces.
- A compromised generator or signing key that creates apparently valid but untrustworthy claims.

Robustness is always threat-model-dependent. A watermark that survives ordinary compression may still fail under generative regeneration or deliberate removal.

## 8. Priority reading list

### Highest priority for the exact problem

1. [Avatar Fingerprinting / AVAPrintDB](https://arxiv.org/abs/2603.26934) — directly relevant to self- versus cross-reenactment.
2. [Unmasking Puppeteers (NeurIPS 2025)](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a34308d616e3193199cfc7e82801a19f-Abstract-Conference.html) — driver identity signals in pose/expression latents.
3. [LIDMark (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/html/Wu_All_in_One_Unifying_Deepfake_Detection_Tampering_Localization_and_Source_CVPR_2026_paper.html) — landmark and identity watermarking, detection, localization, and tracing.
4. [VideoSeal](https://ai.meta.com/research/publications/video-seal-open-and-efficient-video-watermarking/) — robust neural video watermarking baseline.
5. [SIGMark](https://arxiv.org/abs/2603.02882) — in-generation video watermarking and temporal robustness.
6. [SPDMark (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/html/Fares_SPDMark_Selective_Parameter_Displacement_for_Robust_Video_Watermarking_CVPR_2026_paper.html) — parameter-displacement approach to generation-time watermarking.
7. [Video Signature / VIDSIG](https://arxiv.org/abs/2506.00652) — in-generation watermarking and temporal consistency.
8. [VideoShield](https://arxiv.org/abs/2501.14195) — generation-time watermarking and tamper localization.
9. [VideoMark](https://arxiv.org/abs/2504.16359) — frame-wise coding and temporal alignment.

### Identity and source attribution

10. [Proactive Deepfake Defence via Identity Watermarking](https://openaccess.thecvf.com/content/WACV2023/html/Zhao_Proactive_Deepfake_Defence_via_Identity_Watermarking_WACV_2023_paper.html)
11. [SIDT — Source-ID-Tracker](https://ieeexplore.ieee.org/document/9859600/)
12. [LampMark](https://arxiv.org/abs/2411.17209)
13. [SAiW](https://arxiv.org/abs/2603.23178)
14. [DiffMark](https://arxiv.org/abs/2507.01428)

### General watermarking and provenance

15. [Tree-Ring Watermarks](https://arxiv.org/abs/2305.20030) — diffusion noise-space watermarking.
16. [Gaussian Shading](https://arxiv.org/abs/2404.04956) — latent-space watermarking.
17. [Stable Signature](https://openaccess.thecvf.com/content/ICCV2023/papers/Fernandez_The_Stable_Signature_Rooting_Watermarks_in_Latent_Diffusion_Models_ICCV_2023_paper.pdf) — watermarking rooted in a generative model's decoder.
18. [WOUAF](https://openaccess.thecvf.com/content/CVPR2024/html/Kim_WOUAF_Weight_Modulation_for_User_Attribution_and_Fingerprinting_in_Text-to-Image_CVPR_2024_paper.html) — generator/user attribution.
19. [C2PA Specification 2.3](https://spec.c2pa.org/specifications/2.3/) — signed provenance metadata.

## 9. Recommended research direction

A useful working title is:

> **Generation-Time Identity-Conditioned Watermarking for Robust Driver–Target Verification in Talking-Head Reenactment**

Investigate three questions:

1. **Embedding:** Can an identity-conditioned watermark be injected into the reenactment generation process while preserving identity, expression quality, and temporal coherence?
2. **Verification:** Can that watermark be combined with motion-latent or landmark-based biometrics to distinguish self-reenactment from cross-reenactment, including on unseen generators?
3. **Robustness:** Can the system preserve provenance through benign transformations while identifying or localizing malicious edits and temporal manipulation?

The plausible contribution is the **combination** of generation-time identity-conditioned watermarking with an independent driver biometric and temporal integrity checks. This should be treated as a hypothesis to validate, not as an established research gap. Before claiming novelty, compare the proposed combination directly with existing identity watermarking, LIDMark, avatar fingerprinting, and video-generation watermarking approaches.

### Practical recommendation

Start with the avatar-fingerprinting baseline because it directly measures the driver–target question. In parallel, build a VideoSeal watermarking baseline. Once both work independently, integrate identity-conditioned embedding into the generator and run controlled ablations. This sequence provides measurable progress without committing prematurely to a complex custom generation architecture.
