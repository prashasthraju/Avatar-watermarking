# Driver-Identity Verification for Talking-Head Reenactment (Avatar Fingerprinting / Puppeteering Detection): State of the Art, 2023–2026

Scope: methods that decide whether the person **driving** a synthetic talking-head video's motion is authorized, i.e. self-reenactment vs cross-reenactment. Research date: 2026-10-16. All numbers below come from the primary paper (arXiv HTML or proceedings PDF) unless marked **[secondary]**. Where a paper contradicts itself, it is marked **[internal inconsistency]**.

Terminology used throughout: *self-reenactment* means target identity = driver (genuine or authorized). *Cross-reenactment* means target identity ≠ driver (impostor or puppeteered).

---

## Q1. What methods exist (2022–2026) for avatar fingerprinting and driver identification?

### Takeaway
The field is small and young. It has two lineages. **(a) "Avatar fingerprinting"** works on rendered video or landmarks: Prashnani et al. (NVIDIA), ECCV 2024; Pedrouzo-Rodriguez et al. (BiDA Lab, UAM), IJCB 2025, followed by AVAPrintDB in Pattern Recognition 2026; and Chapariniya et al., FG 2026 workshop. There is also an audio variant (Gerstner, 2026). **(b) "Puppeteering detection"** works on the transmitted pose-expression latent of AI videoconferencing: Vahdati et al. (Drexel MISL), CVPRW 2023, followed by "Unmasking Puppeteers" at NeurIPS 2025 with NVIDIA co-authors. I found about 7 papers in total. None combines driver biometrics with watermarking.

### Cited Findings

**Lineage A: avatar fingerprinting (rendered RGB or landmarks, often with enrollment)**

