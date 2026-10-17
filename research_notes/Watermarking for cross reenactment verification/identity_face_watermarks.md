# Identity-, Landmark-, and Source-Conditioned Proactive Face Watermarking for Deepfake Defense (focus: robustness to face reenactment)

Research date: 2026-10-16. Unless a line says otherwise, numbers come from the primary paper's own full text, which I read as arXiv HTML or CVF PDF and grepped locally. Numbers reported only by a later paper are labelled **[secondary]**.

Terms used throughout:
- **"Robust"**: the watermark is designed to survive deepfake manipulation. Detection then works by comparing the recovered payload with the content (or the payload is used for tracing).
- **"Semi-fragile"**: the watermark is designed to break under deepfake manipulation and survive benign processing.

---

## Key Question 1: What do the proactive face-watermarking methods embed and detect, what were they tested against, and what are their datasets, results and code status?

### Takeaway
About 20 methods are covered here. All but two (GIFGuard, which handles 10-frame GIFs, and TaintedPixels, which handles video) are **image-only**, and almost all are trained and tested on CelebA/CelebA-HQ (+LFW/FFHQ) at 128–512 px.

"Identity" means three different things across these papers:
1. **Face identity**: an ArcFace-type embedding (Zhao WACV23, Wang 2311.01357, CMark, SVS-WM, One-Identity-One-Key).
2. **Source/provenance ID**: an arbitrary owner, file or generator ID (LIDMark's 16-bit hash of the *filename*, SAiW, SepMark's Tracer, Dual Defense, SIDT).
3. **Face geometry**: landmarks (LampMark, LIDMark).

No method encodes a *driver* identity.

### Cited Findings

**Dense comparison table** (S-F = semi-fragile; R = robust; "Reen." = reenactment tested; the URL column gives the primary source)

