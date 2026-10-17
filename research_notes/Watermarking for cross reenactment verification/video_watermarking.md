# Video Watermarking (Generation-time and Post-hoc) and Its Applicability to Talking-Head / Portrait-Animation (Face Reenactment) Generators

Research date: 2026-10-16. Unless marked otherwise, all numbers come from the cited paper's own arXiv HTML or abstract page as fetched in this session. Numbers reported by a paper about *other* methods are marked "(as reported by X)". Cross-paper conflicts are flagged explicitly.

---

## Q1. For VideoSeal, SIGMark, SPDMark, VidSig, VideoShield, VideoMark, Stable Signature, Tree-Ring, Gaussian Shading, WOUAF, I2VWM, WaTeRFlow and other 2024–2026 video watermarks: what are the embedding location, payload, robustness (compression, crop, frame drop/reorder), temporal tamper detection/localization, and required generator architecture?

### Takeaway
Video watermarks fall into four embedding families, and each is tied to an architecture. (1) **Post-hoc pixel** methods (VideoSeal, LoT-Pass/I2VWM, WaTeRFlow, LampMark) work with any generator. (2) **Decoder fine-tuning** (Stable Signature, VidSig, SPDMark, WOUAF-style weight modulation) needs a learned decoder you control, whether a VAE decoder or a pixel renderer. (3) **Initial-noise** methods (Tree-Ring, Gaussian Shading, VideoShield, VideoMark, SIGMark) need a diffusion or flow sampler plus inversion through the generator at verification time. (4) **Motion-latent** marks (MoSign) need a motion VAE. Robustness is mostly ≥0.9 bit accuracy for valuemetric and temporal edits, though some reported figures sit lower (VideoSeal valuemetric 0.90, SIGMark drop-30 0.81). It is weaker under real codecs combined with geometry, and under screen recording or recapture (about 0.73–0.88).

### Cited Findings

**Per-method summary table** (every row is sourced in the bullets that follow it).

| Method (venue as verified) | Embedding location | Payload | Key robustness numbers | Temporal features | Generator requirement | Code |
|---|---|---|---|---|---|---|
| VideoSeal (arXiv 2412.09492, preprint) | Post-hoc pixel: U-Net embedder (~16M params) at 256×256; ViT-S extractor (~22M) | 96 bits (same message in every frame) | SA-V: identity 0.99, valuemetric 0.90, geometric 0.85, H.264/H.265 0.85, combined 0.73 bit accuracy | Temporal propagation (embed every k=4th frame, copy residual); soft-bit averaging across frames; no tamper localization | None (any video) | facebookresearch/videoseal |
| SIGMark (arXiv 2603.02882, ICLR 2026 per arXiv comments) | Initial noise via global frame-wise PRC keys (GF-PRC), distortion-free | 512 bits per causal frame group; or distinct 512 bits per group = 512×16 bits/video | HunyuanVideo I2V: clean 0.98, MPEG 0.84, blur 0.95, drop-30 0.81, insert-30 0.87, clip-30 0.85 | Segment Group-Ordering (optical-flow cut detection + sliding-window detection) re-groups/re-orders frames | Video diffusion/flow models with causal 3D VAE (HunyuanVideo, Wan-2.2); extraction = VAE encoder + flow-matching Euler inversion | JeremyZhao1998/SIGMark-release |
| SPDMark (arXiv 2512.12090, CVPR 2026 per arXiv comments) | VAE decoder: LoRA basis shifts (4 rank-32 bases × 14 ResNet blocks), key selects composition | 28 bits/frame (14 blocks × 2 bits); ablations 34 and 56 bits | SVD-XT / ModelScope: crop 0.989/0.978, drop 0.988/0.969, swap 0.994/0.986, insert 0.994/0.986, recompression 0.880/0.986, screen recording 0.837/0.821 | HMAC-SHA256 per-frame messages; Hungarian bipartite matching recovers order; drop/insert localization F1 ≈0.995–0.999; swap order accuracy 1.000 | Latent video diffusion with VAE decoder (SVD-XT, ModelScope) | Samar-Fares/SPDMark |
| VidSig / Video Signature (arXiv 2506.00652, venue not stated) | Partial fine-tune of latent decoder (PAS freezes perceptually sensitive layers) + temporal alignment module | 48 bits (Stable Signature extractor), majority vote across frames | H.264 CRF20 BA 0.894 (TPR@1e-4 0.880), CRF23 0.869; temporal edits ≈0.992 (MS) / 0.999 (SVD) | Same message every frame; robust to drop/swap/insert, but no localization | Latent video diffusion (ModelScope, SVD; transfers to Latte) | Not found |
| VideoShield (arXiv 2501.14195, ICLR 2025) | Initial noise: watermark bits → template bits (repeated ×128 MS, ×512 SVD), training-free | 512 bits/video | Clean 1.000 (MS) / 0.999 (SVD); avg over distortions 0.983 / 0.955 | Temporal tamper localization (swap/insert/drop) 1.000 MS, ~0.936 SVD; spatial localization ~0.76–0.91 | Diffusion T2V/I2V; DDIM inversion (25–50 steps) at extraction | hurunyi/VideoShield |
| VideoMark (arXiv 2504.16359, preprint, cs.CR) | Initial noise, frame-wise PRC, random start index into a fixed sequence | 512 bits/frame | Own paper: swap/insert/drop ≈1.000 (T2V), 0.991–0.997 (I2V) | Temporal Matching Module (edit distance) aligns frames | Diffusion; DDIM inversion | KYRIE-LI11/VideoMark |
| Stable Signature (arXiv 2303.15435, ICCV 2023) | Fine-tuned LDM latent decoder | 48 bits (as used by VidSig) | >90% detection at FPR<1e-6 after crop to 10% of the image | Image method | LDM with VAE decoder | facebookresearch/stable_signature |
| Tree-Ring (arXiv 2305.20030; venue not verified on page) | Fourier pattern in initial noise | Detection "fingerprint" (multi-bit not stated) | Claimed invariance to convolution, crop, dilation, flip, rotation | — | Diffusion + inversion | YuxinWenRick/tree-ring-watermark |
| Gaussian Shading (arXiv 2404.04956, CVPR 2024) | Watermark mapped to Gaussian-distributed latent (initial noise), "performance-lossless" | Not stated on fetched page | Claimed resilience to lossy processing | — | Diffusion + DDIM inversion | No link on arXiv page |
| WOUAF (arXiv 2306.04744, CVPR 2024) | Per-user fingerprint weight modulation of a fine-tuned SD model | Not stated on fetched page | +11% average vs. baselines under post-processing | — | T2I diffusion | kylemin/WOUAF |
| LoT-Pass / I2VWM (arXiv 2509.17773, ECCV 2026 per arXiv comments) | Post-hoc image watermark on the I2V conditioning image (JND-modulated residual) | 32 bits | Accuracy decays over generated frames; RDD (first frame below 0.9) Kling 120, Hailuo 47; CogVideoX VACC/RDD 0.966/49 → 0.910/13 at 20% frame drop; SVD 0.823/1 | Optical-flow (RAFT) alignment to the first frame at extraction | Any I2V model (open and commercial) | Two repo names seen (see below) |
| WaTeRFlow (arXiv 2512.19048, preprint) | Post-hoc image encoder/decoder trained with I2V proxy (FUSE) + flow-warp temporal consistency loss | Not stated | Abstract only: "higher first-frame and per-frame bit accuracy" | — | Any I2V model | Not found |
| MoSign (arXiv 2609.29603, preprint) | Style latent of a motion VAE, keystream-whitened Gaussian Shading | Keyed MAC over epoch counter + session nonce + context | 0.96 codeword accuracy (projected 2D), 0.81 through full render-to-video loop; 0.99 through a real anonymizer | Time-varying keyed message; sequential test | Motion-VAE-based avatar motion pipelines | Not found |