- **Prashnani, Nagano, De Mello, Luebke, Gallo (NVIDIA), "Avatar Fingerprinting for Authorized Use of Synthetic Talking-Head Videos", arXiv 2305.03713 (v1 May 2023, v3 Aug 2024), ECCV 2024.** This paper defines the task ("avatar fingerprinting"), introduces the NVFAIR dataset, and reports an average AUC of 0.85, or 0.83 on generators unseen in training. — [arXiv abs](https://arxiv.org/abs/2305.03713); ECCV venue confirmed by the BibTeX on the [project page](https://research.nvidia.com/labs/nxp/avatar-fingerprinting/), [ECVA PDF](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/02330.pdf) and [MLAnthology](https://mlanthology.org/eccv/2024/prashnani2024eccv-avatar)
  - **Input:** 126 facial landmarks per frame (detector cited as Honari et al.), turned into normalized pairwise landmark distances. These are concatenated over 71-frame clips with a stride of 1 frame. A temporal (3D) CNN is trained with a contrastive loss plus a time-shuffle term, so that clips driven by the same identity cluster together. — [arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
  - **Comparison:** for each target identity, the self-reenacted videos serve as the "authorized" reference set (enrollment of the driver's motion). Distances between clips are thresholded to produce the ROC. — [arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
  - **In-domain AUC:** about 0.868 (face-vid2vid), about 0.85 (TPS), about 0.84 (LIA). Unseen-generator AUCs fall in the 0.82–0.87 range, averaging about 0.83. Baselines: Agarwal et al. 2019, about 0.67–0.73; ID-Reveal (Cozzolino et al., 2021), about 0.67–0.72. Ablation: 3DMM features with the ID-Reveal loss score 0.718; landmark distances with the ID-Reveal loss score 0.754; the full model without time-shuffle scores 0.850; the full model scores 0.868. **No EER is reported.** — [arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
  - **Code:** the NVIDIA model was **never released** according to the AVAPrintDB authors ("system was never released"). The project page also mentions no released code. — [AVAPrintDB HTML](https://arxiv.org/html/2603.26934v2); [project page](https://research.nvidia.com/labs/nxp/avatar-fingerprinting/)

- **Pedrouzo-Rodriguez, Delgado-DeRobles, Gomez, Tolosana, Vera-Rodriguez, Morales, Fierrez (BiDA Lab, Univ. Autónoma de Madrid), "Is It Really You? Exploring Biometric Verification Scenarios in Photorealistic Talking-Head Avatar Videos", arXiv 2508.00748 (Aug 2025), IJCB 2025 (DOI 10.1109/IJCB65343.2025.11411089).** — [arXiv abs](https://arxiv.org/abs/2508.00748)
  - **Input:** MediaPipe Face Landmarker (468 3D landmarks), of which 109 are hand-selected. Edges come from Delaunay triangulation, positions are centred on the nose tip and scaled by intercanthal distance. A 3-layer spatio-temporal GCN (output sizes 64/64/256) with temporal attention pooling runs on non-overlapping 50-frame clips. Training uses a triplet loss with random triplets. — [arXiv HTML](https://arxiv.org/html/2508.00748)
  - **Generator and data:** GAGAvatar only, driven from CREMA-D and RAVDESS. Output is 512×512 on a black background; each target is built from one neutral frontal image. — [arXiv HTML](https://arxiv.org/html/2508.00748)
  - **Comparison:** one genuine avatar clip of the target is the reference. It is compared with other genuine clips (to accept) and with impostor clips that share the target's appearance (to reject). Splits are identity-disjoint. — [arXiv HTML](https://arxiv.org/html/2508.00748)
  - **AUC:**

    | Setting | AUC |
    |---|---|
    | Intra-dataset, RAVDESS | 69.92% |
    | Intra-dataset, CREMA-D | 82.58% |
    | Train CREMA-D → test RAVDESS | 75.38% |
    | Train RAVDESS → test CREMA-D | 78.78% |
    | Combined training, CREMA-D | 83.31% |
    | Combined training, RAVDESS | 74.66% |
    | Applied to real (non-avatar) videos | "up to 83%" |

    No EER is reported. — [arXiv HTML](https://arxiv.org/html/2508.00748)
  - **Code and benchmark:** [github.com/BiDAlab/GAGAvatar-Benchmark](https://github.com/BiDAlab/GAGAvatar-Benchmark) — [arXiv HTML](https://arxiv.org/html/2508.00748)

- **Pedrouzo-Rodriguez, Gomez, Tolosana, Vera-Rodriguez, Daza, Morales, Fierrez, "Leveraging Avatar Fingerprinting: A Multi-Generator Photorealistic Talking-Head Public Database and Benchmark" (AVAPrintDB), arXiv 2603.26934 (v1 27 Mar 2026; v2 10 Sep 2026 = published version), Pattern Recognition vol. 179, art. 114834 (2026), DOI 10.1016/j.patcog.2026.114834.** — [arXiv abs](https://arxiv.org/abs/2603.26934)
  - **Systems evaluated:**
    - "Graph": the IJCB 2025 GCN on 109 landmarks.
    - DINOv2 and CLIP: frozen foundation-model frame features, with temporal attention and a triplet-trained projection head.
    - Fusion: mean of the three systems' scores.

    Scoring uses windowed embeddings compared by cosine similarity, averaged over the window-pair matrix. — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)
  - **Generators:** GAGAvatar (3D Gaussian splatting), LivePortrait (2D warping), HunyuanPortrait (diffusion, CVPR 2025). Full results are under Q2 and Q3. — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)

- **Chapariniya, Odobez, Dellwo, Vuković, "Micro-Expression-Aware Avatar Fingerprinting via Inter-Frame Feature Differencing", arXiv 2604.23247 (v1 25 Apr 2026), accepted to the TrustFA Workshop at IEEE FG 2026.** Note that this is a **workshop** paper, not the FG main track. — [arXiv abs](https://arxiv.org/abs/2604.23247)
  - **Input:** raw **grayscale RGB-derived frames at 128×128**, with no landmark extraction ("preprocessing-free", end-to-end).
  - **Architecture:** the F5C micro-expression backbone (ConvStack, then fully-connected-convolution and channel-correspondence-convolution with a k-NN graph, k=4) followed by **inter-frame feature differencing** d_t = f_{t+1} − f_t. A Conv3D temporal head produces a 256-d embedding, trained with SupCon (τ=0.07). The model has 0.53M parameters, trained from scratch on 64-frame clips. — [arXiv HTML](https://arxiv.org/html/2604.23247v1)
  - **Results:** on NVFAIR, overall AUC is **0.877**, versus 0.853 for the NVFAIR landmark baseline. Full results are under Q2. — [arXiv HTML](https://arxiv.org/html/2604.23247v1)
  - **Code:** footnote link [github.com/Mchapariniya/TrustFA-FG2026](https://github.com/Mchapariniya/TrustFA-FG2026). The repository contents were not verified. — [arXiv HTML](https://arxiv.org/html/2604.23247v1)

- **Gerstner, "Audio Avatar Fingerprinting: An Approach for Authorized Use of Voice Cloning in the Era of Synthetic Audio", arXiv 2603.20165 (20 Mar 2026), cs.SD. Preprint with no venue listed.** — [arXiv abs](https://arxiv.org/abs/2603.20165)
  - **Method:** TitaNet speaker verification, fine-tuned for 10 epochs with an angular softmax loss. The test audio's embedding is compared by cosine similarity with the **average embedding of the authorized driver's enrollment audio**. — [arXiv HTML](https://arxiv.org/html/2603.20165v1)
  - **Data:** an audio version of NVFAIR built from the 46 video-call subjects with one voice-conversion method (Kovela et al. 2023). It has 4 h 45 min of self-reenacted audio (1,899 files) and 90 h 12 min of cross-reenacted audio (74,331 files). Training uses 40 identities and 6 are held out. — [arXiv HTML](https://arxiv.org/html/2603.20165v1)
  - **Results:** real-vs-fake AUC is 0.98 on NVFAIR and 0.91 on In-the-Wild. **For avatar fingerprinting the paper gives only ROC curves**, with no AUC or EER number, and no held-out-generator test. — [arXiv HTML](https://arxiv.org/html/2603.20165v1)

**Lineage B: puppeteering detection in AI videoconferencing (transmitted latent, no enrollment)**

- **Vahdati, Nguyen, Stamm (Drexel), "Defending Low-Bandwidth Talking Head Videoconferencing Systems From Real-Time Puppeteering Attacks", CVPR 2023 Workshops (7th Workshop on Media Forensics), pp. 983–992, DOI 10.1109/CVPRW59228.2023.00105.**
  - **Abstract:** the defense uses biometric information in the facial expression and pose data already transmitted to the receiver. It requires no change to the transmission system, has low compute cost, and comes with a new benchmark dataset. — [CVF Open Access](https://openaccess.thecvf.com/content/CVPR2023W/WMF/html/Vahdati_Defending_Low-Bandwidth_Talking_Head_Videoconferencing_Systems_From_Real-Time_Puppeteering_Attacks_CVPRW_2023_paper.html); [MLAnthology](https://mlanthology.org/cvprw/2023/vahdati2023cvprw-defending)
  - **How the follow-up paper describes it:** the method "avoid[s] enrollment by decoding and re-encoding the received video for comparison". It "depends on facial-landmark estimation, which degrades under large head rotations and lighting artifacts", "relies on simple Euclidean distance", and runs at 32 FPS. — [NeurIPS 2025 PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf)
  - **Flag:** the description above is from the later paper by the same group, not the CVPRW paper itself, because the CVF PDF returned 403. The CVPRW paper's own numbers were not retrieved.

- **Vahdati, Nguyen, Nagano, Luebke, Gallo, Prashnani, Stamm, "Unmasking Puppeteers: Leveraging Biometric Leakage to Expose Impersonation in AI-Based Videoconferencing", arXiv 2510.03548 (v1 3 Oct 2025 … v4 12 May 2026), NeurIPS 2025 (poster).** The v1 title used "Disarm" instead of "Expose". Author order differs between the arXiv listing and the NeurIPS PDF. — [arXiv abs](https://arxiv.org/abs/2510.03548); [NeurIPS poster page](https://neurips.cc/virtual/2025/poster/117596); [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf); "Disarm" title visible at [Fraunhofer related-work listing](https://deepfake-demo.aisec.fraunhofer.de/related_work/2510.03548)
  - **Input:** the **transmitted pose-expression latent z_t**. No RGB decoding and no landmarks are used. — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
  - **Architecture:** a pose-conditioned, large-margin contrastive encoder (the "Enhanced Biometric-Leakage space", under 1M parameters) followed by an LSTM over a window of W frames. — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
  - **Comparison:** the live latent embedding h1(z_t) is compared by cosine similarity with the embedding of the **reference portrait R sent at call setup**, h2(f(R)). The method is enrollment-free. — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
  - **Results:** AUC 0.968 in-domain (Table 1 average), against 0.944 for Vahdati et al. 2023. It runs at about 75 FPS on an RTX 3090. Full results are under Q2. — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
  - **Code:** [github.com/MISLresearch/Unmasking-Puppeteers-Neurips25](https://github.com/MISLresearch/Unmasking-Puppeteers-Neurips25). At research time the repo holds only a README, LICENSE and CITATION file, with "Full implementation code will be released soon". The license is PolyForm Noncommercial 1.0.0. — [GitHub](https://github.com/MISLresearch/Unmasking-Puppeteers-Neurips25)

**Precursors (pre-2022, used as baselines)**

- **Agarwal et al. 2019** (person-specific soft biometrics) and **ID-Reveal** (Cozzolino et al., ICCV 2021). These are identity-aware deepfake detectors. On NVFAIR they reach only about 0.67–0.73 AUC. — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- Generic deepfake detectors fail at this task. Seven were tested by Unmasking Puppeteers: Efficient ViT, CCE ViT, CNN Ensemble, TALL, SupCon, CLRNet, LAA-Net. The best average is 0.648 (CLRNet). The paper's text also gives CLRNet's best single cell as 0.684 (MCNet on CREMA-D). — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4); [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf)

### Inferences
- There are two distinct verification references in the literature:
  - **Enrollment-based** (Prashnani, BiDA GCN, AVAPrintDB, Chapariniya, audio): compares against reference clips of the *claimed driver* or genuine self-reenactments.
  - **Portrait-based** (Unmasking Puppeteers): compares the driver's motion latent against the *target portrait*, which tests whether the latent's identity leakage matches the face.

  A watermark-based design could carry either reference: an enrolled driver template, or a hash or commitment to it.
- Only Lineage B uses the transmitted latent. Lineage A works on rendered video, so it is applicable to any third-party clip but sees the generator's (lossy) motion transfer.
- The research groups are concentrated:
  - NVIDIA: Prashnani, Nagano, Gallo, Luebke.
  - Drexel MISL: Vahdati, Stamm.
  - UAM BiDA Lab: Pedrouzo-Rodriguez, Tolosana, Fierrez.
  - Idiap/UZH: Chapariniya, Odobez.

  Gerstner's affiliation was not verified.

### Gaps
- The Vahdati CVPRW 2023 paper's own numbers, the exact transmitted features (keypoints vs landmarks) and its dataset size were not retrieved (CVF PDF returned 403).
- A Google Scholar "cited by" sweep could not be run directly. Searches surfaced no other 2023–2026 driver-identity papers beyond those listed. A few web-search snippets claimed things not found in the primary text: e.g. that 2604.23247 uses a "raw-RGB ResNet encoder", whereas the paper's ResNet18 variant is only an ablation that scores *worse* (0.547–0.759). These snippets were discarded.
- "Sahadewa et al." is cited by 2604.23247 as related work, but I could not identify that paper.

---

## Q2. Per-method details: modality, reference, metrics, in-domain vs unseen-generator vs unseen-dataset, generators, code and license

### Takeaway
In-domain AUCs cluster at **0.85–0.95 for rendered-video and landmark methods** and **about 0.97 for latent-domain detection**. Cross-generator transfer costs roughly 2–17 AUC points. Cross-dataset transfer costs up to about 28 points (CREMA-D→RAVDESS with LivePortrait). **EER is essentially never reported**; AUC is the universal metric. Code is public only for the BiDA Lab systems; NVIDIA's model is unreleased and the MISL repo is a placeholder.

### Cited Findings

**Summary table** (all values from primary papers)

| Method (venue) | Input | Reference compared against | Generators | In-domain AUC | Unseen generator | Unseen dataset | Code / license |
|---|---|---|---|---|---|---|---|
| Prashnani et al. (ECCV'24) | 126 landmarks → pairwise distances, 71-frame clips, temporal CNN | Self-reenacted (authorized) clips of the driver | face-vid2vid, LIA, TPS | 0.84–0.87 (avg 0.85) | avg 0.83 (range 0.82–0.87) | not reported | Not released; NVFAIR on request |
| Vahdati et al. (CVPRW'23) | Transmitted pose/expression data; re-encodes decoded video, uses landmarks [per NeurIPS'25 description] | Enrollment-free | Not retrieved | 0.944 avg on NVFAIR pool (as re-run in NeurIPS'25) | not applicable | 0.903 avg (NVC→CREMA-D/RAVDESS, as re-run in NeurIPS'25) | Not found |
| Unmasking Puppeteers (NeurIPS'25) | Pose-expression latent (no RGB) | Target reference portrait sent at call start | MCNet, 3DFaceShop, SDFR, EMOPortraits, LivePortrait | 0.968 avg (Table 1) | not tested as leave-one-generator-out | 0.925 avg (train NVC → test CREMA-D+RAVDESS) | Repo placeholder; PolyForm Noncommercial |
| BiDA GCN (IJCB'25) | 109 MediaPipe landmarks, GCN | One genuine clip of the target | GAGAvatar | 69.9% (RAVDESS), 82.6% (CREMA-D) | not applicable (single generator) | 75.4% / 78.8% | GitHub BiDAlab/GAGAvatar-Benchmark |
| AVAPrintDB Graph / DINOv2 / CLIP / Fusion (PR'26) | Landmarks or frozen ViT features | Windowed embeddings, cosine | GAGAvatar, LivePortrait, HunyuanPortrait | 72–91% single system; Fusion up to 95.2% | ΔAUC +2.2 to −20.4 pts | ΔAUC +7.9 to −28.9 pts | GitHub + Zenodo, public |
| Chapariniya et al. (FG'26 TrustFA) | Raw grayscale 128² frames, F5C + feature differencing | Same-driver videos across targets (SupCon); evaluated with self- vs cross-reenactment of each target | FV2V, TPS, LIA (NVFAIR) | 0.877 overall | 0.833–0.872 off-diagonal | not tested | GitHub Mchapariniya/TrustFA-FG2026 (unverified) |
| Audio Avatar Fingerprinting (arXiv'26) | Audio, TitaNet embeddings | Average enrollment embedding of authorized driver | 1 voice-conversion method | ROC curves only | not tested | not tested | not stated |

Sources for the table rows, in order:
- Prashnani et al.: [Prashnani HTML](https://arxiv.org/html/2305.03713v3)
- Vahdati et al. and Unmasking Puppeteers: [Unmasking Puppeteers HTML v4](https://arxiv.org/html/2510.03548v4); [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf); [MISL GitHub](https://github.com/MISLresearch/Unmasking-Puppeteers-Neurips25)
- BiDA GCN: [IJCB'25 HTML](https://arxiv.org/html/2508.00748)
- AVAPrintDB: [AVAPrintDB HTML v2](https://arxiv.org/html/2603.26934v2)
- Chapariniya et al.: [FG'26 HTML](https://arxiv.org/html/2604.23247v1)
- Audio Avatar Fingerprinting: [audio HTML](https://arxiv.org/html/2603.20165v1)

**AVAPrintDB in-domain AUC (%), intra-dataset and intra-generator** — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)

| Dataset / generator | Graph | DINOv2 | CLIP | Fusion |
|---|---|---|---|---|
| CREMA-D / GAGAvatar | 87.8 | 87.0 | 86.4 | 93.8 |
| CREMA-D / LivePortrait | 90.8 | 88.8 | 88.6 | 95.2 |
| CREMA-D / HunyuanPortrait | 82.6 | 79.8 | 81.0 | 87.6 |
| RAVDESS / GAGAvatar | 75.7 | 75.9 | 76.0 | 83.0 |
| RAVDESS / LivePortrait | 76.5 | 67.2 | 70.2 | 79.4 |
| RAVDESS / HunyuanPortrait | 72.3 | 74.0 | 77.0 | 78.8 |

**AVAPrintDB cross-generator ΔAUC, CREMA-D (points relative to the in-domain AUC)** — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)

| Train → test | Graph | DINOv2 | CLIP | Fusion |
|---|---|---|---|---|
| GAGAvatar → LivePortrait | −3.2 | −18.2 | −10.6 | −7.8 |
| GAGAvatar → HunyuanPortrait | −3.4 | −20.4 | −14.6 | −8.4 |
| LivePortrait → GAGAvatar | −14.3 | −18.9 | −17.3 | −16.8 |
| LivePortrait → HunyuanPortrait | −16.9 | −14.6 | −15.0 | −15.9 |
| HunyuanPortrait → GAGAvatar | +2.2 | −16.3 | −8.9 | −8.5 |
| HunyuanPortrait → LivePortrait | +1.9 | 0.0 | −5.8 | −0.9 |

- Interpretation: models trained on LivePortrait transfer worst. Models trained on HunyuanPortrait (diffusion) transfer best. Landmarks ("Graph") are the most generator-robust; DINOv2 and CLIP are the most generator-sensitive. — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)
- On RAVDESS the cross-generator deltas range from −1.8 to −13.7 points. — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)

**AVAPrintDB cross-dataset AUC (%)** — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)
- CREMA-D → RAVDESS with LivePortrait shows the largest drops:

  | System | In-domain → cross-dataset |
  |---|---|
  | Graph | 90.8 → 69.2 |
  | DINOv2 | 88.8 → 66.9 |
  | CLIP | 88.6 → 59.7 |
  | Fusion | 95.2 → 67.5 |

- RAVDESS → CREMA-D *improves* in most cells, by up to +7.9 points (Graph with GAGAvatar: 75.7 → 83.5).

**Chapariniya et al. FG'26 on NVFAIR (AUC, averaged over the 35 test target identities)** — [arXiv HTML](https://arxiv.org/html/2604.23247v1)

Main results:

| Method | Overall | FV2V | LIA | TPS |
|---|---|---|---|---|
| NVFAIR landmark baseline | 0.853 | 0.870 | 0.840 | 0.850 |
| F5C + feature differencing (ours) | **0.877** | 0.869 | 0.882 | 0.880 |
| F5C + pixel differencing | 0.861 | 0.849 | 0.866 | 0.868 |

Cross-generator matrix, feature differencing (rows = training generator, columns = test generator):

| Train \ Test | FV2V | TPS | LIA |
|---|---|---|---|
| FV2V | 0.869 | 0.833 | 0.842 |
| TPS | 0.838 | 0.879 | 0.872 |
| LIA | 0.852 | 0.869 | 0.902 |

Ablations:
- Representation: raw features score 0.649 and static features 0.610, so motion carries the signal.
- Clip length: T=16 gives 0.813; T=32 gives 0.862; T=128 gives 0.891.
- Backbone: ResNet18 variants score 0.547–0.759.

The baseline's own cross-generator pairs are not reported, so the claim that the method "matches or exceeds the baseline on most cross-generator pairs" cannot be checked. **[internal inconsistency]**
- Table II gives the baseline as 0.87, while the text and Table III give 0.853.
- Table VI swaps the TPS and LIA values.
- The text says Face-vid2vid→LIA (0.842) is below the baseline, yet the baseline LIA score is 0.840.

**Unmasking Puppeteers (NeurIPS'25)** — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4); [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf)

Cross-domain results (train on NVC, test on CREMA-D and RAVDESS), AUC in-domain → cross-domain:

| Generator | Proposed | Vahdati et al. 2023 |
|---|---|---|
| 3DFaceShop | .948 → .914 | .920 → .895 |
| MCNet | .950 → .919 | .942 → .921 |
| EMOPortraits | .936 → .917 | .927 → .894 |
| SDFR | .951 → .944 | .904 → .890 |
| LivePortrait | .939 → .931 | .929 → .915 |
| **Average** | **.945 → .925** | **.924 → .903** |

- **Temporal window matters:** AUC is about 0.77 at 10 frames and about 0.97 at 40 frames (about 1.3 s).
- **Ablations:**
  - Removing the biometric-leakage network: 0.635.
  - Removing the contrastive loss: 0.788.
  - Removing the MLP projection: 0.827.
  - Removing the extreme-pose (yaw) filter: 0.929, versus 0.966 for the full model.
- **[internal inconsistency]** The text claims "AUC > 0.97 across all combinations" and an average of 0.971 against Vahdati's 0.945. Table 1 shows an average of 0.968 against 0.944, with some cells below 0.97 (e.g. .952). The text also calls the cross-domain drop "only 5%", while the table shows about 2 points.

### Inferences
- Numbers are **not comparable across papers**:
  - Prashnani and Chapariniya use the original NVFAIR generators (FV2V, LIA, TPS) with per-target AUC.
  - Unmasking Puppeteers regenerates NVFAIR identities with 5 different generators, operates on latents, and uses window-level AUC.
  - AVAPrintDB pools all genuine and impostor pairs and reports bootstrap CIs.

  A student project should pick one protocol, most practically AVAPrintDB because it is fully public, and report AUC **and** EER (a gap in the literature).
- Modern generators (LivePortrait, GAGAvatar, HunyuanPortrait, EMOPortraits) are covered only by AVAPrintDB, which uses rendered video, and by Unmasking Puppeteers, which uses latents.

### Gaps
- No paper reports EER or TAR@FAR operating points. These matter for a biometric-plus-watermark system design.
- No leave-one-generator-out evaluation exists on diffusion generators other than HunyuanPortrait (e.g. EMO, Hallo, X-Portrait).
- The CVPRW'23 paper's own results were not retrieved.

---

## Q3. How large are NVFAIR and AVAPrintDB, and how are they obtained?

### Takeaway
**NVFAIR**: 161 identities and more than 650,000 synthetic videos from 3 pre-diffusion generators. It is gated behind an NVIDIA request form, with consent-revocation obligations. **AVAPrintDB**: 109 identities and 66,069 videos (22,023 per generator) from 3 modern generators. It is fully public on GitHub and Zenodo with released trial lists and checkpoints.

### Cited Findings

**NVFAIR (Prashnani et al., ECCV 2024)**

- **Identities:** 161 in total: 46 newly recorded video-call subjects, 24 from RAVDESS and 91 from CREMA-D. The split is 112 train / 14 validation / 35 test identities. — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Real capture:** subjects were recorded in pairs over video calls. Stage I is free-form answers to 7 prompts; Stage II is 30 scripted 2–3-sentence utterances. Per subject this gives about 76 real and 228 scripted videos on average, and about 3,840 cross-reenactments on average. — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Synthetic videos:** more than 650,000, from face-vid2vid, LIA and TPS. Generating them took more than 2,500 RTX 3090 GPU-hours. — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3); size also restated in [Chapariniya HTML](https://arxiv.org/html/2604.23247v1)
- **Demographics:** about 48% Asian and about 41% Caucasian among the new subjects (supplement). — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Generator release:** LIA and TPS videos are released **for the test set only**. — [NVFAIR page](https://research.nvidia.com/labs/nxp/nvfair/)
- **Access:** request via a Google "Dataset Request Form"; NVFAIR-v1 is currently available. Governance: IRB approval and informed consent. Subjects may revoke access at any time, and recipients must keep their contact information current. The page names **no explicit license**. The AVAPrintDB paper describes NVFAIR as "restricted, available on request" and excluded it for that reason. — [NVFAIR page](https://research.nvidia.com/labs/nxp/nvfair/); [project page](https://research.nvidia.com/labs/nxp/avatar-fingerprinting/); [AVAPrintDB HTML](https://arxiv.org/html/2603.26934v2)
- **Consent annotations:** each file records whether the participant consented to public display, and reuse should respect this. This matters for any figures in a student paper. — [Prashnani arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Re-rendered variant:** Unmasking Puppeteers built its own puppeteered set from NVFAIR identities with 5 generators (15 dataset-generator combinations). For example, the NVC subset has 1,331 train / 439 test authorized videos and 41,261 / 3,951 puppeteered videos. The paper calls the data "publicly available", but its release status is unclear: the repo has no data. — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4); [MISL GitHub](https://github.com/MISLresearch/Unmasking-Puppeteers-Neurips25)

**AVAPrintDB (Pattern Recognition 2026)**

- **Sources:**
  - CREMA-D: 85 of 91 actors kept, 6,120 source videos, 460×360 at 30 FPS.
  - RAVDESS: 24 actors, speech subset, 1,440 videos, 1280×720 at 30 FPS.

  Total 109 identities: 77 development and 32 evaluation, identity-disjoint (about 70/30), stratified by gender, age and ethnicity. — [AVAPrintDB HTML v2](https://arxiv.org/html/2603.26934v2)
- **Videos:** per generator, 7,560 self-reenactments and 14,463 cross-reenactments (22,023 total). Over 3 generators this gives 22,680 self, 43,389 cross and **66,069 total**. Every target-driver pair is rendered by all three generators, which allows paired cross-generator studies. — [AVAPrintDB HTML v2](https://arxiv.org/html/2603.26934v2)
- **Trials:** 153,216 genuine and 297,936 impostor comparisons per generator, released as CSV. The metric is AUC with 95% bootstrap CIs (1,000 resamples). — [AVAPrintDB HTML v2](https://arxiv.org/html/2603.26934v2)
- **Access:**
  - [github.com/BiometricsAI/AVAPrintDB](https://github.com/BiometricsAI/AVAPrintDB) as given in the paper. The search engine also indexes [github.com/BiDAlab/AVAPrintDB](https://github.com/BiDAlab/AVAPrintDB).
  - Zenodo DOI 10.5281/zenodo.20548978 (record page seen as [zenodo.org/records/20548979](https://zenodo.org/records/20548979)).
  - Protocols, code, metadata and pretrained checkpoints are public.
  - The paper says the source corpora are CREMA-D (ODbL) and RAVDESS (CC BY), and states no separate AVAPrintDB license.

  — [AVAPrintDB HTML v2](https://arxiv.org/html/2603.26934v2)
- **Earlier single-generator set:** the BiDA GCN paper released a GAGAvatar-only set at [github.com/BiDAlab/GAGAvatar-Benchmark](https://github.com/BiDAlab/GAGAvatar-Benchmark). It is 512×512 on a black background; video counts were not given in the text I read. — [IJCB'25 HTML](https://arxiv.org/html/2508.00748)

### Inferences
- For a time-boxed student project, AVAPrintDB is the practical choice: it is public, uses modern generators and has fixed trial lists. NVFAIR requires a request and possibly a wait, and only face-vid2vid is available for training.
- Both corpora are acted or studio-recorded, except the NVFAIR video-call part. Conversational, in-the-wild driver data is missing.

### Gaps
- Exact AVAPrintDB license and EULA for redistribution were not stated in the paper. Check the GitHub or Zenodo page.
- AVAPrintDB generator versions and output resolution were not stated.
- NVFAIR turnaround time and terms (e.g. non-commercial use) are not public.

---

## Q4. Failure modes, and adversarial attacks against fingerprinting

### Takeaway
Reported failure modes are:
- **generator shift**, the dominant one: up to −20 AUC points;
- **source-dataset shift**: up to −29 points;
- **weakly expressive drivers**;
- **generators that fail to transfer identifying expressions** (e.g. squinting);
- **extreme head pose and occlusion**;
- **lighting and blur**;
- **demographic disparities**, by age and ethnicity.

**No paper evaluates adaptive adversaries** such as motion style transfer or mimicry of the target driver's motion. Several papers explicitly list this as untested.

### Cited Findings
- **Prashnani:** performance is weaker on less expressive or neutral speakers. It drops when the generator fails to reproduce identifying expressions; the example is a squinting driver whose eyes stay shut in every output. Hand motion was avoided during capture, and occlusion, pose and resolution are not quantified. Robustness to compression is claimed in the supplement but was not verified. — [arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Unmasking Puppeteers** (Sec. 7):
  - Stated failure modes are extreme head rotation, occlusion (hands or objects), poor lighting or overexposure, and motion blur from rapid movement or blinking.
  - Extreme-yaw frames are excluded; AUC peaks at a ±18° threshold (0.966) and falls to 0.929 at ±38°.
  - Appearance robustness: eyeglasses 0.939, piercings 0.961, makeup 0.957. The text says 0.974 for makeup **[internal inconsistency]**.
  - Fairness: no subgroup gap larger than 1 AUC point.

  — [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
- **Landmark dependence:** the NeurIPS'25 authors argue that landmark-based pipelines (Vahdati'23) degrade under large head rotations and reconstruction lighting artifacts. — [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf)
- **BiDA GCN:** depends on landmark accuracy, which degrades under extreme poses or expressions. GAGAvatar does not always reproduce subtle or extreme driver expressions. Only acted, controlled data is used, and the results are described as preliminary. — [arXiv HTML](https://arxiv.org/html/2508.00748)
- **AVAPrintDB:**
  - Generator and dataset shift, as in Q2.
  - The authors suspect LivePortrait's high in-domain scores may reflect generator-specific regularities.
  - Demographics: age gives the largest disparities, with the 46–60 group worst on CREMA-D. Asian and Hispanic subjects score lower with HunyuanPortrait.
  - Stated as **not evaluated**: adversarial evaluation, identification, impersonator detection and continuous authentication.

  — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)
- **Chapariniya:**
  - "No robustness analysis against adaptive or adversarial attackers who might suppress the motion cues".
  - Diffusion generators are untested.
  - Weakly expressive subjects are untested.
  - Short clips hurt (T=16 gives 0.813).
  - Face-vid2vid-trained models transfer worst.

  — [arXiv HTML](https://arxiv.org/html/2604.23247v1)
- **Third-party critique [secondary, automated review]:** a Pith review of 2508.00748 argues that landmarks may encode static identity geometry, so the "motion biometric" claim could be overstated. It says a stronger test would use imitation or motion-retargeting attacks rather than unmodified impostor motion. — [Pith review](https://pith.science/paper/2508.00748)
- **Related adversarial work targets generation, not fingerprinting:** SyncBreaker (arXiv 2604.08405) perturbs portrait and audio inputs to disrupt audio-driven talking-head generation. It is a protection against misuse, not an attack on driver verification. — [arXiv PDF](https://arxiv.org/pdf/2604.08405)

### Inferences
- Several attacks are plausible but unpublished:
  - motion style transfer or retargeting that imposes the victim's motion idiosyncrasies on the attacker's driving signal;
  - expression suppression or neutral driving, since methods are weak on low-expressivity drivers;
  - latent-space perturbation, for latent-domain detectors.

  Any of these would be a novel evaluation axis. Note that these attacks would also face a watermark channel in a combined system.
- Generator shift is the single largest weakness. A watermark that carries generator-independent information (e.g. a signed driver-identity claim) could complement a biometric channel that degrades across generators.

### Gaps
- I found no published study of mimicry or impersonation attacks (a professional imitator, or automated motion-style transfer) against avatar fingerprinting.
- No resolution or compression sweeps were found in the main papers. Prashnani's supplement is the only claimed source, and I did not verify it.

---

## Q5. Does any work combine avatar fingerprinting with watermarking or provenance?

### Takeaway
**No.** None of the driver-identity papers integrates watermarking or provenance. Prashnani et al. explicitly position their passive method as an alternative to watermarking and active forensics. AVAPrintDB mentions "provenance" only for dataset documentation. Unmasking Puppeteers mentions watermarking only as a release-policy measure for *detector outputs*. A combined driver-biometric plus watermark scheme therefore appears to be open territory as of 2026-10-16, within the limits of the search below.

### Cited Findings
- **Prashnani et al.:** the method is passive and does not embed watermarks. The paper contrasts itself with watermarking or active-forensics approaches and states it is not focused on detecting synthetic media. — [arXiv HTML v3](https://arxiv.org/html/2305.03713v3)
- **Unmasking Puppeteers:** the only watermark mention is in the NeurIPS checklist: "Release plan includes watermarking detector outputs and open-sourcing under a non-commercial license." It contains no technical watermarking component. — [NeurIPS PDF](https://papers.nips.cc/paper_files/paper/2025/file/a34308d616e3193199cfc7e82801a19f-Paper-Conference.pdf); [arXiv HTML v4](https://arxiv.org/html/2510.03548v4)
- **AVAPrintDB:** no watermarking of generated avatars. "Provenance" refers only to documenting the source datasets and the generation pipeline. — [arXiv HTML v2](https://arxiv.org/html/2603.26934v2)
- **Chapariniya and the audio fingerprinting paper:** watermarking is not mentioned. — [Chapariniya HTML](https://arxiv.org/html/2604.23247v1); [audio HTML](https://arxiv.org/html/2603.20165v1)
- **Adjacent and non-academic sources:**
  - USPTO patents 12155771 and 12301728 ("Talking head digital identity authentication") describe blockchain-stored hashes of talking-head files plus a watermark or logo, authenticated by hash match. These are not peer-reviewed and use no driver biometrics. — [USPTO 12301728](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12301728); [USPTO 12155771](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12155771)
  - GAGAvatar's paper (arXiv 2410.07971) mentions tracing misuse through a watermark system on the generator side, with no driver verification. — [arXiv PDF](https://arxiv.org/pdf/2410.07971)
  - A talking-head generation survey recommends consent verification, watermarking and provenance metadata as safeguards, but in general terms only. — [arXiv 2308.16041](https://arxiv.org/html/2308.16041v2)

### Inferences
- Novelty angle for the student project: the fingerprinting papers answer "who drives this?" passively. Watermark and provenance work answers "which generator or session made this?" They are complementary, and nobody has fused them. Candidate designs:
  - (a) embed a commitment to the enrolled driver template, or the sender's latent-identity embedding (cf. Unmasking Puppeteers' portrait-vs-latent check), as a watermark, then verify it against the biometric extracted from the rendered motion;
  - (b) use the biometric score to gate or sign watermark insertion at the sender;
  - (c) evaluate whether watermark embedding degrades the subtle motion cues that fingerprinting relies on.

  Chapariniya shows micro-motion carries the signal, so this risk is real.
- Unmasking Puppeteers' setting (sender-side latent, receiver-side rendering) is the most natural host for a watermark: the sender could watermark the latent stream or the rendered output. Its code is not yet released, however.

### Gaps
- The search was not exhaustive. I could not run a Google Scholar "cited by" sweep, and works appearing after early October 2026 may be missed.
- I found no paper on "biometric watermarking" of driving signals specifically for reenactment. Adjacent fields (identity-preserving watermarks for face-swap or deepfake provenance) were outside this scope and may be covered by other research notes.