| Method (venue, ID) | Design | Payload / what is embedded | Conditioning | Detects / outputs | Deepfakes tested (train → test) | Reen. tested? | Image/Video | Datasets | Key quantitative results (own paper) | Code | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **LIDMark "All in One"** (CVPR 2026; arXiv 2602.23523; Wu, Wang, Guo) | Robust ("purely robust" composite payload) | 152-D: **136-D normalized 68-pt landmarks** (face-alignment lib) + **16-D bipolar ID = truncated SHA-256 of the image filename** (32-D variant = 168-D in appendix) | Landmark (geometry) + source ID (not face identity) | Detection: "intrinsic–extrinsic" check = AED between decoded landmarks and landmarks re-detected on the suspect image; threshold 3.2375 px (Youden J; ROC AUC 0.9388). Localization: per-facial-region AED. Tracing: 16-bit ID via a classification head | Fine-tune on SimSwap, UniFace, CSCS, StarGAN-v2 → **InfoSwap held out** | **No** (only swaps + StarGAN-v2 attribute/style editing) | Image | CelebA-HQ (train/test), LFW (2,000 images, cross-dataset), 128 and 256 px | Avg ID BER over 5 deepfakes 3.33% (128) / 2.55% (256); unseen InfoSwap BER 0.22% / 0.84%; worst case StarGAN-v2 BER 16.42% / 8.47%; landmark AED avg 1.58 / 4.01 px | Yes, verified: github.com/vpsg-research/LIDMark (main.py, model, trainer...) | [arXiv HTML](https://arxiv.org/html/2602.23523), [abs](https://arxiv.org/abs/2602.23523), [code](https://github.com/vpsg-research/LIDMark) |
| **LampMark** (ACM MM 2024; arXiv 2411.17209; Wang, Huang, Cheng, Zhang, Shen) | Robust; detection by content/watermark consistency | Training-free landmark → binary watermark (PCA projection plus cellular-automaton encryption); 64 bits @128, 128 bits @256 | Landmark (geometry) | Real/fake from bit match between the recovered watermark and the watermark re-derived from the suspect image's landmarks | Train: **SimSwap only** → test: SimSwap, InfoSwap, UniFace, E4S, StarGAN (v2), **StyleMask, HyperReenact** | **Yes** (StyleMask, HyperReenact; also counts StarGAN as "reenactment") | Image | CelebA-HQ, LFW | Recovery @128: SimSwap 99.95, InfoSwap 97.99, UniFace 99.72, E4S 92.09, StarGAN 73.12, StyleMask 74.19, HyperReenact 73.53 (avg 87.23%). @256: 99.98 / 98.31 / 94.28 / 93.27 / 74.66 / 75.83 / 74.18 (avg 87.21%). Detection AUC ≥96.76% on every manipulation; HyperReenact 98.87 / 99.02; Mixed 98.39 / 98.55 | Yes, verified: github.com/wangty1/LampMark | [arXiv HTML](https://arxiv.org/html/2411.17209), [DOI](https://doi.org/10.1145/3664647.3680869), [code](https://github.com/wangty1/LampMark) |
| **FractalForensics** (ACM MM 2025 Oral; arXiv 2504.09451; Wang, Cheng, Liu, Kankanhalli) | **Semi-fragile** | Parameter-driven fractal-curve watermark matrix with 4-bit entries, chaotic encryption; "entry-to-patch" embedding | None (content-independent, keyed) | Detection from patch recovery rate; localization from per-patch watermark loss; also sensitive to cropping | **Black-box: no deepfakes in training** (Identity, JPEG, Gaussian noise only) → test: SimSwap, InfoSwap, UniFace, E4S, DiffSwap; "reenactment": StarGAN, StyleMask, HyperReenact | **Yes** (StyleMask, HyperReenact) | Image | CelebA-HQ, LFW; 256 and 512 px | Detection AUC **99.99% on all 8 manipulations**, including StyleMask and HyperReenact (Table 4). Fragility: watermark recovery drops to about 10% under the three "reenactment" methods | Yes, verified: github.com/wangty1/FractalForensics | [arXiv HTML](https://arxiv.org/html/2504.09451), [DOI](https://doi.org/10.1145/3746027.3754544), [code](https://github.com/wangty1/FractalForensics) |
| **GIFGuard** (ACM MM 2026; arXiv 2604.26519; Che, Guo, Miao, Ma, Yang) | Robust (tracing) | 128-bit message spread spatiotemporally over 10-frame GIF volumes (3D-conv STARE encoder, DIRD hourglass decoder) | Source ID (generic message) | Message recovery / provenance under deepfake | Frozen attack simulators in training: SimSwap, MobileFaceSwap, Ghost (swaps only) | **No** | **GIF (10 frames), the only temporal method among the listed watermark-recovery methods** | New GIFfaces dataset (50k samples from Celeb-DF-v2, DFEW, CAER, other video benchmarks and YouTube); 10k/3k/3k split | "BER 0.01%" under deepfake attacks (abstract/intro); baselines REVmark avg BER 22.81%, VideoSeal 10.78% at 128 bits | Yes, verified: github.com/vpsg-research/GIFGuard | [arXiv HTML](https://arxiv.org/html/2604.26519), [code](https://github.com/vpsg-research/GIFGuard) |
| **SAiW** (arXiv 2603.23178, Mar 2026; Das, Adak, Chattopadhyay, Akhtar, Dutta; no venue listed) | Robust; **post-generation source attribution** | Watermark "identity" = source/generator class (logo image → latent; FiLM conditioning); ArcFace-style margin loss over classes plus a "no watermark" class | **Source-conditioned** (generator/source, not face) | Watermark recovery plus classification of the originating source | Watermarks **existing deepfake images** from 5 swaps (Ghost, SimSwap, SimSwap++, FaceDancer, InsightFace) and FaceApp; "post-attack" = photometric/signal distortions, **not** deepfakes applied after watermarking | No | Image | IndicSideFace (primary), FF, FF++, CelebA (cross-dataset) | PSNR >50–55 dB; bit recovery >0.97 under brightness/contrast/JPEG/noise/blur; JPEG 0.9955, blur 0.9968 on CelebA | No link found | [arXiv HTML](https://arxiv.org/html/2603.23178), [abs](https://arxiv.org/abs/2603.23178) |
| **DiffMark** (Information Fusion, Mar 2026, DOI 10.1016/j.inffus.2025.103801; arXiv 2507.01428) | Robust | 30 bits @128, 128 bits @256; diffusion-generated watermarked image (CIF cross-attention module) | Face image as diffusion condition (no identity semantics) | Watermark recovery (tracing) | Training: frozen autoencoder simulates deepfakes; sampling-time "Deepfake-resistant guidance" uses **SimSwap**. Test: SimSwap, UniFace, CSCS, StarGAN, **FSRT (reenactment, CVPR 2024)**, VQGAN | **Yes** (FSRT) | Image | CelebA-HQ, LFW | BER under FSRT: **0.12% (128) / 4.05% (256)**; avg BER across 6 manipulations 1.75% / 2.77% | Yes, verified: github.com/vpsg-research/DiffMark | [arXiv HTML](https://arxiv.org/html/2507.01428), [code](https://github.com/vpsg-research/DiffMark) |
| **Zhao et al. "Proactive Deepfake Defence via Identity Watermarking"** (WACV 2023; Zhao, Liu, Ding, Liu, Zhu, Yu; UTS/CSIRO Data61) | **Semi-fragile** | Pseudo-random sequence (Gold sequence chosen) added (α=0.1) to the **512-D identity vector** of a pretrained identity encoder; image re-synthesized from watermarked identity + attributes (AAD blocks) | **Face identity** | Real/fake from the correlation peak (PAR) between the re-extracted identity vector and the sequence | Test: AttGAN, StarGAN2 (attribute), InfoSwap, SimSwap (swap), CIAGAN, DeepPrivacy (anonymization); also FaceShifter vs AGF | **No** | Image | Train FFHQ; test CelebA, CelebA-HQ | Abstract: average detection accuracy >80%. Authors: "performs poorly on StarGAN2 … because StarGAN2 does not modify face identity-related features" | No link found | [CVF](https://openaccess.thecvf.com/content/WACV2023/html/Zhao_Proactive_Deepfake_Defence_via_Identity_Watermarking_WACV_2023_paper.html), [PDF](https://openaccess.thecvf.com/content/WACV2023/papers/Zhao_Proactive_Deepfake_Defence_via_Identity_Watermarking_WACV_2023_paper.pdf) |
| **SIDT: Source-ID-Tracker** (IEEE ICME 2022, pp. 1–6, DOI 10.1109/ICME52920.2022.9859600; Lin, Chen, Maiorana, Campisi, Li) | Robust steganography; **post-generation, service-provider side** | Hides the **whole source-face image** inside the face-swap output | **Source face identity** (the identity donor) | Recovers the hidden source face and infers its identity after social-media sharing | Face swapping (provider's own output) | No | Image | n/a (abstract only) | Abstract reports "promising" reconstruction quality and attribution accuracy; no numbers available | No link found | [Crossref/IEEE DOI](https://doi.org/10.1109/ICME52920.2022.9859600), [IEEE Xplore](https://ieeexplore.ieee.org/document/9859600) |
| **Robust Identity Perceptual Watermark** (arXiv 2311.01357, v3 Nov 2025; Wang, Huang, Cheng, Ma, Wang; "In peer review") | Robust; consistency check | Identity-perceptual binary watermark from face-recognition embedding (scaled + rounded), chaotic encryption; collision check | **Face identity** | Detects swaps (recovered vs content-derived identity watermark mismatch) **and** traces source (recovered = original identity) | Train: SimSwap only → test: SimSwap, InfoSwap, UniFace, E4S, DiffSwap, FuseAnyPart, Face-Adapter, REFace | **No** (title and scope: face swapping) | Image | CelebA-HQ, LFW | Detailed numbers not extracted | No link found | [arXiv](https://arxiv.org/abs/2311.01357), [HTML](https://arxiv.org/html/2311.01357) |
| **Dual Defense** (IEEE TIFS 2024, DOI 10.1109/TIFS.2024.3383648; arXiv 2310.16540; Zhang, Ye et al.) | Robust **and adversarial** (disrupts swap output) | 30-bit user-defined message (ID, timestamp...) | Source/owner ID | Tracing plus disruption of FaceSwap output | FaceSwap (encoder/decoder swap) white-box; cross-task/cross-dataset | No | Image | VGGFace2, CASIA-WebFace | Not extracted | No link found | [arXiv HTML](https://arxiv.org/html/2310.16540), [DOI](https://doi.org/10.1109/TIFS.2024.3383648) |
| **CMark: Contour-Hybrid Watermark** (arXiv 2505.19081; Xia, Zhou, Liu, Yuan, Li, Wang, Gao; "under review") | Robust (embedded in facial-contour/background band, outside the inner face) | 32 bits = 16 contour-texture + 16 face-identity features, RSA-encrypted | **Face identity + contour texture** | Two-step check: watermark present? then identity match → swap detection | 8 swaps (FaceSwap, MobileFS, FaceShifter, SimSwap, E4S, MegaFS, DiffSwap, DiffFace) | **No.** Authors: generalization "to … face reenactment and editing requires further investigation" | Image | CelebA-HQ, FFHQ | Avg ACC/F1 across 8 swaps exceed the best passive detector by 11.64% / 10.45% | No link found | [arXiv HTML](https://arxiv.org/html/2505.19081) |
| **DeepForgeSeal** (accepted IEEE TPAMI; arXiv 2511.04949; Fernando, Fookes, Sridharan) | **Semi-fragile**, latent-space (adversarial RL) | Message from a shared secret key, embedded in generator latent space | Key (not identity) | Detection via bit recovery accuracy (BRA) | Trained on FFHQ with swaps + attribute edits (hair, **expression**...). Tested: AttGAN, StarGAN2, InfoSwap, SimSwap, CIAGAN, DeepPrivacy (detection); SimSwap, UniFace, FaceDancer, **HyperReenact** (fragility) | **Yes** (HyperReenact; expression edits were in training) | Image | FFHQ, CelebA, CelebA-HQ | BRA under HyperReenact **0.06** (lower is better) vs FaceSigns 0.51, EditGuard 0.50, OmniGuard 0.42, VINE 0.48; benign BRA 0.98–1.00 | No link found | [arXiv HTML](https://arxiv.org/html/2511.04949) |
| **"Watermarking Matters for Deepfake Detection: A Proactive Method for Detecting Forgeries under Conventional Attacks"** (CVPR 2026 Findings; Xia, Mu, Li, Zhang, Gui, Wang, Liu) | **Semi-fragile** watermark + distilled detector | 256 bits (16×16 binary image) in Quaternion Continuous Orthogonal Moments (QCOMs) space; SFmamba extractor; detector distilled via adapters | Random message | Binary real/fake (detector) | Unseen at test: **Face2Face**, StarGAN, HifiFace, DiffSwap (supplement also visualizes StyleGAN, FaceSwap, DeepPrivacy, HiSD) | **Yes** (Face2Face, classical graphics-based reenactment) | Image | Train/test CelebA (24k/6k); cross-domain real images from DFDC, FF++, Celeb-DF, DF40, WDF | ACC under unseen deepfake + conventional attacks: **Face2Face 90.53**, StarGAN 89.43, HifiFace 91.77, DiffSwap 90.63; cross-dataset AUC 95.92–97.66 | "will be made publicly available" (supplement); none found | [CVF PDF](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf), [supp](https://openaccess.thecvf.com/content/CVPR2026F/supplemental/Xia_Watermarking_Matters_for_CVPRF_2026_supplemental.pdf), [poster](https://cvpr.thecvf.com/virtual/2026/poster/40675) |
| **SepMark** (ACM MM 2023; arXiv 2305.06321; Wu, Liao, Ou) | One encoder, two decoders: robust **Tracer** + semi-fragile **Detector** | 30 bits @128 / 128 bits @256 | Source ID | Tracing (Tracer) + detection (Detector breaks) | Trained **with** SimSwap, **GANimation** (expression reenactment), StarGAN attributes | Yes, GANimation, but **seen in training** | Image | CelebA-HQ, CelebA, COCO | GANimation: Tracer BER ≈0.000%, Detector BER ≈36.8% (128) / 43.9% (256). Column mapping parsed from HTML; treat as approximate | Yes, verified: github.com/sh1newu/SepMark | [arXiv HTML](https://arxiv.org/html/2305.06321), [code](https://github.com/sh1newu/SepMark) |
| **FaceSigns** (ACM TOMM 2024, DOI 10.1145/3640466; arXiv 2204.01960; Neekhara et al.) | **Semi-fragile** | Encrypted bit string (e.g., device code); 128 bits per later comparisons | Key/device | Real/fake from bit recovery | SimSwap, FSFT, FaceSwap (graphics) | No | Image (motivated by video) | CelebA | Not extracted | Demo/inference repo only: github.com/paarthneekhara/FaceSignsDemo | [arXiv HTML](https://arxiv.org/html/2204.01960), [DOI](https://doi.org/10.1145/3640466), [demo](https://github.com/paarthneekhara/FaceSignsDemo) |
| **EditGuard** (CVPR 2024, DOI 10.1109/CVPR52733.2024.01137; arXiv 2312.08883) | Dual: fragile 2D localization watermark (image-in-image) + robust 1D copyright bits | 2D RGB localization pattern + bit copyright string | None | Tamper localization (AIGC edits) + copyright | SD-Inpaint, ControlNet, SDXL, RePaint, LaMa, FaceSwap (the "StarGAN, GANimation, SimSwap" entry in its appendix comparison table belongs to the SepMark row, not to EditGuard) | **No** | Image (video extension claimed as future work) | COCO, CelebA (AGE-Set) | Not extracted | Yes, verified: github.com/xuanyuzhang21/EditGuard | [arXiv HTML](https://arxiv.org/html/2312.08883), [code](https://github.com/xuanyuzhang21/EditGuard) |
| **One-Identity-One-Key / "Segfacemark"** (IEEE TCSVT vol. 36, pp. 14007–14020, 2026; He, Guo, Wang, Tao, Liao) | Region-aware watermark; dual verification | Structural watermark encrypted with **personalized keys derived from identity features** | **Face identity** (as the key) | Detection via identity-decryption consistency + region consistency; forgery-type identification; tracing | Not available (abstract only) | Unknown | Image (presumed) | Unknown | Not available | Not found | [DOI](https://doi.org/10.1109/TCSVT.2026.3700633) |
| **SVS-WM: Self-Verifiable Semantic Watermarking** (ACM MM 2025, DOI 10.1145/3746027.3755587; Jiang et al.) | **Semi-fragile**, blind | **Pairs of correlated** pseudo-random watermarks injected into **identity and multi-level attribute** features | Face identity + attributes | Detection via cross-correlation between the decoded attribute watermark and the extracted identity vector, with no reference needed | Identity and attribute manipulations (details not retrieved) | Unknown | Image | Unknown | "average detection accuracy of 98.19%" (abstract) | Not found | [DOI](https://doi.org/10.1145/3746027.3755587) |
| **Big Brother is Watching: learnable hidden face** (arXiv 2504.11309, Apr 2025) | Semi-fragile steganography (hides a face) | A learnable "hidden face" | Face-like template | Detection via hidden-face recoverability | SimSwap, FaceShifter, FaceSwap, MobileFaceSwap, StarGAN2, TTedit, FIT | No | Image | FFHQ (train), CelebA-HQ, VGGFace2 | AUC tables not extracted | Not checked | [arXiv HTML](https://arxiv.org/html/2504.11309) |
| **TaintedPixels: "Can Tainted Pixels Expose Deepfake Videos?"** (arXiv 2608.27492, Aug 2026; Hu, Fan, Saha, Herrera, Sim) | Perturbation that becomes **visible** after manipulation (not a recoverable payload) | Periodic blue-channel stripe perturbation, motion-adaptive, LPIPS 0.0042 | None | Makes forgeries visibly or detectably fake | Black-box tools: **Roop, FaceFusion (swap), MuseTalk (audio-driven animation)** | Partially (audio-driven lip-sync, not motion transfer) | **Video** | 400-stimulus human study | Protected source videos drew a 3.26% suspicion rate | Not checked | [arXiv HTML](https://arxiv.org/html/2608.27492) |
| **Synth-Tracker** (IEEE SPL vol. 32, pp. 3715–3719, 2025; Zhang, Chen, Zheng) | "Recoverable and traceable defense watermark against face synthesis" | Unknown (no abstract retrieved) | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Unknown | Not checked | [DOI](https://doi.org/10.1109/LSP.2025.3608085) |

**Supporting details:**
- LIDMark's identifier is a hash of the filename, used "for convenience … to simulate this tracing scenario"; the authors say it "can represent arbitrary provenance or copyright data". It is not a face-identity code. LIDMark's conclusion lists "extend to video modalities" as future work. — [LIDMark HTML](https://arxiv.org/html/2602.23523)
- LIDMark trains with an "intra-batch rolling strategy, using another image from the same batch as the identity source" for its swap simulators. — [LIDMark HTML](https://arxiv.org/html/2602.23523)
- LampMark explicitly claims to be "the first to simultaneously detect face swapping and face reenactment Deepfake manipulations with a single robust watermark". — [LampMark HTML](https://arxiv.org/html/2411.17209)
- LampMark attributes its weaker reenactment recovery (~75%) to reenactment "wiping out the background information … making it more difficult to recover the original watermarks". — [LampMark HTML](https://arxiv.org/html/2411.17209)
- DeepForgeSeal argues semi-fragile marks avoid the need to validate "against a known source or identity", which "can be logistically complex" on social platforms. This is the authors' design argument against identity-bound robust marks. — [DeepForgeSeal HTML](https://arxiv.org/html/2511.04949)
- SVS-WM detects by verifying "the correlation result between the decoded attribute watermark and the extracted identity vector", which "enables authentication without requiring original reference watermark". — [Semantic Scholar record of DOI 10.1145/3746027.3755587](https://doi.org/10.1145/3746027.3755587)
- The ACM CSUR survey (Nguyen-Le, Tran, Nguyen, Le-Khac; published 2025-11-20) covers disruption and watermarking. It evaluates them on imperceptibility, protectability/detectability, transferability, traceability and robustness. — [DOI 10.1145/3771296](https://doi.org/10.1145/3771296)

### Inferences
- **Landmark-conditioned robust marks (LampMark, LIDMark)** flag *any* change in facial geometry. Reenactment changes pose and expression by design, so these methods should flag every reenactment, authorized or not. They cannot say who drove the motion, or whether it was licensed. LIDMark has no published reenactment test, so this applies to it only by inference.
- **Face-identity-conditioned marks (Zhao WACV23, 2311.01357, CMark, One-Identity-One-Key, likely SVS-WM's identity half)** check whether the face identity changed. Reenactment preserves the target's identity, so the identity channel is structurally blind to it. Zhao et al. concede this for StarGAN2 ("does not modify face identity-related features"). Any reenactment sensitivity would have to come from attribute or geometry channels.
- **Source-ID marks** (LIDMark's 16-bit ID, SepMark's Tracer, GIFGuard, Dual Defense, SAiW) answer "whose image/file was this?". They carry no notion of who is depicted or who drove the motion.
- One lab group (Guo / Wang / vpsg-research: DiffMark, LIDMark, GIFGuard, One-Identity-One-Key) produces much of this 2025–2026 line, with shared baselines and protocols. Their results are not independent replications.

### Gaps
- One-Identity-One-Key, SVS-WM and Synth-Tracker: only abstracts or metadata were available. Manipulations tested, payloads, datasets and code are unknown.
- SIDT: only the abstract was available; no quantitative results or dataset details.
- Detailed numbers for 2311.01357, Dual Defense, FaceSigns, EditGuard and Big Brother were not extracted.
- LIDMark table cells for the 128/256 columns were parsed from HTML. Values match the paper's stated averages, but individual cells should be spot-checked against the PDF.

---

## Key Question 2: Which works actually tested reenactment, and how robust are they to *unseen* reenactment? (Includes a check of "LampMark 96.5% vs 73.6%")

### Takeaway
Only six methods report any reenactment test: LampMark, FractalForensics, DiffMark, DeepForgeSeal, Watermarking Matters, and SepMark (seen in training). The tested generators are all **2018–2024 image-level models**: GANimation, Face2Face, StyleMask, HyperReenact and FSRT. LampMark's robust landmark mark drops about 22–23 points on unseen reenactment. Semi-fragile designs (FractalForensics, DeepForgeSeal) report near-perfect detection, because breaking is the goal for them. The widely repeated "96.46% vs 73.61%" comparison mixes resolutions and mislabels the training regime.

### Cited Findings
- FractalForensics states: "LampMark … has an average of 96.46% watermark recovery rate against face swapping algorithms (trained with) but an average of 73.61% against face reenactment algorithms (unseen)." — [FractalForensics HTML](https://arxiv.org/html/2504.09451)
- **Verification against LampMark's own Table 3 shows the figure mixes resolutions:**

  | | 128 px | 256 px |
  |---|---|---|
  | Swap average (SimSwap, InfoSwap, UniFace, E4S) | 97.44% | **96.46%** |
  | "Reenactment" average (StarGAN, StyleMask, HyperReenact) | **73.61%** | 74.89% |

  FractalForensics paired the 256-px swap number with the 128-px reenactment number. The like-for-like gap is about 23.8 points at 128 px and about 21.6 points at 256 px. (Averages computed from LampMark's Table 3: 128 px rows 99.95/97.99/99.72/92.09 and 73.12/74.19/73.53; 256 px rows 99.98/98.31/94.28/93.27 and 74.66/75.83/74.18.) — [LampMark HTML](https://arxiv.org/html/2411.17209)
- **"Trained with" is inaccurate for most of the swaps.** LampMark's model "sees only [benign pool] and SimSwap during the training phase", so InfoSwap, UniFace and E4S were also unseen. — [LampMark HTML](https://arxiv.org/html/2411.17209)
- **"Reenactment" includes StarGAN in both papers.** Both list StarGAN (Choi et al. 2020, i.e., StarGAN v2) under face reenactment, alongside StyleMask and HyperReenact. StarGAN v2 is a reference-guided image-to-image translation model. Counting only StyleMask and HyperReenact, LampMark's recovery is 73.86% (128) / 75.01% (256). — [FractalForensics HTML](https://arxiv.org/html/2504.09451); [LampMark HTML](https://arxiv.org/html/2411.17209)
- Despite ~74% bit recovery, LampMark's *detection* AUC on HyperReenact is 98.87% (128) / 99.02% (256), and on StyleMask 98.62 / 98.98. Detection compares the recovered watermark with the content-derived one, so partial recovery still separates real from fake. — [LampMark HTML](https://arxiv.org/html/2411.17209)
- FractalForensics (no deepfakes in training) reports AUC 99.99% on StarGAN, StyleMask and HyperReenact. Its watermark recovery under these three falls to about 10%, i.e., strongly fragile. Its own recovery under the five swaps is much higher (about 24–81% across its 256/512 models), so it is markedly more fragile to "reenactment" than to swaps. — [FractalForensics HTML](https://arxiv.org/html/2504.09451)
- DiffMark: FSRT (Rochow et al., CVPR 2024, a transformer one-shot reenactment model) gives BER 0.12% (128) / 4.05% (256). Only SimSwap is used in DiffMark's guidance, and FSRT is not described as a training manipulation, so it appears unseen. LampMark re-implemented by DiffMark gets **[secondary]** 2.93% / 18.08% BER on FSRT. — [DiffMark HTML](https://arxiv.org/html/2507.01428)
- DeepForgeSeal: bit recovery accuracy (BRA) under HyperReenact is 0.06, versus FaceSigns 0.51, EditGuard 0.50, OmniGuard 0.42, VINE 0.48 **[those four are secondary re-runs]**. Training included "expression" attribute edits, so reenactment-like changes were not fully out of distribution. — [DeepForgeSeal HTML](https://arxiv.org/html/2511.04949)
- Watermarking Matters (CVPR 2026 Findings): detection ACC on unseen Face2Face is 90.53%, versus SepMark **[secondary]** 82.42% and FDebias **[secondary]** 84.32%. — [CVF PDF](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf)
- SepMark trains on GANimation (expression reenactment). Its robust Tracer recovers almost perfectly under GANimation while the semi-fragile Detector degrades. This is an in-distribution test. — [SepMark HTML](https://arxiv.org/html/2305.06321)
- **Conflicting secondary numbers.**
  - DiffMark's re-implementation of LampMark (with "landmark perceptual watermarks" rebuilt to a standardized length) reports **[secondary]** 16.53% BER on SimSwap at 128 px. LampMark's own paper reports 99.95% recovery (~0.05% BER). — [DiffMark HTML](https://arxiv.org/html/2507.01428); [LampMark HTML](https://arxiv.org/html/2411.17209)
  - LIDMark's Table 3 baseline rows are identical to DiffMark's Table 3 for MBRS, CIN, SepMark, EditGuard and LampMark on SimSwap, UniFace and CSCS (e.g., LampMark 16.53% / 15.11% on SimSwap; SepMark 20.02% / 11.95%). This indicates the baselines were copied rather than re-run. — [LIDMark HTML](https://arxiv.org/html/2602.23523); [DiffMark HTML](https://arxiv.org/html/2507.01428)

### Inferences
- For robust, consistency-based designs, unseen reenactment hurts *payload recovery* far more than *detection AUC*, because any geometry change also changes the content-derived reference. Payload-carrying functions (tracing, claim binding) are therefore the part most at risk under reenactment.
- None of these reenactment tests uses a video with a real driver. All are single-image source→target transfers at 128–512 px on CelebA-HQ-style crops, with no temporal decoding or aggregation.

### Gaps
- No paper reports results separately for self-reenactment (same identity drives) and cross-reenactment (different identity drives).
- LIDMark (the method most relevant to landmark binding) has no reenactment numbers at all.

---

## Key Question 3: Has any method been evaluated against modern reenactment / portrait-animation generators (LivePortrait, EMOPortraits, X-Portrait, HunyuanPortrait)?

### Takeaway
No. I found no proactive face-watermarking paper evaluated against LivePortrait, EMOPortraits, X-Portrait or HunyuanPortrait. The newest reenactment generator used in any watermark evaluation is FSRT (CVPR 2024, in DiffMark). The only proactive defense tested on current off-the-shelf video tools is TaintedPixels (MuseTalk, Roop, FaceFusion), and it is a visibility-perturbation scheme, not a recoverable watermark.

### Cited Findings
- **Local full-text check.** I grepped 20 full texts for `LivePortrait | EMOPortrait | X-Portrait | Hunyuan | FOMM / First Order Motion | TPSMM | face-vid2vid | DaGAN | MCNet | MuseTalk | SadTalker | EchoMimic | Hallo`. The texts were the arXiv HTML of LIDMark, LampMark, FractalForensics, GIFGuard, SAiW, DiffMark, 2311.01357, Dual Defense, CMark, DeepForgeSeal, SepMark, FaceSigns, EditGuard, Big Brother, TaintedPixels and the two avatar-fingerprinting papers, plus the CVF PDFs of WACV23 and Watermarking Matters (paper + supplement).
  - **No watermarking paper mentions any of these generators.**
  - Hits occurred only in the passive avatar-fingerprinting papers (face-vid2vid, LivePortrait), in TaintedPixels (MuseTalk), and as false positives ("hallo"/"hunyuan" substrings in names or references).
  - Sources: [LIDMark](https://arxiv.org/html/2602.23523), [LampMark](https://arxiv.org/html/2411.17209), [FractalForensics](https://arxiv.org/html/2504.09451), [DiffMark](https://arxiv.org/html/2507.01428), [DeepForgeSeal](https://arxiv.org/html/2511.04949), [GIFGuard](https://arxiv.org/html/2604.26519), [Watermarking Matters](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf)
- The reenactment generators actually used are:
  - StyleMask (FG 2023) and HyperReenact (ICCV 2023): LampMark, FractalForensics, DeepForgeSeal
  - FSRT (CVPR 2024): DiffMark
  - Face2Face (2016): Watermarking Matters
  - GANimation (2018): SepMark
  - Sources: [LampMark](https://arxiv.org/html/2411.17209), [FractalForensics](https://arxiv.org/html/2504.09451), [DiffMark](https://arxiv.org/html/2507.01428), [DeepForgeSeal](https://arxiv.org/html/2511.04949), [Watermarking Matters](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf), [SepMark](https://arxiv.org/html/2305.06321)
- TaintedPixels evaluates "three representative tools spanning two manipulation paradigms: Roop … and FaceFusion … for face swapping, and MuseTalk … for audio-driven animation". The authors "do not claim universal robustness against future, closed-source, or adaptive forgery models". — [TaintedPixels HTML](https://arxiv.org/html/2608.27492)
- The FG 2026 avatar-fingerprinting paper (passive, not a watermark) lists LivePortrait among latent-space reenactment generators. It evaluates on NVFAIR, which was generated with Face-vid2vid, TPS and LIA. — [arXiv 2604.23247](https://arxiv.org/html/2604.23247)
- A web search ("proactive watermark deepfake LivePortrait reenactment robustness", extended mode) surfaced no such evaluation. — [search-surfaced FractalForensics PDF](https://arxiv.org/pdf/2504.09451); [Watermarking Matters](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf)

### Inferences
- Modern portrait animators (LivePortrait-style implicit-keypoint warping plus decoder, or diffusion-based X-Portrait / HunyuanPortrait / EMOPortraits) re-render the whole face region, often at 512 px, with temporal smoothing. Robust-payload survival through these pipelines is untested. It is plausibly harder than against HyperReenact, given LampMark's ~74% recovery and its own background-wiping explanation, but this is unverified.
- Benchmarking an existing watermark (LampMark, LIDMark, DiffMark, FractalForensics; all have released code) against LivePortrait and similar models would itself be a novel empirical contribution.

### Gaps
- The search may miss non-indexed 2026 workshop papers or Chinese-language journals.
- I did not check the ACM CSUR survey's full text for a table of reenactment-evaluated watermarks; only its abstract was retrieved.

---

## Key Question 4: Does any work encode BOTH a driver claim and a target identity, or distinguish self- from cross-reenactment? (Novelty)

### Takeaway
No. In everything I found, no watermark encodes a driver claim, and no watermark (proactive or post-generation) distinguishes self- from cross-reenactment. The self-vs-cross question has been posed only **passively** (avatar fingerprinting, ECCV 2024 / FG 2026 TrustFA workshop). The nearest watermark analogs each carry one claim: a source identity (SIDT) or a generator ID (SAiW). Or they pair identity with attributes for integrity rather than authorization (SVS-WM). A system that binds a driver claim and a target identity claim in reenactment video therefore appears novel on the claim-binding, reenactment-specific and video axes. That novelty claim rests on this search's coverage.

### Cited Findings
- **Avatar fingerprinting (Prashnani, Nagano, De Mello, Luebke, Gallo; NVIDIA; arXiv 2305.03713; ECCV 2024 per secondary index).**
  - Frames the task as verifying the *driving* identity of a synthetic talking-head video, regardless of the target identity shown.
  - Introduces NVFAIR, with both self- and cross-reenactments per subject (Face-vid2vid, TPS, LIA; 161 identities).
  - Average AUC 0.85, and 0.83 on generators unseen in training.
  - Explicitly passive: "a passive technique that does not rely on active watermarks".
  - Sources: [arXiv HTML](https://arxiv.org/html/2305.03713); [project page](https://research.nvidia.com/labs/nxp/avatar-fingerprinting/); ECCV 2024 venue only from [secondary paper-notes index](https://github.com/zhaoyang97/Paper-Notes-en/blob/main/docs/ECCV2024/human_understanding/avatar_fingerprinting_for_authorized_use_of_synthetic_talking-head_videos.md)
- **Micro-Expression-Aware Avatar Fingerprinting (Chapariniya, Odobez, Dellwo, Vuković; TrustFA Workshop @ IEEE FG 2026).** Passive, preprocessing-free, 0.53M parameters, overall AUC 0.877 on NVFAIR. — [arXiv 2604.23247](https://arxiv.org/abs/2604.23247); [code](https://github.com/Mchapariniya/TrustFA-FG2026)
- **SIDT (ICME 2022)** is the closest structural precedent for generation-time claim embedding. A "legitimate faceswap service provider" embeds the *source face* into the generated deepfake so the identity donor can be recovered later. It carries one claim, applies to swaps, and has no driver/motion claim. — [DOI](https://doi.org/10.1109/ICME52920.2022.9859600)
- **SAiW** is source-conditioned post-generation marking: the watermark "identity encodes the originating source" (the generator). No person-level claims. — [arXiv](https://arxiv.org/abs/2603.23178)
- **SVS-WM (ACM MM 2025)** is the nearest "two-claim" design: correlated identity and attribute watermarks, verified against each other. Both claims are about the *same* depicted face, and it is a semi-fragile integrity check, not authorization. — [DOI](https://doi.org/10.1145/3746027.3755587)
- **CMark** pairs face identity (16 bits) with contour texture (16 bits) for swap detection. Its authors defer reenactment to future work. — [arXiv HTML](https://arxiv.org/html/2505.19081)
- **One-Identity-One-Key** derives per-identity encryption keys from the face identity and verifies identity-decryption consistency (target-side only). — [DOI](https://doi.org/10.1109/TCSVT.2026.3700633)
- **LIDMark** binds geometry (landmarks) to a source identifier. The ID is a filename hash, so neither a driver nor a target-person claim is encoded. — [LIDMark HTML](https://arxiv.org/html/2602.23523)
- The avatar-fingerprinting paper notes that features designed to separate real from synthetic "are not reliable" for this task, "since we only have access to synthetic videos". — [arXiv HTML](https://arxiv.org/html/2305.03713)

**Gap map** (rows = capability; ✓ = shown in this notes file)

| Capability | Who has it |
|---|---|
| Target face-identity claim in watermark | Zhao WACV23, 2311.01357, CMark, One-Identity-One-Key, SVS-WM (pre-manipulation, image) |
| Source/donor identity embedded at generation time | SIDT (swap, image) |
| Generator/source attribution at generation time | SAiW (image) |
| Facial-geometry (landmark) binding | LampMark, LIDMark (image) |
| Reenactment robustness tested | LampMark, FractalForensics, DiffMark, DeepForgeSeal, Watermarking Matters, SepMark (image, pre-2025 generators) |
| Temporal / video watermark against deepfakes | GIFGuard (10-frame GIF, swaps only); TaintedPixels (perturbation, not payload) |
| Driver identity verification | Avatar fingerprinting (passive only) |
| Self- vs cross-reenactment distinction | Avatar fingerprinting / NVFAIR (passive only) |
| **Driver claim + target identity bound in one watermark, in reenactment video** | **None found** |

### Inferences
- The proposed system's novelty claim is strongest phrased as: *"first active/proactive mechanism that binds a driver authorization claim to a target identity claim in reenactment video, enabling self- vs cross-reenactment verification."*
- Prior watermarking addresses "was this face altered?" or "whose file/generator is this?". Passive avatar fingerprinting addresses "who drove this?". Nothing addresses "was this driver authorized to animate this target?".
- Architecturally, the closest building blocks are:
  1. SIDT/SAiW-style **generation-time** embedding by a cooperating avatar service.
  2. LIDMark-style **factorized payloads** (a geometric/regression part plus a classification ID part).
  3. SVS-WM-style **cross-verification** between two correlated claims.
  4. NVFAIR for self- and cross-reenactment evaluation data.
- Reviewers will likely ask why a passive avatar-fingerprinting check plus C2PA-style signed metadata is not enough. That comparison should be pre-empted. (This is an inference; no source discusses the combination.)

### Gaps
- I could not retrieve full texts for One-Identity-One-Key, SVS-WM or Synth-Tracker to rule out a driver/motion claim, although their abstracts give no sign of one.
- Patent literature and industry provenance schemes (C2PA, avatar-platform watermarks) were not searched.
- The ECCV 2024 venue of avatar fingerprinting was confirmed only via a secondary index.

---

## Key Question 5: Do the listed citations exist, with correct venues and IDs?

### Takeaway
All listed citations exist. Corrections and clarifications:
- **SIDT** = "Source-ID-Tracker: Source Face Identity Protection in Face Swapping", **IEEE ICME 2022** (DOI 10.1109/ICME52920.2022.9859600). It is a post-generation, provider-side scheme, not a pre-manipulation protective watermark.
- **DiffMark** is now published in **Information Fusion** (Mar 2026).
- **FaceSigns** is published in **ACM TOMM 2024**.
- **Dual Defense** is in **IEEE TIFS 2024**.
- **Robust Identity Perceptual Watermark (2311.01357)** and **CMark (2505.19081)** are still arXiv-only ("in peer review" / "under review").
- **SAiW** has no venue.

### Cited Findings

| Citation as given | Verified title | Venue / status | IDs | Evidence |
|---|---|---|---|---|
| LIDMark "All in One", arXiv 2602.23523, CVPR 2026 | "All in One: Unifying Deepfake Detection, Tampering Localization, and Source Tracing with a Robust Landmark-Identity Watermark" (Wu, Wang, Guo) | arXiv comment "Accepted by CVPR 2026"; submitted 2026-02-26 | arXiv 2602.23523. 136-D landmarks + 16-D ID = 152-D confirmed; image-only, CelebA-HQ/LFW confirmed | [arXiv](https://arxiv.org/abs/2602.23523) |
| LampMark, arXiv 2411.17209 | "LampMark: Proactive Deepfake Detection via Training-Free Landmark Perceptual Watermarks" | ACM MM 2024 (32nd), Melbourne | DOI 10.1145/3664647.3680869 | [arXiv](https://arxiv.org/abs/2411.17209); [DOI](https://doi.org/10.1145/3664647.3680869) |
| FractalForensics, arXiv 2504.09451 | "FractalForensics: Proactive Deepfake Detection and Localization via Fractal Watermarks" | ACM MM 2025, Oral | DOI 10.1145/3746027.3754544 | [arXiv](https://arxiv.org/abs/2504.09451); [DOI](https://doi.org/10.1145/3746027.3754544) |
| GIFGuard, arXiv 2604.26519 | "GIFGuard: Proactive Forensics against Deepfakes in Facial GIFs via Spatiotemporal Watermarking" | ACM MM 2026 (arXiv comment); v2 2026-08-10 | arXiv 2604.26519 | [arXiv](https://arxiv.org/abs/2604.26519) |
| SAiW, arXiv 2603.23178 | "SAiW: Source-Attributable Invisible Watermarking for Proactive Deepfake Defense" | arXiv only (cs.AI), 2026-03-24; no venue | arXiv 2603.23178 | [arXiv](https://arxiv.org/abs/2603.23178) |
| DiffMark, arXiv 2507.01428 | "DiffMark: Diffusion-based Robust Watermark Against Deepfakes" | **Information Fusion**, issue dated March 2026 | DOI 10.1016/j.inffus.2025.103801 | [arXiv](https://arxiv.org/abs/2507.01428); [DOI](https://doi.org/10.1016/j.inffus.2025.103801) |
| Zhao et al., WACV 2023 | "Proactive Deepfake Defence via Identity Watermarking" (Yuan Zhao, Bo Liu, Ming Ding, Baoping Liu, Tianqing Zhu, Xin Yu) | WACV 2023. Page range conflicts: CVF lists 4602–4611, the UTS repository 4591–4600 | — | [CVF](https://openaccess.thecvf.com/content/WACV2023/html/Zhao_Proactive_Deepfake_Defence_via_Identity_Watermarking_WACV_2023_paper.html); [UTS](https://opus.lib.uts.edu.au/handle/10453/166458) |
| SIDT, IEEE 9859600 | "Source-ID-Tracker: Source Face Identity Protection in Face Swapping" (Yuzhen Lin, Han Chen, Emanuele Maiorana, Patrizio Campisi, Bin Li) | **IEEE ICME 2022**, pp. 01–06 | DOI 10.1109/ICME52920.2022.9859600 | [DOI](https://doi.org/10.1109/ICME52920.2022.9859600) (Crossref + Semantic Scholar; one web-search snippet wrongly said it could not be found) |
| Robust Identity Perceptual Watermark, arXiv 2311.01357 | "Robust Identity Perceptual Watermark Against Deepfake Face Swapping" (Wang, Huang, Cheng, Ma, Wang) | arXiv only; comment "In peer review"; v3 2025-11-04 | arXiv 2311.01357 | [arXiv](https://arxiv.org/abs/2311.01357) |
| Dual Defense, arXiv 2310.16540 | "Dual Defense: Adversarial, Traceable, and Invisible Robust Watermarking against Face Swapping" | **IEEE TIFS 2024** | DOI 10.1109/TIFS.2024.3383648 | [arXiv](https://arxiv.org/abs/2310.16540); [DOI](https://doi.org/10.1109/TIFS.2024.3383648) |
| Contour-Hybrid Watermark, arXiv 2505.19081 | "Towards Generalized Proactive Defense against Face Swapping with Contour-Hybrid Watermark" (CMark) | arXiv only, "under review" | arXiv 2505.19081 | [arXiv](https://arxiv.org/abs/2505.19081) |
| DeepForgeSeal, arXiv 2511.04949 | "DeepForgeSeal: Latent Space-Driven Semi-Fragile Watermarking for Deepfake Detection Using Adversarial Reinforcement Learning" | Accepted to **IEEE TPAMI** (arXiv comment; v2 2026-08-06) | arXiv 2511.04949 | [arXiv](https://arxiv.org/abs/2511.04949) |
| "Watermarking Matters for Deepfake Detection", CVPR 2026 Findings | "Watermarking Matters for Deepfake Detection: A Proactive Method for Detecting Forgeries under Conventional Attacks" (Xia, Mu, Li, Zhang, Gui, Wang, Liu) | CVPR 2026 Findings (CVF "CVPRF"); Findings poster 2026-06-05 | CVF open access; page numbers 1655–1656 are visible on the PDF, but the full range is not confirmed | [CVF PDF](https://openaccess.thecvf.com/content/CVPR2026F/papers/Xia_Watermarking_Matters_for_Deepfake_Detection_A_Proactive_Method_for_Detecting_CVPRF_2026_paper.pdf); [poster](https://cvpr.thecvf.com/virtual/2026/poster/40675) |
| SepMark | "SepMark: Deep Separable Watermarking for Unified Source Tracing and Deepfake Detection" (Wu, Liao, Ou) | ACM MM 2023 | arXiv 2305.06321 | [arXiv](https://arxiv.org/abs/2305.06321) |
| FaceSigns | "FaceSigns: Semi-fragile Watermarks for Media Authentication" (Neekhara et al.) | **ACM TOMM**, 2024 (arXiv v1 2022 titled "…Neural Watermarks for Media Authentication and Countering Deepfakes") | DOI 10.1145/3640466; arXiv 2204.01960 | [DOI](https://doi.org/10.1145/3640466); [arXiv](https://arxiv.org/abs/2204.01960) |
| EditGuard | "EditGuard: Versatile Image Watermarking for Tamper Localization and Copyright Protection" (Zhang et al.) | CVPR 2024 | DOI 10.1109/CVPR52733.2024.01137; arXiv 2312.08883 | [DOI](https://doi.org/10.1109/CVPR52733.2024.01137); [arXiv](https://arxiv.org/abs/2312.08883) |
| ACM survey, DOI 10.1145/3771296 | "A Survey on Proactive Deepfake Defense: Disruption and Watermarking" (Nguyen-Le, Tran, Nguyen, Le-Khac) | ACM Computing Surveys, 2025-11-20 | DOI 10.1145/3771296 | [DOI](https://doi.org/10.1145/3771296) |
| (added) One-Identity-One-Key | "One-Identity-One-Key: Region-Aware Watermark for Proactive Deepfake Detection and Robust Source Tracing" (He, Guo, Wang, Tao, Liao) | IEEE TCSVT vol. 36, pp. 14007–14020, Sep 2026 | DOI 10.1109/TCSVT.2026.3700633 | [DOI](https://doi.org/10.1109/TCSVT.2026.3700633) |
| (added) SVS-WM | "Proactive Deepfake Detection via Self-Verifiable Semantic Watermarking" (Jiang et al.) | ACM MM 2025 | DOI 10.1145/3746027.3755587 | [DOI](https://doi.org/10.1145/3746027.3755587) |
| (added) Synth-Tracker | "Synth-Tracker: Recoverable and Traceable Defense Watermark Against Face Synthesis" | IEEE SPL vol. 32, 2025 | DOI 10.1109/LSP.2025.3608085 | [DOI](https://doi.org/10.1109/LSP.2025.3608085) |
| (added) Avatar Fingerprinting | "Avatar Fingerprinting for Authorized Use of Synthetic Talking-Head Videos" (Prashnani et al., NVIDIA) | ECCV 2024 (secondary index only) | arXiv 2305.03713 | [arXiv](https://arxiv.org/abs/2305.03713) |
| (added) TaintedPixels | "Can Tainted Pixels Expose Deepfake Videos?" (Hu, Fan, Saha, Herrera, Sim) | arXiv, 2026-08-26 | arXiv 2608.27492 | [arXiv](https://arxiv.org/abs/2608.27492) |

**Code-availability status:**
- **Verified via GitHub API (2026-10-16):**
  - vpsg-research/LIDMark: code present; pushed 2026-08
  - vpsg-research/GIFGuard: code + checkpoint dir; pushed 2026-08
  - vpsg-research/DiffMark: code present, contrary to the arXiv "will be available" note; pushed 2025-10
  - wangty1/FractalForensics: pushed 2026-04
  - wangty1/LampMark: pushed 2026-03
  - sh1newu/SepMark
  - paarthneekhara/FaceSignsDemo: demo/inference only
  - xuanyuzhang21/EditGuard
  - Mchapariniya/TrustFA-FG2026: avatar fingerprinting
- **No code link found / not checked:** Zhao WACV23, SIDT, Dual Defense, 2311.01357, SAiW, DeepForgeSeal, CMark, Watermarking Matters (code promised in supplement), One-Identity-One-Key, SVS-WM, Synth-Tracker, Big Brother, TaintedPixels.

### Inferences
- When citing the LampMark reenactment gap, cite LampMark's own Table 3 at a single resolution (e.g., 97.44% vs 73.61% at 128 px, or 96.46% vs 74.89% at 256 px). Note that its "reenactment" set includes StarGAN v2. Do not reuse FractalForensics' mixed-resolution "96.46 vs 73.61" pairing.
- SIDT should be described as a provider-side, post-generation identity-provenance scheme for face swaps, not as a proactive protective watermark.

### Gaps
- IEEE Xplore pages were not directly accessible (fetch failed). SIDT, One-Identity-One-Key and Synth-Tracker details come from Crossref and Semantic Scholar metadata.
- The CVPR 2026 main-conference listing for LIDMark was not checked directly on CVF; acceptance rests on the arXiv comment.
- The WACV 2023 page-range discrepancy (4602–4611 vs 4591–4600) is unresolved.
