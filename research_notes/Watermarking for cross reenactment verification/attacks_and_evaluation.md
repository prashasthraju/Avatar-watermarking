# Attacks on, and Evaluation Protocols for, Video/Face Watermarks and Provenance, Applied to Watermarked Talking-Head Reenactment with Driver-Identity Verification

Scope note: research date 2026-10-16. The arXiv IDs given in the brief were each checked against their arXiv abstract page: 2505.21620, 2512.10248, 2605.09203, 2509.10766, 2605.01479. So were the supporting IDs 2412.09492, 2306.01953, 2401.08573, 2602.23523, 2605.07398 and 2407.03168. The following IDs, titles and claims come only from search listings or summaries, not fetched pages: VideoShield 2501.14195, Müller et al. 2412.03283, UnMarker 2405.08363, Hu et al. 2405.07145, RoboSignature 2412.19834, Avatar Fingerprinting 2305.03713, Unmasking Puppeteers 2510.03548 and its CVPRW 2023 predecessor, and TalkingHeadBench 2505.24866. Numbers are labeled **[unverified]** when they come only from search-result summaries or press coverage and not from a fetched paper page.

## Removal attacks (regeneration/diffusion purification, VAE/compression, averaging/collusion, adversarial) and results against VideoSeal and other video watermarks

### Takeaway
In VideoMarkBench, white-box adversarial perturbation fully breaks all four tested video watermarks. JPEG and MPEG-4 compression raise FNR for all four, notably at MPEG-4 Q = 40. Gaussian noise at σ = 0.15 drives FNR to about 1 for VideoSeal only, and VideoSeal is also the most vulnerable to score-based black-box removal. Image-domain evidence (Zhao et al., WAVES, UnMarker) shows that regeneration and spectral attacks remove most pixel-level watermarks. No paper was found that runs diffusion regeneration directly against Video Seal or another video watermark. A defender has one partial counter: image-domain removal outputs are currently easy to detect forensically with attack-specific detectors.