**VideoSeal** ([arXiv abs](https://arxiv.org/abs/2412.09492), [HTML](https://arxiv.org/html/2412.09492v1))
- Fernandez, Elsahar, Yalniz, Mourachko (Meta). Submitted 12 Dec 2024. The arXiv page lists no peer-reviewed venue. Code is at [facebookresearch/videoseal](https://github.com/facebookresearch/videoseal) — [arXiv abs](https://arxiv.org/abs/2412.09492)
- The embedder is an efficient U-Net (~16M params) at 256×256 with the message injected in the bottleneck. The extractor is ViT-Small (~22M params, patch 16). The default payload is 96 bits — [HTML](https://arxiv.org/html/2412.09492v1)
- Temporal propagation: the embedder runs every k-th frame (k=4) and its distortion is copied to the next k−1 frames. Large k causes "shadow" artifacts under high motion. Extraction decodes each frame and averages soft predictions across frames — [HTML](https://arxiv.org/html/2412.09492v1)
- Table 4 (SA-V **real** videos, not generated): identity 0.99 bit accuracy (log10 p −26.8), valuemetric 0.90, geometric 0.85, H.264/H.265 compression 0.85 (log10 p −15.7), combined 0.73 (−8.1). The text cites log10 p = −6.1 for H.264 CRF30 + brightness + 50% crop — [HTML](https://arxiv.org/html/2412.09492v1)
- The paper does not evaluate frame drop or reordering, per-frame unique messages, or temporal tamper detection (in the 100k characters read) — [HTML](https://arxiv.org/html/2412.09492v1)
- Imperceptibility on SA-V: PSNR 48.02, SSIM 0.998, LPIPS 0.013, VMAF 93.77 — [HTML](https://arxiv.org/html/2412.09492v1)
- **Conflict, VideoSeal clean accuracy as measured by others:** about 0.999 on ModelScope (as reported by [SPDMark](https://arxiv.org/html/2512.12090v2)); 0.975/0.979 on MS/SVD (as reported by [VidSig](https://arxiv.org/html/2506.00652v4)); 0.964/0.982 on T2V/I2V (as reported by [VideoMark](https://arxiv.org/html/2504.16359v3)). VideoMark also reports VideoSeal at only **0.565** under "resolution compression" on T2V — [VideoMark HTML](https://arxiv.org/html/2504.16359v3)
- Average robust bit accuracy as reported by SPDMark: VideoSeal 0.912 (SVD-XT) / 0.906 (ModelScope) — [SPDMark HTML](https://arxiv.org/html/2512.12090v2)

**SIGMark** ([arXiv abs](https://arxiv.org/abs/2603.02882), [HTML](https://arxiv.org/html/2603.02882v1))
- Zhu, Zhao, Jin, Guo, Ma, Wang, Guo, Zhang. Submitted 3 Mar 2026. "Accepted to ICLR 2026" per the arXiv comments field — [arXiv abs](https://arxiv.org/abs/2603.02882)
- Embedding is in the initial noise via a Global set of Frame-wise PRC keys (GF-PRC), which preserves the noise distribution ("distortion-free"). It targets video diffusion models with causal 3D VAEs — [arXiv abs](https://arxiv.org/abs/2603.02882)
- Payload is 512 bits repeated per causal frame group, or distinct 512 bits per group (512×16 = 8,192 bits for 65-frame 512×512 videos; the first frame is not watermarked) — [HTML](https://arxiv.org/html/2603.02882v1)
- Generators: HunyuanVideo and Wan-2.2 in T2V and I2V modes — [HTML](https://arxiv.org/html/2603.02882v1)
- "Blind" extraction means only the global PRC keys are stored, with no per-video message database. Extraction still runs the causal 3D VAE encoder, then flow-matching Euler inversion (empty prompt), then PRC decoding of latent signs — [HTML](https://arxiv.org/html/2603.02882v1)
- HunyuanVideo I2V bit accuracy: SIGMark clean 0.98, Gaussian noise 0.89, MPEG 0.84, blur 0.95, temporal clean 0.91, drop-30 0.81, insert-30 0.87, clip-30 0.85. VideoShield in the same table: 1.00 / 1.00 / 0.99 / 1.00 / 0.99 / 0.89 / 0.84 / 0.83. VideoMark: 0.85 / 0.64 / 0.63 / 0.64 / 0.71 / 0.52 / 0.51 / 0.51 — [HTML](https://arxiv.org/html/2603.02882v1)
- **Note:** in SIGMark's own table, VideoShield equals or beats SIGMark on almost every column except insert and clip. SIGMark's claimed advantage is scalability: constant-cost blind extraction vs. VideoShield's extraction time growing linearly with the number of stored videos (its Fig. 5) — [HTML](https://arxiv.org/html/2603.02882v1)
- Swap and crop are claimed but not quantified in the portion read. Wan-2.2 results (Appendix D) were not retrieved — [HTML](https://arxiv.org/html/2603.02882v1)

**SPDMark** ([arXiv abs](https://arxiv.org/abs/2512.12090), [HTML v2](https://arxiv.org/html/2512.12090v2))
- Fares, Tastan, Nandakumar. v1 12 Dec 2025, v2 1 Apr 2026. "CVPR 2026" per the arXiv comments field — [arXiv abs](https://arxiv.org/abs/2512.12090)
- Only the VAE decoder is modified, with 4 parallel rank-32 LoRA bases on each of 14 spatial ResNet blocks and one basis active per block. This gives 28 bits/frame (14 × log2 4). It adds ~2M params and <5% decoding overhead — [HTML](https://arxiv.org/html/2512.12090v2)
- Generators: SVD-XT (I2V) and ModelScope (T2V) — [HTML](https://arxiv.org/html/2512.12090v2)
- Robustness (SVD-XT / ModelScope): crop 0.989/0.978, color jitter 0.993/0.981, frame drop 0.988/0.969, swap 0.994/0.986, insert 0.994/0.986, recompression 0.880/0.986, screen recording 0.837/0.821, average 0.935/0.939 — [HTML](https://arxiv.org/html/2512.12090v2)
- Average robust bit accuracy as reported by SPDMark: VideoShield 0.833/0.886, VidSig 0.685/0.812 — [HTML](https://arxiv.org/html/2512.12090v2)
- The abstract page lists no code, but the HTML paper links [github.com/Samar-Fares/SPDMark](https://github.com/Samar-Fares/SPDMark) — [HTML](https://arxiv.org/html/2512.12090v2)

**VidSig / Video Signature** ([arXiv abs](https://arxiv.org/abs/2506.00652), [HTML v4](https://arxiv.org/html/2506.00652v4))
- Huang, Chen, Liu, Li, Li, Zheng, Liu, Fung, Hu. v1 31 May 2025, v4 16 Nov 2025. No venue stated — [arXiv abs](https://arxiv.org/abs/2506.00652)
- Partially fine-tunes the latent decoder. Perturbation-Aware Suppression (PAS) scores each layer's sensitivity to Gaussian perturbation and freezes sensitive ones. A temporal alignment module adds coherence — [arXiv abs](https://arxiv.org/abs/2506.00652); [HTML](https://arxiv.org/html/2506.00652v4)
- Payload is 48 bits, read per frame by the Stable Signature extractor and majority-voted. Generators: ModelScope and SVD, with transfer to Latte — [HTML](https://arxiv.org/html/2506.00652v4)
- H.264 on SVD: CRF20 BA 0.894 / TPR@1e-4 0.880; CRF23 BA 0.869 / 0.840. Temporal edits (drop, swap, insert, Gaussian insert, frame averaging) leave BA ≈0.992 (MS) / 0.999 (SVD). Crop is not reported — [HTML](https://arxiv.org/html/2506.00652v4)
- Timing reported by VidSig (units not stated; ModelScope): VideoShield Ti 26.994 / Te 6.224; VideoSeal 0.121 / 0.036; Stable Signature and VidSig 0.000 / 0.008 — [HTML](https://arxiv.org/html/2506.00652v4)

**VideoShield** ([arXiv abs](https://arxiv.org/abs/2501.14195), [HTML v2](https://arxiv.org/html/2501.14195v2))
- Hu, Zhang, Li, Li, Guo, Qiu, Zhang. ICLR 2025. Training-free. Watermark bits are mapped to template bits that generate the initial noise. Extraction and tamper detection use DDIM inversion. Covers T2V and I2V — [arXiv abs](https://arxiv.org/abs/2501.14195)
- 512 bits per video. Template repetition is 8,1,4,4 for ModelScope (128 copies per bit) and 8,1,8,8 for SVD (512 copies). Tested on ModelScope, SVD, ZeroScope, I2VGen-XL and SD 1.4/1.5/2.1 — [HTML](https://arxiv.org/html/2501.14195v2)
- Clean BA 1.000 (MS) / 0.999 (SVD). Average over MPEG-4, frame averaging, swap, noise, blur, resize, crop and brightness is 0.983 / 0.955 — [HTML](https://arxiv.org/html/2501.14195v2)
- Temporal tamper localization accuracy (swap/insert/drop): ModelScope 1.000 for each; SVD 0.935/0.937/0.936. Spatial localization averages 0.886–0.906 (MS) and 0.755–0.790 (SVD) — [HTML](https://arxiv.org/html/2501.14195v2)
- Code: [hurunyi/VideoShield](https://github.com/hurunyi/VideoShield) — [arXiv abs](https://arxiv.org/abs/2501.14195)
- **Conflict:** VidSig states VideoShield "requires the frame count and resolution to match exactly for detection" ([VidSig HTML](https://arxiv.org/html/2506.00652v4)). VideoMark says VideoShield cannot decode variable-frame videos and leaves its temporal results blank in Table 1, yet reports ~0.98 I2V matching accuracy for it in Table 4 ([VideoMark HTML](https://arxiv.org/html/2504.16359v3)). VideoShield's own paper reports localization of swap, insert and drop ([VideoShield HTML](https://arxiv.org/html/2501.14195v2)).

**VideoMark** ([arXiv abs](https://arxiv.org/abs/2504.16359), [HTML v3](https://arxiv.org/html/2504.16359v3))
- Hu, Li, Li, Huang, Liu, Zheng, Chen, Liu. v1 23 Apr 2025, v3 16 Nov 2025. arXiv cs.CR, no venue listed. Training-free. Frame-wise PRC codes in the initial noise, with a fixed watermark sequence and a random start index per video. Code at [KYRIE-LI11/VideoMark](https://github.com/KYRIE-LI11/VideoMark) — [arXiv abs](https://arxiv.org/abs/2504.16359)
- 512 bits per frame. ModelScope (16 frames) and I2VGen-XL (15 watermarked frames). DDIM inversion at extraction. Detection threshold p-value τ = 0.005 — [HTML](https://arxiv.org/html/2504.16359v3)
- Own results (T2V / I2V): swap 1.000/0.997, insert 1.000/0.991, drop 1.000/0.997, blur 1.000/0.857, color jitter 1.000/0.955, resolution compression 1.000/0.921. MPEG-4 and crop not tested — [HTML](https://arxiv.org/html/2504.16359v3)
- **Conflict:** on HunyuanVideo, SIGMark measures VideoMark at 0.85 clean and 0.51–0.52 under temporal disturbances ([SIGMark HTML](https://arxiv.org/html/2603.02882v1)), versus ≈1.000 in VideoMark's own ModelScope experiments. The generator differs (HunyuanVideo vs. ModelScope/I2VGen-XL).

**Image-generator watermarks (Stable Signature, Tree-Ring, Gaussian Shading, WOUAF)**
- Stable Signature: Fernandez et al., ICCV 2023. It "quickly fine-tunes the latent decoder." After cropping to 10% of the content it keeps >90% detection at FPR <1e-6. Code at [facebookresearch/stable_signature](https://github.com/facebookresearch/stable_signature) — [arXiv abs](https://arxiv.org/abs/2303.15435)
- Stable Signature's extractor carries a 48-bit message (as used by VidSig) — [VidSig HTML](https://arxiv.org/html/2506.00652v4)
- Tree-Ring: Wen, Kirchenbauer, Geiping, Goldstein. A pattern in Fourier space of the initial noise, detected by inverting diffusion. Claimed invariance to convolutions, crops, dilations, flips and rotations, with negligible FID loss. Code at [YuxinWenRick/tree-ring-watermark](https://github.com/YuxinWenRick/tree-ring-watermark). The arXiv page lists no venue — [arXiv abs](https://arxiv.org/abs/2305.20030)
- Gaussian Shading: Yang et al., CVPR 2024. Maps the watermark to a standard-Gaussian latent and extracts it via DDIM inversion. "Provable performance-lossless" — [arXiv abs](https://arxiv.org/abs/2404.04956)
- WOUAF: Kim, Min, Patel, Cheng, Yang, CVPR 2024. Weight modulation of SD by per-user fingerprint, with an 11% average improvement under post-processing. Code at [kylemin/WOUAF](https://github.com/kylemin/WOUAF) — [arXiv abs](https://arxiv.org/abs/2306.04744)

**LoT-Pass / I2VWM** ([arXiv abs](https://arxiv.org/abs/2509.17773), [HTML v3](https://arxiv.org/html/2509.17773v3))
- The current arXiv title (v3, 24 Jun 2026) is "LoT-Pass: Long-term-robust Image Watermarking for Image to Video Generation" by Wang, Ma, Fang, Zhang. I2VWM is the framework name. "Accepted to ECCV 2026" per the comments field — [arXiv abs](https://arxiv.org/abs/2509.17773)
- 32-bit message. Embedding is I_wm = I_o + λ·JND(I_E − I_o), with residual rescaling for arbitrary resolutions. Training uses a video-simulation noise layer, and inference uses RAFT optical-flow alignment of each frame to the first — [HTML](https://arxiv.org/html/2509.17773v3)
- Robust Diffusion Distance (RDD) is the first frame index where frame-averaged accuracy drops below 0.9. All methods decline with temporal distance from the first frame, and for some baselines "the watermark signal is completely removed in most frames." Baselines: SSLWM, CIN, MuST, VINE-R, TrustMark, Robust-Wide, WAM. VideoSeal is not compared — [HTML](https://arxiv.org/html/2509.17773v3)
- Code is listed as [MrCrims/I2VWM-Robust-Watermarking-for-Image-to-Video-Generation](https://github.com/MrCrims/I2VWM-Robust-Watermarking-for-Image-to-Video-Generation) on the abstract page ([arXiv abs](https://arxiv.org/abs/2509.17773)) and as [MrCrims/LoT-Pass-Long-term-robust-Image-Watermarking-for-Image-to-Video-Generation](https://github.com/MrCrims/LoT-Pass-Long-term-robust-Image-Watermarking-for-Image-to-Video-Generation) in the HTML ([HTML](https://arxiv.org/html/2509.17773v3)). The repo was likely renamed.

**WaTeRFlow** ([arXiv abs](https://arxiv.org/abs/2512.19048))
- Jeong et al. (incl. Seungryong Kim), 22 Dec 2025, preprint. It has three parts: FUSE, which exposes the encoder/decoder to instruction-driven edits and a fast video-diffusion proxy; an optical-flow-warp temporal consistency loss; and a semantic preservation loss. It claims higher first-frame and per-frame bit accuracy across I2V models. No numbers or code were found on the abstract page — [arXiv abs](https://arxiv.org/abs/2512.19048)

**Other related 2024–2026 methods found**
- GenPTW (arXiv 2504.19567): latent image watermarking for provenance tracing and tamper localization — [arXiv PDF](https://arxiv.org/pdf/2504.19567) (title only seen; not analysed)
- DistSeal (arXiv 2601.16140): distils a watermark into diffusion or autoregressive generators so no post-hoc step is needed — [arXiv HTML](https://arxiv.org/html/2601.16140v1) (from a search summary; not fetched)

### Inferences
- The VideoSeal robustness table uses real SA-V footage. Its numbers on generated or reenacted faces may differ, and VideoMark's 0.565 under resolution compression suggests VideoSeal can be fragile to rescaling pipelines.
- The noise-inversion family (VideoShield, VideoMark, SIGMark, Tree-Ring, Gaussian Shading) has the best clean and temporal numbers, but verification costs a full inversion through the generator (minutes per video, and the model must be available to the verifier).
- Decoder-tuning methods (SPDMark, VidSig, Stable Signature) verify with a lightweight extractor (VidSig reports Te ≈ 0.008, units not stated). SPDMark adds per-frame keyed messages, so this family offers the best balance of cost, temporal integrity and robustness among published methods.

### Gaps
- Payload sizes for Gaussian Shading and WOUAF were not stated on the fetched abstract pages, so they are not reported.
- No single crop or MPEG-4 numbers for VideoShield were found in the text (they are only in figures). VideoMark did not test MPEG-4 or crop. SIGMark crop and swap results were not quantified in the portion read.
- WaTeRFlow: no quantitative results, venue or code were found.
- The Tree-Ring venue was not verified from the arXiv page (it is commonly cited as NeurIPS 2023, but that was not confirmed here).
- No head-to-head benchmark puts all methods on the same generator and attack suite. Cross-paper numbers are not directly comparable.

---

## Q2. Which methods support frame-specific messages and recovering frame order / detecting frame deletion, insertion, reordering?

### Takeaway
Three generation-time methods have explicit per-frame or per-group messages plus order recovery: **SPDMark** (HMAC-derived per-frame messages + Hungarian matching, F1 ≈0.995–0.999), **VideoMark** (frame-wise PRC sequence + edit-distance alignment) and **SIGMark** (per-group PRC + optical-flow Segment Group-Ordering). **VideoShield** localizes temporal tampering via template bits. **VideoSeal** and **VidSig** embed the same message in every frame and only *survive* temporal edits; they do not *detect* them.

### Cited Findings
- SPDMark derives each frame's message from a base key with HMAC-SHA256. It matches extracted to expected messages by maximum-weight bipartite matching (Hungarian), with edge weights equal to the fraction of matching bits, and keeps a pair only if it passes frame- and video-level binomial tests — [SPDMark HTML](https://arxiv.org/html/2512.12090v2)
- SPDMark temporal localization: frame drop P/R/F1 ≈0.999 (SVD-XT) and ≈0.998/0.999/0.999 (ModelScope); frame insert F1 0.995 (SVD-XT) and 0.999 (MS); random and adjacent swap order accuracy 1.000 — [SPDMark HTML](https://arxiv.org/html/2512.12090v2)
- VideoMark uses a fixed watermark sequence with a random start index per video. Its Temporal Matching Module uses edit distance (match/insert/delete/substitute) to align decoded frame messages. I2V frame-matching accuracy: swap 0.996, insert 0.989, drop 0.996 — [VideoMark HTML](https://arxiv.org/html/2504.16359v3)
- SIGMark's per-group distinct-message mode carries 512 bits × 16 groups. Segment Group-Ordering uses Farnebäck optical flow (flow magnitude, forward-backward consistency, motion-compensated residual, speed change) to find cut points, then sliding-window inversion to recover group indices. Without SGO, extraction under 30 inserted frames drops from 0.869 to 0.534 — [SIGMark HTML](https://arxiv.org/html/2603.02882v1)
- VideoShield localizes temporal tampering (swap/insert/drop) at 1.000 on ModelScope and ~0.936 on SVD, and also localizes spatial tampering — [VideoShield HTML](https://arxiv.org/html/2501.14195v2)
- VidSig embeds the watermark in every frame and aggregates by majority vote. Temporal edits leave BA ≈0.99, but there is no per-frame message or localization — [VidSig HTML](https://arxiv.org/html/2506.00652v4)
- VideoSeal averages soft bits over frames, and its paper does not evaluate frame drop or reorder or describe per-frame messages — [VideoSeal HTML](https://arxiv.org/html/2412.09492v1)
- MoSign embeds a *time-varying* keyed MAC over an epoch counter and session nonce, which gives replay resistance. This is a temporal-integrity feature on a motion channel — [MoSign arXiv](https://arxiv.org/abs/2609.29603)

### Inferences
- SPDMark's design (keyed per-frame message → per-frame extractor → bipartite matching) is the most portable to a non-diffusion reenactment generator, because it needs only a decoder that emits frames one at a time. LivePortrait's SPADE generator does exactly that (see Q4).
- A post-hoc per-frame scheme can be built on VideoSeal by embedding a different 96-bit payload per frame (e.g., truncated HMAC(key, video_id‖frame_idx) plus a frame index) and reusing SPDMark-style matching. This is my inference; the VideoSeal paper does not evaluate it. Two caveats: VideoSeal's temporal propagation (copying the residual across k frames) and cross-frame averaging would have to be disabled, and single-frame accuracy is lower than multi-frame averaged accuracy.

### Gaps
- No method reports detection of frame *duplication* or *speed change* (frame-rate resampling) as a separate class.
- Per-frame bit accuracy without cross-frame averaging is not reported for VideoSeal in the portion read.

---

## Q3. Has anyone watermarked a talking-head or portrait-animation generator (motion latent, keypoints, warping field, decoder, or fine-tuning)? Include MoSign and analogs. Does a watermark in the source portrait survive reenactment?

### Takeaway
No peer-reviewed or arXiv work was found that embeds a watermark *inside* a talking-head or face-reenactment generator (LivePortrait, FOMM, GAGAvatar, Hallo, EchoMimic, X-Portrait, HunyuanPortrait). The closest analogs are MoSign (keyed watermark in a motion-VAE latent, but for body/VR motion, not faces), the proactive face watermarks LampMark and LIDMark, and I2V conditioning-image watermarks (LoT-Pass, WaTeRFlow). The evidence on source-portrait survival is mixed. LampMark's watermark drops to about 73–75% bit accuracy after GAN reenactment (vs. 92–99.9% after face swap), so exact payload recovery fails, but presence detection likely still works (my binomial estimate: p ≈ 1e-8 at 128 bits). LivePortrait's default paste-back copies non-face pixels from the source, so a source mark would likely persist there. Such a surviving mark only proves which source was used; it cannot tell a genuine output from a reenacted one.

### Cited Findings
- Searches for watermarking in talking-head or portrait-animation generators returned only calls for it. A 2023 survey argues provenance and watermarking "should be considered part of the generation pipeline rather than optional post-processing" — [From Pixels to Portraits survey](https://arxiv.org/html/2308.16041v2). The EditYourself paper recommends "robust digital watermarking" among safeguards — [EditYourself arXiv 2601.22127](https://arxiv.org/pdf/2601.22127)
- The LivePortrait paper mentions deepfake risks and the need for ethical guidelines, but describes no watermark or technical safeguard — [LivePortrait HTML](https://arxiv.org/html/2407.03168)
- **MoSign** (Che, Carr, Xu, Lu, Yuan; arXiv 2609.29603, cs.CR, preprint; the abstract page says submitted 30 Aug 2026)
  - Method: watermarking as challenge-response authentication on the motion channel. A time-varying keyed message is embedded in the style latent of a motion VAE using keystream-whitened Gaussian Shading. A key-holding verifier runs a sequential test — [MoSign arXiv](https://arxiv.org/abs/2609.29603)
  - Datasets are HumanML3D (body motion) and BOXRR-23 (VR telemetry), **not faces**. FAR 10⁻⁴ for legitimate users; detection AUC by non-key holders 0.51 (chance 0.5); 0.99 codeword accuracy through a real anonymizer — [MoSign arXiv](https://arxiv.org/abs/2609.29603)
  - Recapture threat (render → record → re-estimate pose): a *generic pose estimator removes the watermark*, while a recapture-robust keyed reader recovers 0.96 codeword accuracy on a projected-2D channel and 0.81 through a full render-to-video loop — [MoSign arXiv](https://arxiv.org/abs/2609.29603)
  - No code link on the arXiv page — [MoSign arXiv](https://arxiv.org/abs/2609.29603)
  - Date note: the arXiv ID prefix (2609) reflects the September 2026 announcement month, which is consistent with a 30 Aug 2026 (Sunday) submission.
- **LampMark** (ACM MM 2024; arXiv 2411.17209)
  - Method: a training-free landmark-perceptual watermark. Facial landmarks are converted to a binary watermark (Rule-30 CA encryption) and embedded into the image to be protected. A deepfake is flagged when recovered landmarks mismatch the suspect image — [LampMark HTML](https://arxiv.org/html/2411.17209v1)
  - Payload is 64 bits at 128×128 and 128 bits at 256×256 — [LampMark HTML](https://arxiv.org/html/2411.17209v1)
  - Survival after manipulation of the watermarked image (128 / 256 px): SimSwap 99.95/99.98%, InfoSwap 97.99/98.31%, UniFace 99.72/94.28%, E4S 92.09/93.27%; **reenactment** StarGAN 73.12/74.66%, StyleMask 74.19/75.83%, HyperReenact 73.53/74.18%. The authors attribute the reenactment drop to loss of background information — [LampMark HTML](https://arxiv.org/html/2411.17209v1)
  - FOMM, TPSMM and LivePortrait-style keypoint reenactors were not evaluated — [LampMark HTML](https://arxiv.org/html/2411.17209v1)
- **LIDMark** (Wu, Wang, Guo; arXiv 2602.23523, CVPR 2026): a 152-dimensional watermark combining facial landmarks and a source identifier. A Factorized-Head Decoder splits it into a regression head (landmarks → detection and localization) and a classification head (ID → source tracing). Code at [vpsg-research/LIDMark](https://github.com/vpsg-research/LIDMark). The abstract does not say whether reenactment is covered — [arXiv abs](https://arxiv.org/abs/2602.23523)
- Identity-perceptual watermark (Wang et al., arXiv 2311.01357) targets face swapping with an adversarially trained encoder/decoder — [arXiv PDF](https://arxiv.org/pdf/2311.01357). An ACM survey notes some works embed messages "into the identity representation" to counter swapping or reenactment — [ACM survey on proactive deepfake defense](https://dl.acm.org/doi/10.1145/3771296)
- **Conditioning-image survival in I2V** (closest analog to "source portrait → reenacted video")
  - LoT-Pass/I2VWM: all tested image watermarks decline with temporal distance from the first frame. For some baselines "the watermark signal is completely removed in most frames." SVD's RDD is only 1 even for LoT-Pass (VACC 0.823) — [LoT-Pass HTML](https://arxiv.org/html/2509.17773v3)
  - WaTeRFlow targets the same problem with flow-consistency training — [WaTeRFlow arXiv](https://arxiv.org/abs/2512.19048)
- **3D Gaussian Splatting watermarks** are per-scene or per-asset, not avatar generators. GuardSplat embeds in spherical-harmonic features ([arXiv 2411.19895](https://arxiv.org/html/2411.19895v5)). 3D-GSW protects the model and its renders ([arXiv 2409.13222](https://arxiv.org/html/2409.13222v4)). CompMarkGS reports that existing 3DGS watermarks degrade under 3DGS compression ([arXiv 2503.12836](https://arxiv.org/html/2503.12836v5)). GaussianSeal claims the first bit watermark for 3DGS *generative* models ([arXiv 2503.00531 via papers.cool](https://papers.cool/arxiv/2503.00531); summary only). None targets GAGAvatar-style animatable heads — [search summary incl. GS-Marker](https://arxiv.org/pdf/2503.18718)
- **Older motion-data watermarking:** wavelet watermarks on joint trajectories, SVD-domain mocap watermarks, skin-weight/keyframe watermarks, and fragile watermarks on motion curves — [UNR Motwani et al. papers](https://www.cse.unr.edu/~fredh/papers/journal/31-woscuwd/paper.pdf); [USPTO 9922392](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9922392). A KIST record titled "A watermarking method for face animation parameters obtained by motion estimation" exists — [KIST](https://pubs.kist.re.kr/handle/201004/106690) (title only; **unverified**, content not read)
- Generator-side ("parameter-based") watermarking is established in speech synthesis, with vocoder weights modulated or fine-tuned (RIWF, HFGw). These bind the mark to the trained model and require retraining to change it — [arXiv 2610.04235](https://arxiv.org/html/2610.04235)

### Inferences
- Watermarking a reenactment generator's decoder or motion latent appears to be an open gap as of Oct 2026, so a project that does it would be novel. The closest templates are SPDMark (decoder LoRA keyed per frame) and MoSign (keyed motion-latent).
- **Exact recovery vs. detection.** LampMark's ~74% reenactment bit accuracy means exact payload recovery fails, but *presence detection* likely still works. Assuming independent bit errors (my calculation, not the paper's), ≥95/128 correct bits has a binomial tail p ≈ 1.9×10⁻⁸, and ≥47/64 has p ≈ 1.1×10⁻⁴. A zero-bit or keyed-detection use of a source mark is therefore more viable than a multi-bit payload.
- **Whether LivePortrait is more or less destructive than LampMark's reenactors is unknown.** Two considerations pull in opposite directions:
  - StyleMask and HyperReenact re-synthesize through StyleGAN inversion. LivePortrait instead warps the source's own appearance feature volume, which may preserve more source texture.
  - LivePortrait's SPADE decoder still regenerates the face pixels, and I2V conditioning watermarks decay over frames (LoT-Pass).
  - LivePortrait was not evaluated in any paper found.
- **Paste-back (LivePortrait default):** pixels outside the face region come from the source image, so a source-portrait mark would largely persist there. LampMark's authors blame their reenactment drop on lost background information, which is consistent with this. However, such a surviving mark proves only "derived from this source image". A genuine and a reenacted output both carry it, so it cannot verify *whether* reenactment happened or who drove it. Verification needs a generator-side or motion-bound mark.
- MoSign's recapture result implies that a watermark placed only in LivePortrait's implicit keypoints would be lost if a verifier re-extracts keypoints with the stock motion extractor. A dedicated keyed reader trained through the render loop would be needed, and even then the analogous accuracy was ~0.81.
- LampMark/LIDMark's "semi-fragile + semantic consistency" idea (the watermark encodes landmarks, so a mismatch reveals manipulation) could be repurposed for reenactment *verification*. A generator could embed the driving landmarks or keypoints it actually used, so any later re-driving or editing produces a mismatch.

### Gaps
- No talking-head-specific watermarking paper was found. Searches might miss non-English venues or workshop papers.
- No measurement of any watermark surviving LivePortrait, FOMM, GAGAvatar or diffusion portrait animators was found.
- MoSign's face applicability is untested; no code found.
- LIDMark's evaluated manipulation models were not retrieved.

---

## Q4. For an open-source non-diffusion model like LivePortrait (and GAGAvatar / diffusion portrait models), what are concrete feasible embedding options and their trade-offs?

### Takeaway
For LivePortrait the most practical option is **SPDMark/Stable-Signature-style fine-tuning (or LoRA) of the SPADE generator/decoder** with keyed per-frame messages and a separately trained extractor. It needs no noise latent, adds ~zero inference cost, and supports frame-order verification. **Post-hoc VideoSeal** is the zero-training baseline (96 bits, cheap, but no temporal integrity unless engineered). **Keypoint perturbation** is low-capacity and fragile to recapture. Noise-inversion methods (VideoShield, VideoMark, SIGMark, Tree-Ring, Gaussian Shading) are **not applicable** to LivePortrait or GAGAvatar but apply in principle to diffusion portrait animators (HunyuanPortrait on SVD; Hallo, EchoMimic and X-Portrait on pre-trained image-diffusion backbones). A mark on the source portrait largely survives in LivePortrait's pasted-back background, but it cannot tell a genuine output from a reenacted one. For open weights, every in-model option can be removed by swapping in the original weights.

### Cited Findings
- **LivePortrait architecture**
  - Components: an appearance feature extractor (3D feature volume); a single ConvNeXt-V2-Tiny motion extractor predicting canonical keypoints, head pose, expression deformation, scale and translation; a warping module; and a SPADE decoder generator with PixelShuffle upsampling from 256 to 512 px — [LivePortrait HTML](https://arxiv.org/html/2407.03168)
  - Stitching MLP [126,128,128,64,65], eye retargeting MLP, lip retargeting MLP — [LivePortrait HTML](https://arxiv.org/html/2407.03168)
  - Keypoint count is not stated explicitly; the 63-dimensional retargeting outputs imply K=21 (**inferred**, not stated) — [LivePortrait HTML](https://arxiv.org/html/2407.03168)
  - Speed and training: 12.8 ms/frame on RTX 4090. Training on ~69M frames, ~18.9K identities. Stage I took 8×A100 for ~10 days; Stage II (stitching/retargeting) ~2 days with the rest frozen — [LivePortrait HTML](https://arxiv.org/html/2407.03168)
  - The public inference config defaults to `flag_do_crop = True` ("crop the source portrait or video to the face-cropping space") and `flag_pasteback = True` ("paste-back/stitch the animated face cropping from the face-cropping space to the original image space"), with `flag_stitching = True` — [LivePortrait argument_config.py](https://raw.githubusercontent.com/KwaiVGI/LivePortrait/main/src/config/argument_config.py)
- **SPDMark template for decoder watermarking:** LoRA only in 14 decoder ResNet blocks (~2M params, <5% decode overhead). Trained ~8 GPU-hours on one A6000 (6,000 steps, batch 1, 10k OpenVid videos) with message-recovery, perceptual and temporal-consistency losses. Achieved 28 bits/frame and the robustness in Q1 — [SPDMark HTML](https://arxiv.org/html/2512.12090v2)
- **Stable Signature template:** "quickly fine-tunes the latent decoder"; >90% detection after crop to 10% at FPR <1e-6 — [Stable Signature arXiv](https://arxiv.org/abs/2303.15435)
- **VidSig template:** freeze perceptually sensitive decoder layers (PAS) and fine-tune the rest, on 1 A800 — [VidSig HTML](https://arxiv.org/html/2506.00652v4)
- **WOUAF template:** per-user weight modulation enables user attribution (multiple users from one model) — [WOUAF arXiv](https://arxiv.org/abs/2306.04744)
- **Post-hoc VideoSeal:** 96 bits; embedding ~0.42 s GPU / 1.14 s CPU per second of video; extraction ~0.11 s GPU; works on any frames — [VideoSeal HTML](https://arxiv.org/html/2412.09492v1)
- **Motion-latent template (MoSign):** keyed Gaussian-Shading in a motion VAE latent is statistically undetectable without the key, but generic re-estimation strips it — [MoSign arXiv](https://arxiv.org/abs/2609.29603)
- **GAGAvatar** (Chu & Harada, NeurIPS 2024): one-shot dual-lifting produces 3D Gaussians from a single image with 3DMM priors. Splatted coarse results are refined by a **neural renderer**. Only a small driving part re-runs per frame. Code at [xg-chu/GAGAvatar](https://github.com/xg-chu/GAGAvatar) — [GAGAvatar arXiv](https://arxiv.org/html/2410.07971v1)
- **HunyuanPortrait** uses Stable Video Diffusion as its backbone, with adapter layers injecting implicit motion conditions into the denoising UNet — [HunyuanPortrait arXiv](https://arxiv.org/pdf/2503.18860)
- **EchoMimic** extends Stable Diffusion image techniques to video (denoising UNet, reference UNet, motion modules, face locator) — [EchoMimic arXiv](https://arxiv.org/pdf/2407.08136); component list from a third-party model card — [PromptLayer](https://www.promptlayer.com/models/echomimic)
- **Hallo** is an end-to-end diffusion model with UNet denoiser, reference network and temporal alignment — [Hallo arXiv HTML](https://arxiv.org/html/2406.08801v2). "Built on Stable Diffusion" comes from a GitHub-based project summary — [sourcepulse](https://www.sourcepulse.org/projects/1843418). Other details (EMO latent diffusion framework, wav2vec last-12-layer embeddings) come from a third-party review — [themoonlight.io review](https://www.themoonlight.io/en/review/hallo-hierarchical-audio-driven-visual-synthesis-for-portrait-image-animation)
- **X-Portrait** (Xie et al., SIGGRAPH 2024 per arXiv comments) is a conditional diffusion model that uses "the generative prior of a pre-trained diffusion model as the rendering backbone." Head pose and expression control are built "within the framework of ControlNet," plus a patch-based local control module. The abstract does not name the specific SD version — [X-Portrait arXiv](https://arxiv.org/abs/2403.15931)

### Inferences

**Option matrix for LivePortrait (all inferences grounded in the templates above)**

| Option | How | Capacity / temporal integrity | Robustness expectation | Cost | Main risks |
|---|---|---|---|---|---|
| A. Decoder (SPADE generator) fine-tune or LoRA, à la Stable Signature / SPDMark | Freeze F, M, W; train LoRA bases or partial weights in the SPADE decoder plus a separate extractor (or reuse a frozen extractor like Stable Signature/VidSig); key selects the basis per frame (SPDMark) | ~28–56 bits/frame (SPDMark-like), per-frame HMAC messages enable drop/insert/swap localization | Likely similar to SPDMark (~0.93 average, ~0.88 recompression, ~0.83 screen recording), but untested on faces | Training is plausibly in the GPU-hours range (SPDMark ~8 GPU-h on A6000 as an analogy, not a measurement); inference overhead small vs 12.8 ms/frame | Quality loss in fine facial detail (eyes, teeth) where SPADE is sensitive; open weights mean an attacker can swap back the original decoder |
| B. Perturb implicit keypoints, expression deltas or warping field | Add keyed small offsets to expression deformation or keypoints per frame (MoSign-like) | Very low capacity (tens of bits over many frames); temporal key schedule possible | Weak: re-extraction by the stock motion extractor is the "recapture" problem (MoSign: generic estimator strips the mark; keyed reader ~0.81 through render-to-video); visible motion jitter if strong | Cheap at inference; needs a learned keyed reader for verification | Motion artifacts; easily removed by smoothing keypoints; verifier must run a custom keypoint reader |
| C. Post-hoc VideoSeal on output frames | Run VideoSeal embedder on each output (or per-frame keyed payloads, disabling propagation) | 96 bits; per-frame keyed messages possible (inference) but unvalidated | Paper numbers: compression 0.85, combined 0.73 (real videos) | Cheap (~0.42 s GPU per second of video) | Separate step, trivially skipped in open-source code; no native temporal tamper detection |
| D. Watermark the source portrait before reenactment | Embed in the input image (LampMark / LoT-Pass style) | 32–128 bits | Face region: degraded (~74% after GAN reenactment in LampMark; decays over frames in I2V per LoT-Pass) but likely still detectable. Background/hair: likely survives via LivePortrait's default paste-back | Cheap | Only proves "derived from this source", which genuine and reenacted outputs share; cannot attest who generated or drove it. Breaks if the user disables paste-back or crops to the face |
| E. Appearance-feature-volume watermark | Train keyed perturbation of the 3D appearance feature volume so that it propagates through warping + decoder | Unknown | Unknown; no published precedent found | Moderate | Unexplored research direction |

- **Paste-back caveat (inference from the config cited below):** a decoder-level mark covers only the animated face crop, and the surrounding pixels come from the source. Verification must therefore re-detect and align the face crop, and face cropping and resizing become part of the attack model.
- **Open-weights limitation:** for any open-source generator, a decoder, LoRA or keypoint watermark can be removed by loading the original released weights, and a post-hoc step can be skipped. In-model watermarking therefore protects a specific *deployed* build (an API or a distributed binary), not the open model itself. This bounds the value of options A, B and E.
- **GAGAvatar:** the per-frame neural renderer is the analog of LivePortrait's SPADE decoder, so option A transfers directly. Embedding in the Gaussians themselves (GuardSplat-style SH features) would mark the per-identity avatar, not the generator, and must survive the neural renderer. That is unknown.
- **Diffusion portrait models (HunyuanPortrait on SVD; Hallo and EchoMimic SD-based; X-Portrait on an unnamed pre-trained diffusion backbone with ControlNet):**
  - Decoder methods (SPDMark, VidSig, Stable Signature) apply directly to their VAE decoders. HunyuanPortrait's SVD backbone means SPDMark, VideoShield and VidSig SVD-XT results are the most transferable evidence.
  - Noise methods (VideoShield, VideoMark, SIGMark, Tree-Ring, Gaussian Shading) are technically applicable, but verification needs inversion through the conditioned UNet. The verifier does not know the reference image, audio or pose conditioning, so inversion accuracy with unknown or empty conditioning is an open feasibility question. SIGMark uses an empty prompt for T2V/I2V, but portrait conditioning is stronger.
- **For cross-reenactment verification specifically:** option A combined with SPDMark-style per-frame keyed messages gives frame-level provenance and tamper localization. Combining it with LampMark/LIDMark-style semantic payloads (e.g., hashing the driving keypoints into the message) could also bind the content to the motion actually generated.

### Gaps
- No experiment found on fine-tuning a non-diffusion reenactment decoder (SPADE, FOMM, GAGAvatar renderer) for watermarking. All feasibility statements are by analogy.
- X-Portrait's exact backbone version (which SD) is not stated in its abstract, and the VAE details of EchoMimic and Hallo were not verified from primary sources.
- Whether perturbing LivePortrait keypoints yields any recoverable signal after rendering is untested.

---

## Q5. Compute requirements and code availability for each.

### Takeaway
Post-hoc and decoder-based methods are cheap at inference, with decoder methods also cheap to train (SPDMark ~8 GPU-hours on one A6000). Noise-inversion methods cost no training but need minutes of diffusion inversion per video at verification. Code is public for VideoSeal, SPDMark, SIGMark, VideoShield, VideoMark, Stable Signature, Tree-Ring, WOUAF, LoT-Pass/I2VWM, LIDMark and LivePortrait/GAGAvatar. No code was found for VidSig, WaTeRFlow, MoSign or LampMark.

### Cited Findings
- VideoSeal
  - Training: image pre-training on 500k SA-1B images for 800 epochs, then hybrid SA-V video training (51k videos, 32-frame clips) for the last 300 epochs, then extractor fine-tuning — [VideoSeal HTML](https://arxiv.org/html/2412.09492v1)
  - Inference per second of video: embedding ~42 GFLOPs (0.42 s GPU / 1.14 s CPU); extraction ~3.1 GFLOPs (0.11 s GPU / 0.69 s CPU) — [VideoSeal HTML](https://arxiv.org/html/2412.09492v1)
  - Code: [facebookresearch/videoseal](https://github.com/facebookresearch/videoseal)
- SPDMark: ~8 GPU-hours on 1×A6000 (6,000 steps, batch 1, 10k OpenVid-1M videos); +2M params, <5% decode overhead. Code: [Samar-Fares/SPDMark](https://github.com/Samar-Fares/SPDMark) — [SPDMark HTML](https://arxiv.org/html/2512.12090v2)
- SIGMark: generating one 65-frame 512×512 video takes ~4 min on A800, with negligible embedding time. PRC detection/decoding takes ~30 s per sample on CPU, plus inversion. Storage is O(f·K), constant in the number of videos. Code: [JeremyZhao1998/SIGMark-release](https://github.com/JeremyZhao1998/SIGMark-release) — [SIGMark HTML](https://arxiv.org/html/2603.02882v1)
- VideoShield: training-free; DDIM inversion with 25 steps (ModelScope, SVD) or 50 (ZeroScope, I2VGen-XL). As reported by VidSig: insertion 26.994 / extraction 6.224 (units not stated) on ModelScope. Code: [hurunyi/VideoShield](https://github.com/hurunyi/VideoShield) — [VideoShield HTML](https://arxiv.org/html/2501.14195v2); [VidSig HTML](https://arxiv.org/html/2506.00652v4)
- VideoMark: training-free; DDIM inversion (25 steps T2V, 50 I2V). Extraction time not reported. Code: [KYRIE-LI11/VideoMark](https://github.com/KYRIE-LI11/VideoMark) — [VideoMark HTML](https://arxiv.org/html/2504.16359v3); [arXiv abs](https://arxiv.org/abs/2504.16359)
- VidSig: 1×A800, 10k OpenVid-1M videos (8 frames, 256×256), batch 2, AdamW lr 5e-4. Total steps not reported. No code found — [VidSig HTML](https://arxiv.org/html/2506.00652v4)
- Stable Signature: [facebookresearch/stable_signature](https://github.com/facebookresearch/stable_signature). Compute not on the abstract page — [arXiv abs](https://arxiv.org/abs/2303.15435)
- Tree-Ring: [YuxinWenRick/tree-ring-watermark](https://github.com/YuxinWenRick/tree-ring-watermark) — [arXiv abs](https://arxiv.org/abs/2305.20030)
- Gaussian Shading: no repo link on the arXiv page — [arXiv abs](https://arxiv.org/abs/2404.04956)
- WOUAF: [kylemin/WOUAF](https://github.com/kylemin/WOUAF) — [arXiv abs](https://arxiv.org/abs/2306.04744)
- LoT-Pass/I2VWM: [MrCrims/LoT-Pass-…](https://github.com/MrCrims/LoT-Pass-Long-term-robust-Image-Watermarking-for-Image-to-Video-Generation) (HTML) and [MrCrims/I2VWM-…](https://github.com/MrCrims/I2VWM-Robust-Watermarking-for-Image-to-Video-Generation) (abstract page) — [HTML](https://arxiv.org/html/2509.17773v3)
- WaTeRFlow: no code found — [arXiv abs](https://arxiv.org/abs/2512.19048)
- MoSign: no code found — [arXiv abs](https://arxiv.org/abs/2609.29603)
- LampMark: no code link in the HTML content read — [LampMark HTML](https://arxiv.org/html/2411.17209v1)
- LIDMark: [vpsg-research/LIDMark](https://github.com/vpsg-research/LIDMark) — [arXiv abs](https://arxiv.org/abs/2602.23523)
- LivePortrait: 12.8 ms/frame on RTX 4090; base training 8×A100 ~10 days + ~2 days — [LivePortrait HTML](https://arxiv.org/html/2407.03168). GAGAvatar code: [xg-chu/GAGAvatar](https://github.com/xg-chu/GAGAvatar) — [GAGAvatar arXiv](https://arxiv.org/html/2410.07971v1)

### Inferences
- For a LivePortrait watermark project, the compute budget is dominated by decoder-LoRA training plus extractor training. By analogy to SPDMark this is likely single-GPU, hours-to-a-day scale. Full retraining of LivePortrait (8×A100, ~12 days) is not required if F, M and W are frozen.
- Inversion-based verification (minutes per video, generator required) is impractical for a verification service handling many reenactment videos. Lightweight extractors (VideoSeal, SPDMark, Stable Signature/VidSig at ~ms per frame) are better suited.

### Gaps
- Stable Signature's fine-tuning compute and Gaussian Shading's code location were not confirmed from the fetched pages.
- VideoShield's compute-overhead appendix (E.7) was not retrieved, and VidSig's timing units are unstated.
- The licenses of the code repos were not checked.