### Cited Findings
**VideoMarkBench (arXiv 2505.21620; Jiang, Guo, Li, Hu, Wang, Huang, Hong, Gong; submitted 27 May 2025; cs.CR preprint)**
- It describes itself as the first systematic benchmark of video-watermark robustness. It covers removal and forgery under white-box, black-box and no-box threat models, on videos from 3 generators in 3 styles (realistic, cartoon, sci-fi). — [arXiv abs](https://arxiv.org/abs/2505.21620)
- **Watermarks tested:** REVMark, StegaStamp, VideoSeal and VideoShield. **Generators:** Stable Video Diffusion, Sora and HunyuanVideo. — [arXiv HTML](https://arxiv.org/html/2505.21620)
- **12 perturbations:**
  - White-box: PGD with an ℓ∞ bound on every frame; arbitrary perturbation of a subset of frames.
  - Black-box: Square Attack (score-based, ℓ∞ 0.05); Triangle Attack (label-only).
  - Common: JPEG, Gaussian noise, Gaussian blur, crop, MPEG-4, frame averaging, frame swapping, frame removal.
  - [arXiv HTML](https://arxiv.org/html/2505.21620)
- **7 frame-to-video aggregation rules:** logit-mean, logit-median, bit-median, BA-mean, BA-median, detection-median, detection-threshold. — [arXiv HTML](https://arxiv.org/html/2505.21620)
- **White-box result:** with a small ℓ∞ PGD on all frames, every method reaches FNR = 1 (removal) and FPR = 1 (forgery). VideoSeal is the most removal-resistant, StegaStamp the most forgery-resistant. Forgery needs much smaller perturbations than removal. — [arXiv HTML](https://arxiv.org/html/2505.21620)
- **Black-box result (Square Attack):** VideoSeal is far more vulnerable to removal than StegaStamp or REVMark, which the authors attribute partly to its weakness against Gaussian noise. Under the label-only Triangle Attack, VideoSeal also needs much smaller perturbations. — [arXiv HTML](https://arxiv.org/html/2505.21620)
- **Common perturbations:**
  - All four methods withstand frame averaging, frame swapping, frame removal and Gaussian blur.
  - All are vulnerable to JPEG and MPEG-4, with FNR rising at MPEG-4 quality Q = 40.
  - VideoSeal's FNR approaches 1 at Gaussian noise σ = 0.15.
  - Only VideoSeal withstands cropping.
  - [arXiv HTML](https://arxiv.org/html/2505.21620)
- **Content dependence:** FNR differs significantly across generators (p ≈ 0.038) and across styles (p ≈ 0.029). Sora videos are more vulnerable than SVD videos, and sci-fi more than cartoon. — [arXiv HTML](https://arxiv.org/html/2505.21620)

**Video Seal's own evaluation (arXiv 2412.09492, Meta)**
- **Bit accuracy / log10 p on SA-V, Video Seal vs. the best baseline:**
  - Combined (H.264 + crop + brightness): 0.73 / −8.1. Every baseline (HiDDeN, MBRS, CIN, TrustMark, WAM) is at or below 0.61.
  - Geometric: 0.85 / −17.0.
  - Compression: 0.85 / −15.7, against MBRS 0.79 / −34.6 and CIN 0.90 / −6.7.
  - [arXiv HTML](https://arxiv.org/html/2412.09492)
- **Discrepancy:** the paper's text gives log10 p = −6.1 for the combined attack, but Table 4 gives −8.1. — [arXiv HTML](https://arxiv.org/html/2412.09492)
- The main evaluation uses H.264 at CRF 30. Training covers CRF 9–27, and ablations go to CRF 40–60. H.265 is mentioned, but no H.265 results are shown. — [arXiv HTML](https://arxiv.org/html/2412.09492)

**Regeneration attacks (Zhao et al., arXiv 2306.01953; NeurIPS 2024 per the arXiv comments)**
- **Method:** add noise, then reconstruct with a denoiser, VAE or diffusion model. A theorem bounds every detector: at FPR ε₁, FNR ≥ Φ(Φ⁻¹(1−ε₁) − L·Δ/σ) for a Δ-invisible watermark. — [arXiv HTML](https://arxiv.org/html/2306.01953v3)
- **Watermarks tested:** DwtDctSvd, RivaGAN, SSL and StegaStamp. — [arXiv HTML](https://arxiv.org/html/2306.01953v3)
- **Results:**
  - VAE and diffusion regeneration remove over 99% of DwtDctSvd, RivaGAN and SSL watermarks.
  - RivaGAN: about 98% removal at PSNR > 30.
  - StegaStamp falls only to diffusion at substantial noise (σ up to 0.57).
  - Tree-Ring resisted the attack.
  - [arXiv HTML](https://arxiv.org/html/2306.01953v3)

**WAVES (arXiv 2401.08573; ICML 2024)**
- **Setup:** 26 attacks in three families. Distortions: single and combined. Regeneration: Diff, DiffP, VAE, KLVAE, and 2x/4x diffusion "rinsing". Adversarial: embedding attacks through a surrogate VAE, CLIP or ResNet, plus surrogate-detector attacks. — [arXiv HTML](https://arxiv.org/html/2401.08573v3)
- **Metrics:** TPR@0.1%FPR, and normalized quality degradation computed from 8 metrics. — [arXiv HTML](https://arxiv.org/html/2401.08573v3)
- **Results:**
  - Stable Signature: regeneration drops average TPR to about 0.001.
  - Tree-Ring: a grey-box embedding attack using a shared VAE drives TPR to nearly zero.
  - StegaStamp: the most robust; Rinse-4xDiff only lowers TPR to about 0.909.
  - [arXiv HTML](https://arxiv.org/html/2401.08573v3)

**UnMarker (Kassis & Hengartner, IEEE S&P 2025, arXiv 2405.08363)** [details from a search summary of the arXiv page; full text not read]
- A spectral-amplitude adversarial attack that needs no detector feedback. The authors report it cuts the best detection rate against semantic watermarks to 43%. — [arXiv](https://arxiv.org/html/2405.08363v2)
- **[unverified]** The press claim of more than 50% success, including against SynthID and Stable Signature, comes from a university press release. Google DeepMind disputed the SynthID figure. — [Waterloo news](https://uwaterloo.ca/news/media/watermarks-offer-no-defense-against-deepfakes); [IEEE Spectrum](https://spectrum.ieee.org/ai-watermark-remover)

**"Removing the Watermark Is Not Enough" (arXiv 2605.09203; Goonatilake & Ateniese; May 2026, v2 Aug 2026)**
- Image-domain only. Across 6 removal attacks covering 4 strategies, attack-specific forensic detectors flag at least 99% of removal outputs at 1% FPR. — [arXiv abs](https://arxiv.org/abs/2605.09203)
- Of 750 outputs, only 1 removed the watermark, stayed within the fidelity budget and evaded forensic detection. — [arXiv abs](https://arxiv.org/abs/2605.09203)
- In theory, exact "forensic stealth" is achievable, so removal traces are not unavoidable. — [arXiv abs](https://arxiv.org/abs/2605.09203)

**RobustSora (arXiv 2512.10248; Wang, Liu, Sun; Dec 2025, v2 May 2026)**
- This paper concerns *visible* commercial watermarks (Sora, Sora 2, Pika, KLing, Open-Sora 2) and *AI-video detectors*. It does not test invisible-watermark robustness. — [arXiv abs](https://arxiv.org/abs/2512.10248)
- **Dataset:** 6,500 videos, split into Authentic-Clean, Generated-Watermarked, Generated-DeWatermarked and Authentic-Spoofed. — [arXiv abs](https://arxiv.org/abs/2512.10248)
- **Results:**
  - Erasing or spoofing watermarks shifts detector accuracy by −9.4 to +1.6 pp (mean 6.6 pp); the effect is significant (p < 0.01) for 7 of 10 detectors.
  - Sora 2 drops are −11 to −14 pp.
  - A placebo control bounds the inpainting confound at 2 pp or less.
  - Watermark-aware augmentation recovers about 3–4 pp.
  - [arXiv abs](https://arxiv.org/abs/2512.10248)

**Other removal work seen but not read in full**
- An NFPA paper (NeurIPS 2025) frames removal as next-frame prediction. **[unverified]** A search snippet gave about 1.2 s per image. — [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/b48405307576689bea14d221ccba73ae-Paper-Conference.pdf)
- Diffusion-editing attacks (arXiv 2510.05978, 2511.10933): titles only, no claims extracted. — [2510.05978](https://arxiv.org/pdf/2510.05978); [2511.10933](https://arxiv.org/html/2511.10933v1)

### Inferences
- A talking-head watermark has to survive two things. First, the codec chain: H.264/H.265 at CRF ≥ 30 and conferencing-grade bitrates. Second, a public decoder. In VideoMarkBench, white-box PGD fully breaks all four tested methods, and MPEG-4/JPEG raise FNR for all four (notably at Q = 40).
- Gaussian noise at σ ≈ 0.15 is a cheap, generator-free removal attack on VideoSeal. Any VideoSeal-derived scheme should be re-tested against it.
- Talking-head video is low-motion, with a static background and a centered face. That makes it a likely good case for regeneration attacks: per-frame image purification followed by temporal smoothing would probably preserve identity and expression well. This is untested.
- Forensic "laundering detectors" in the style of 2605.09203 are a reasonable second layer, so a verifier can flag "probably scrubbed". They are attack-specific, though, and were shown only on images.

### Gaps
- No paper was found that applies diffusion regeneration, VAE purification or UnMarker to *video* watermarks such as VideoSeal, REVMark or VideoShield. WAVES and Zhao et al. are image-only.
- **Collusion is untested.** No evaluation was found of averaging multiple outputs that carry *different* payloads (for example, two drivers' videos of the same avatar), or of estimating a fixed post-hoc residual pattern from many outputs. VideoMarkBench's "frame averaging" happens within a single video.
- The specific removal numbers of NFPA, 2510.05978 and 2511.10933 were not verified.

## Forgery, spoofing and copy attacks, and content-bound or cryptographic defenses

### Takeaway
A content-agnostic watermark (a fixed payload in a learned residual) can be forged or transplanted onto other content. In VideoMarkBench's white-box setting, forgery is easier than removal. Semantic, inversion-based watermarks can also be forged black-box. The defenses that work bind the watermark to the content and to a secret: MetaSeal signs content features, and CSGuard puts a secret matrix in both embedding and verification. Neither has been shown on video or on a reenactment generator.

### Cited Findings
- **VideoMarkBench:**
  - White-box PGD forgery reaches FPR = 1 for all 4 methods, with smaller perturbations than removal needs.
  - Black-box forgery stays near FPR ≈ 0. Under Triangle Attack, StegaStamp and VideoSeal keep an ℓ∞ norm of 1, while REVMark's falls to about 0.6.
  - [arXiv HTML](https://arxiv.org/html/2505.21620)
- **Black-box semantic-watermark forgery (Müller et al., CVPR 2025, arXiv 2412.03283):**
  - "Imprinting" moves a Tree-Ring or Gaussian Shading watermark onto real images by pushing their latent toward a watermarked latent in an *unrelated* latent diffusion model. The same technique also removes watermarks.
  - "Reprompting" inverts a watermarked image and regenerates it with a new prompt, and the watermark survives.
  - Both need only one watermarked reference image and a proxy model, even across UNet and DiT architectures.
  - [CVF open access](https://openaccess.thecvf.com/content/CVPR2025/html/Muller_Black-Box_Forgery_Attacks_on_Semantic_Watermarks_for_Diffusion_Models_CVPR_2025_paper.html)
- **MetaSeal (arXiv 2509.10766; Zhou, Ding, Liu, Fleming, Kompella, Fei, Xu, Ren; to appear at TMLR 2026):**
  - Content-dependent watermarking with cryptographic security guarantees.
  - Claimed properties: forgery resistance; self-contained attribution that tolerates benign transforms; and visible evidence of tampering.
  - Its motivation is that content-agnostic watermarks "can be transferred across images to fake attribution", and that detector-based verification can be fooled.
  - The abstract gives no numbers.
  - [arXiv abs](https://arxiv.org/abs/2509.10766)
- **CSGuard (arXiv 2605.01479; Lai et al.; May 2026; cs.CV preprint):**
  - Targets the invert → regenerate with an arbitrary prompt → extract forgery on latent-diffusion watermarks.
  - Binds embedding and verification to a secret compressed-sensing matrix.
  - Attack success drops from 100.0% to 28.12%, with 100% detection on benign watermarked images.
  - [arXiv abs](https://arxiv.org/abs/2605.01479)
- **RobustSora "Authentic-Spoofed" task:** fake visible watermarks injected onto authentic videos raise false alarms in AI-video detectors. This is a spoofing confound for any pipeline that uses watermark presence as a feature. — [arXiv abs](https://arxiv.org/abs/2512.10248)
- **LIDMark ("All in One", arXiv 2602.23523; CVPR 2026 per the arXiv comments):**
  - A 152-dimensional face watermark that "structurally interweaves facial landmarks with a unique source identifier".
  - A factorized decoder regresses landmarks for an intrinsic-vs-extrinsic consistency check, used for detection and tamper localization, and classifies the source ID for tracing.
  - This is a face-specific content-binding pattern. The abstract gives no numbers.
  - [arXiv abs](https://arxiv.org/abs/2602.23523)

### Inferences
- A reenactment watermark that encodes only (session ID, driver ID) bits is a content-agnostic payload. Given the public VideoSeal extractor, white-box PGD can stamp it onto any video. VideoMarkBench shows forgery is cheaper than removal. The result would be framing a legitimate driver for content they never produced.
- The appropriate pattern, combining MetaSeal and LIDMark, works as follows:
  1. Compute a robust content descriptor: for example, landmark trajectories and a coarse perceptual hash per frame or segment.
  2. Sign the descriptor together with the driver/session ID and a frame or segment index, using a private key.
  3. Embed the signature as the payload.
  4. At verification, recompute the descriptor and check the signature.
- With this design, transplanting a watermark onto new content fails the content-to-signature check.
- CSGuard shows that keeping the verifier key secret helps against forgery. That conflicts with public verifiability, so a design must choose between a secret verifier (a service attests on request) and an asymmetric signature with a robust content hash.

### Gaps
- No forgery or copy-attack evaluation was found specifically for post-hoc video watermarks (VideoSeal/WAM-style) under black-box *residual estimation*, meaning averaging the residual over many watermarked outputs and adding it to new content. The classic "copy attack" was not re-tested in 2023–2026 video papers found here.
- MetaSeal's and LIDMark's quantitative robustness and forgery numbers were not extracted, because only the abstracts were read.

## The open-source generator problem (public LivePortrait, Video Seal's security note, model-level removal)

### Takeaway
If the reenactment generator is public, an adversary can run it without the watermarking step. If the watermark is built into the weights, they can fine-tune it out. Video Seal's own paper concedes that post-hoc watermarking is "less secure" when the generator is open-sourced. Because Video Seal also releases its extractor, the white-box setting in which every VideoMarkBench method fails is the realistic threat model. Watermarks in this setting can support only *positive* attestation.

### Cited Findings
- **Video Seal on security:**
  - Contrasted with generation-time methods, post-hoc watermarking is "less secure, e.g., in the case of open-sourcing the generative model."
  - Security is explicitly left as future work ("exploring the security of the framework").
  - Code, checkpoints and a demo are released under permissive licenses.
  - [arXiv HTML 2412.09492](https://arxiv.org/html/2412.09492)
- **Model-level removal of in-weights watermarks:**
  - [from search summary; full text not read] Hu et al. ("Stable Signature is Unstable", arXiv 2405.07145) remove Stable Signature by fine-tuning the diffusion decoder while preserving quality. They need no access to the watermark encoder, and the earlier "model purification" defense they improve on degraded quality. — [arXiv 2405.07145](https://arxiv.org/pdf/2405.07145)
  - RoboSignature (arXiv 2412.19834) [from search summary] shows adversarial fine-tuning that stops the model from embedding the watermark, and proposes tamper-resistant fine-tuning as a defense. — [arXiv 2412.19834](https://arxiv.org/html/2412.19834v1)
- **Proxy-model attacks:** Müller et al. forge or remove semantic watermarks with *unrelated* public models. Even a closed generator gives no protection once open proxy models exist. — [CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Muller_Black-Box_Forgery_Attacks_on_Semantic_Watermarks_for_Diffusion_Models_CVPR_2025_paper.html)
- **White-box results (VideoMarkBench):** FNR = FPR = 1 for all four methods at small ℓ∞ budgets. — [arXiv HTML 2505.21620](https://arxiv.org/html/2505.21620)
- **Why proactive verification is needed:** in AI videoconferencing every frame is synthetic, so passive deepfake detectors fail. That motivates verifying identity in the transmitted latent rather than detecting synthesis. — [NeurIPS 2025 Unmasking Puppeteers](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a34308d616e3193199cfc7e82801a19f-Abstract-Conference.html)

### Inferences
These are labeled inferences, not sourced claims.
- **Public LivePortrait plus a public VideoSeal extractor:**
  - (a) *Absence* of a watermark proves nothing, because anyone can render unwatermarked reenactments.
  - (b) A content-agnostic payload can be forged onto arbitrary video through the public extractor's gradients.
  - (c) The watermark therefore supports only positive attestation ("this video was produced by our service, for this driver, in this session"), and only if the payload is cryptographically bound to content and the verification key or signing is controlled.
- Moving the watermark into LivePortrait's weights (Stable-Signature-style decoder fine-tuning, or watermarking the warping/SPADE decoder) does not fix (a). Attackers can use the original public checkpoint, or fine-tune the watermark out (Hu et al., RoboSignature).
- In-weights watermarking does help when the operator controls deployment, for example a hosted API or closed conferencing client. There it raises cost against casual removal.
- Driver-identity verification is a complementary signal that does not depend on the operator's pipeline. If the claim is "driver X drove this", a behavioral biometric (see the biometric section) can test it even on unwatermarked videos rendered by an attacker's own copy of LivePortrait. It is spoofable by mimicry, however.
- The threat model should state attacker knowledge explicitly, following VideoMarkBench:
  - White-box: public extractor and weights.
  - Black-box: scores or labels from a verification API.
  - No-box: common transforms only.
  - The public-code case is white-box.

### Gaps
- No paper was found that specifically studies watermark removal or bypass for open-source *reenactment* generators such as LivePortrait, FOMM or Face-vid2vid.
- No paper was found that evaluates in-weights watermarking of a warping-based reenactment model.
- Whether VideoSeal's extractor release was deliberate as a security trade-off is not discussed beyond the quoted sentence.

## Temporal attacks (frame deletion, insertion, reordering, frame-rate conversion) and detection

### Takeaway
Current frame-level watermarks are *robust* to frame removal, swapping and averaging: VideoMarkBench found none of the four methods broken by these. By the same property, they cannot *detect* temporal edits. Only schemes with per-frame positional templates, such as VideoShield, localize temporal tampering. Frame-rate conversion is not evaluated in any source found.

### Cited Findings
- **VideoMarkBench:** all four methods (REVMark, StegaStamp, VideoSeal, VideoShield) withstand frame averaging, frame swapping and frame removal. — [arXiv HTML](https://arxiv.org/html/2505.21620)
- **Video Seal's temporal design and coverage:**
  - Frame-rate changes, frame removal and temporal pooling attacks are not evaluated.
  - Temporal handling is limited to propagating the watermark every k = 4 frames and averaging soft bits across frames at extraction.
  - Accuracy rises with the number of frames.
  - k = 4 can cause "shadowy or blinkering artifacts" in fast motion.
  - [arXiv HTML 2412.09492](https://arxiv.org/html/2412.09492)
- **VideoShield (ICLR 2025, arXiv 2501.14195):**
  - An in-generation (diffusion) watermark whose template bits are recovered by DDIM inversion.
  - Temporal tamper localization compares each suspect frame against every original frame's template bits; the best match gives the frame's original position.
  - It covers frame swapping, insertion and dropping.
  - The authors note that image tamper-localization methods miss temporal tampering.
  - [arXiv HTML](https://arxiv.org/html/2501.14195v2); [ICLR poster](https://iclr.cc/virtual/2025/poster/27941)
- **VideoShield's PSNR of 7.945 in VideoMarkBench:** this measures the in-generation watermark's change to the content itself, not post-hoc distortion, so it is not comparable to post-hoc PSNR. VideoShield is also the slowest method (about 1.09×10⁴ ms per video, against about 16 ms for StegaStamp). — [arXiv HTML 2505.21620](https://arxiv.org/html/2505.21620)
- **Temporal-spectrum evasion of deepfake detectors (arXiv 2605.07398; Gu et al.; May 2026):**
  - Spatiotemporal detectors overfit to "fragile temporal spectrum cues" and can be evaded.
  - The proposed SpInShield defense beats the strongest baseline by 21.30 pp AUC under simulated amplitude-spectral attacks.
  - The attack is spectral, not frame deletion.
  - [arXiv abs](https://arxiv.org/abs/2605.07398)
- **LIDMark** claims tamper localization through a landmark-consistency check. The paper does not state temporal-edit coverage. — [arXiv abs](https://arxiv.org/abs/2602.23523)

### Inferences
- For a reenactment provenance system, two design options follow:
  1. Embed a per-segment index (frame counter or segment number) in the payload, and sign it together with the session ID. This mirrors VideoShield's positional templates in a post-hoc scheme.
  2. Bind the payload to a hash chain over segments.
- Either way, deletion, insertion and reordering become detectable as index gaps, duplicates or out-of-order indices. The segment length sets the temporal resolution of detection.
- Frame-rate conversion with interpolated frames (RIFE/FILM) blends two watermarked frames. If the payload differs per segment, blended frames may decode as garbage. Detection-threshold or median aggregation (VideoMarkBench's most robust rules) should tolerate a minority of such frames. This is untested.
- The temporal evaluation should include, as separate tests:
  - Deletion of N% of frames, random and in contiguous blocks.
  - Insertion of foreign frames, both unwatermarked and watermarked from another session.
  - Segment reordering.
  - Frame-rate change (30→24→30 and 30→60 with interpolation).
  - Speed change.
  - Splicing two sessions together.
- Report both robustness (the payload still decodes) and tamper-detection TPR/FPR, separately.

### Gaps
- VideoShield's temporal-localization accuracy numbers were not verified.
- No study found evaluates frame-rate conversion or frame interpolation against any video watermark.
- No post-hoc video watermark with signed frame indices was found in the 2023–2026 literature surveyed. The frame-deletion detection literature for natural video is older and was not covered here.

## Attacks against biometric and behavioral verification of drivers (mimicry, motion retargeting, adversarial latents)

### Takeaway
Driver verification from motion ("avatar fingerprinting") and from transmitted latents (puppeteering defenses) is an active line of work. Reported AUCs are modest (about 0.85) and degrade under generator or domain shift. No adversarial evaluation was found: none covers mimicry by a skilled impersonator, retargeting a victim's recorded motion, or adversarial perturbation of the pose/expression latent. This is the largest gap for the target system.

### Cited Findings
- **Avatar Fingerprinting (Prashnani et al., NVIDIA, ECCV 2024, arXiv 2305.03713):**
  - Learns motion embeddings that cluster by *driving* identity regardless of rendered appearance, to flag unauthorized use of a person's likeness.
  - **[unverified]** Search summaries give an average AUC of 0.85 and 0.83 on unseen generators.
  - [ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/2330_ECCV_2024_paper.php); [HF papers](https://huggingface.co/papers/2305.03713)
- **Follow-up work:**
  - **[unverified]** A 2026 FG paper (arXiv 2604.23247) reports 0.877 AUC on NVFAIR from raw frames without landmarks. — [alphaXiv](https://www.alphaxiv.org/abs/2604.23247.md)
  - **[unverified]** A Pattern Recognition benchmark (AVAPrintDB) reports that current avatar-fingerprinting systems remain highly sensitive to changes in the synthesis pipeline and source domain. — the paper mapping is unconfirmed; candidates are [arXiv 2603.26934](https://arxiv.org/html/2603.26934v1) and [arXiv 2508.00748](https://arxiv.org/pdf/2508.00748v1)
- **Unmasking Puppeteers (Vahdati, Nguyen, Stamm et al., NeurIPS 2025, arXiv 2510.03548):**
  - A pose-conditioned, large-margin contrastive encoder on the *transmitted pose/expression latent* isolates identity cues that leak into that latent.
  - A cosine test flags identity swaps in real time.
  - Self-reported to beat earlier puppeteering defenses and to generalize out of distribution.
  - [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/a34308d616e3193199cfc7e82801a19f-Abstract-Conference.html); [arXiv](https://arxiv.org/abs/2510.03548)
- **Predecessor (Vahdati et al., CVPRW 2023):** a defense against real-time puppeteering in low-bandwidth talking-head videoconferencing, using identity information in the transmitted expression and pose data, with a released benchmark dataset. — [CVF](https://openaccess.thecvf.com/content/CVPR2023W/WMF/html/Vahdati_Defending_Low-Bandwidth_Talking_Head_Videoconferencing_Systems_From_Real-Time_Puppeteering_Attacks_CVPRW_2023_paper.html)
- **TalkingHeadBench (WACV 2026, arXiv 2505.24866):** detectors that are near-perfect on older benchmarks struggle on modern talking-head deepfakes, especially under identity and generator shift. — [arXiv HTML](https://arxiv.org/html/2505.24866v3)

### Inferences
- The attack taxonomy for driver verification follows from how these systems work. Avatar fingerprinting assumes motion is idiosyncratic, and puppeteer defenses read identity leakage in latents. The four attacks below are inferred from that and are untested in the sources found.
  1. **Replay or retarget:** reuse the victim's recorded motion (from public video), extract LivePortrait keypoints, and drive any avatar. The motion biometric then *passes*, because it is genuinely the victim's motion.
  2. **Mimicry:** an impersonator imitates the victim's mannerisms.
  3. **Motion-style transfer:** a model maps the attacker's motion into the victim's style.
  4. **Adversarial latents:** with white-box access to the verifier, perturb the implicit keypoints or expression deltas to hit the target embedding within an AED/APD budget.
- Retargeting means motion-based verification does not prove *liveness*. It must be paired with a session-bound challenge (random prompts or expressions), or with the watermark payload signed at capture time by the driver's device.
- Evaluate the driver verifier like a biometric system (ISO/IEC 30107-3-style presentation-attack framing). Report:
  - EER and TPR at FAR = 1e-2 / 1e-3 for zero-effort impostors.
  - Separate attack-presentation classification error rates for replay, mimicry and adversarial attacks.
  - Cross-generator and cross-dataset splits, since AVAPrintDB shows sensitivity to these.

### Gaps
- No paper was found that attacks avatar fingerprinting or latent-domain puppeteer detectors with mimicry, motion retargeting or adversarial latents.
- The AUC figures for avatar fingerprinting and its follow-ups were not verified against the papers themselves.
- No source was found on ISO/IEC 30107-3 applied to talking-head reenactment, so that recommendation is an inference.

## Standard metrics and protocols (bit accuracy, TPR@FPR, PSNR/SSIM/LPIPS/VMAF, FVD, ArcFace identity, AED/APD, temporal consistency) and thresholds and uncertainty

### Takeaway
The detection metrics in use are bit accuracy and log10 p (Video Seal), FNR and FPR at a bit-match threshold (VideoMarkBench), and TPR@0.1%FPR (WAVES). Quality is reported with PSNR, SSIM, LPIPS, VMAF and temporal LPIPS. Reenactment fidelity follows LivePortrait: CSIM (ArcFace), AED and APD (SMIRK), gaze MAE (L2CS-Net) and FID. Theoretical binomial thresholds should be checked empirically on clean videos. Frame-to-video aggregation needs to be specified, because it changes results materially.

### Cited Findings
- **Video Seal:**
  - log10 p of the observed bit accuracy under a Binomial(n_bits, 0.5) null, with log10 p < −6 corresponding to FPR < 1e-6.
  - Quality: PSNR (whole video), SSIM and LPIPS (frame-averaged), and VMAF.
  - The authors note that "clear metrics" for video imperceptibility are lacking, and that artifacts can be visible even at high PSNR, SSIM or VMAF.
  - Imperceptibility on SA-V: PSNR 48.02, SSIM 0.998, VMAF 93.77. MBRS has the best VMAF at 94.10.
  - [arXiv HTML](https://arxiv.org/html/2412.09492)
- **VideoMarkBench:**
  - Thresholds: τ = 67/96 bits for REVMark and VideoSeal; 27/32 for StegaStamp; for VideoShield, the maximum score over 1,000 unwatermarked videos. Target theoretical FPR < 0.01%.
  - Quality: PSNR, SSIM and temporal LPIPS (tLP).
  - Unperturbed PSNR/SSIM/tLP: VideoSeal 37.85/0.942/0.145 and StegaStamp 37.91/0.945/0.198.
  - Logit-level aggregation beats bit-accuracy-level aggregation, and median beats mean.
  - Significance tests across generators and styles are reported.
  - [arXiv HTML](https://arxiv.org/html/2505.21620)
- **WAVES:**
  - Detection: TPR@0.1%FPR, chosen over AUROC or p-values.
  - Quality: normalized degradation over PSNR, SSIM, NMI, FID, CLIP-FID, LPIPS, aesthetics and artifacts.
  - Attacks ranked by performance-vs-quality curves (Q@0.95P, Q@0.7P).
  - [arXiv HTML](https://arxiv.org/html/2401.08573v3)
- **Zhao et al.:** TPR at FPR = 0.01. — [arXiv HTML](https://arxiv.org/html/2306.01953v3)
- **"Removing the Watermark Is Not Enough":** forensic detection rate at 1% FPR. A joint criterion counts an attack as successful only if it removes the watermark, stays within the fidelity budget and evades forensic detection. — [arXiv abs](https://arxiv.org/abs/2605.09203)
- **RobustSora:** reports accuracy deltas in pp with p-values and a placebo control for confounds. — [arXiv abs](https://arxiv.org/abs/2512.10248)
- **LivePortrait protocol (arXiv 2407.03168):**
  - Self-reenactment: PSNR, SSIM, LPIPS (AlexNet), L1, CSIM (ArcFace cosine, animated vs. driving) and gaze MAE (L2CS-Net), at 256×256 on TalkingHead-1KH (35 videos) and VFHQ (50 videos).
  - Cross-reenactment: the first 50 FFHQ images as sources, with FID, CSIM (vs. source), AED (SMIRK expression parameters, mean L1), APD (SMIRK pose parameters) and MAE.
  - [arXiv HTML](https://arxiv.org/html/2407.03168)
- **LivePortrait baselines (useful for "fidelity cost of watermarking"):**

| Setting | Dataset | PSNR | SSIM | LPIPS | CSIM | AED | APD | FID |
|---|---|---|---|---|---|---|---|---|
| Self | TalkingHead-1KH | 32.01 | 0.819 | 0.066 | 0.913 | – | – | – |
| Cross | TalkingHead-1KH | – | – | – | 0.391 | 0.677 | 0.0333 | 58.04 |
| Cross | VFHQ | – | – | – | 0.261 | 0.648 | 0.0271 | 56.42 |

  Source: [arXiv HTML](https://arxiv.org/html/2407.03168)

### Inferences
- **Threshold arithmetic.** Computed here with an exact binomial tail, not taken from a source.
  - P(X ≥ 67 | n = 96, p = 0.5) ≈ 6.6e-5, and P(X ≥ 27 | n = 32) ≈ 5.7e-5. Both are consistent with VideoMarkBench's "FPR < 0.01%".
  - Reaching Video Seal's log10 p < −6 (FPR < 1e-6) with 96 bits needs at least 72 matching bits (tail ≈ 4.8e-7).
  - The null assumes independent, unbiased bits for unwatermarked content. Learned extractors violate this, because they produce biased or correlated bits on certain content. Calibrate the threshold empirically on a large clean set that includes real, unwatermarked talking-head video (VoxCeleb, HDTF, TalkingHead-1KH), the way VideoMarkBench does for VideoShield.
- **Reporting uncertainty:**
  - Give Clopper–Pearson 95% intervals for TPR and FPR.
  - Rule of three: zero false positives in N clean videos bounds FPR at about 3/N, so claiming FPR ≤ 1e-4 needs roughly 30,000 or more negatives, and 1e-6 needs millions. Use the analytic binomial bound only alongside an empirical check at the achievable N.
  - Report the aggregation rule (prefer logit-median or detection-threshold) and the number of frames used.
  - Use per-generator and per-identity breakdowns, with significance tests as VideoMarkBench does.
- **Recommended protocol for this system:**
  - (i) Robustness: TPR@FPR ∈ {1e-2, 1e-3, 1e-4} and bit accuracy under:
    - Codecs: H.264/H.265 at CRF 23/30/40, and conferencing transcodes.
    - Crop, resize and brightness.
    - Gaussian noise σ up to 0.15.
    - Temporal edits.
    - Regeneration: per-frame diffusion and VAE purification.
    - White-box PGD using the public extractor.
  - (ii) Forgery: FPR for watermark transplant and PGD forgery onto clean or other-session videos.
  - (iii) Quality: PSNR, SSIM, LPIPS, VMAF and tLP between watermarked and unwatermarked reenactments.
  - (iv) Reenactment fidelity delta, comparing watermarked vs. unwatermarked on CSIM, AED, APD, gaze MAE and FID under the LivePortrait protocol, so watermarking does not damage identity or expression transfer.
  - (v) Driver verification: EER and TPR@FAR, with separate attack classes.
  - (vi) A joint attack-success criterion in the style of 2605.09203 (removed AND within the quality budget AND undetected).
- **Choosing attack strength:** sweep the attack and plot detection against quality (WAVES-style curves) instead of using a single operating point. Use CSIM, AED and APD as the "semantic fidelity budget" for talking heads: an attack that removes the watermark but destroys identity or expression is not a practical success.

### Gaps
- No source was fetched that defines FVD or temporal-consistency metrics (warping error, tLP) for watermark evaluation. VideoMarkBench uses tLP but its definition was not extracted.
- VMAF's sensitivity to watermark artifacts on faces was not studied in any source found.
- No standard benchmark was found for watermarking *reenactment* outputs specifically. VideoMarkBench uses SVD, Sora and HunyuanVideo, not talking-head generators.
