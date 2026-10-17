# Cryptographic Provenance, Payload Design, and Privacy/Consent for Identity-Claim Watermarks on AI Talking-Head Reenactment Video

Scope: binding claims {target identity, declared driver, generator, session} to a reenactment video. Research date: 2026-10-16. "Secondary" marks claims that come only from law-firm, vendor or blog summaries, not the primary instrument.

## 1. C2PA: current spec, soft bindings, Durable Content Credentials, live video, AI-generation assertions, and how a short watermark references a signed manifest

### Takeaway
The current C2PA spec is **2.4 (April 2026)**. 2.3 (December 2025) added live video, and 2.2 (May 2025) added the Soft Binding Resolution API.

In C2PA, a watermark is a *soft binding*: a lookup key that leads a resolver to a manifest in a repository. It is explicitly not an integrity proof ("a soft binding shall not be used as a hard binding"). A "Durable Content Credential" is simply a credential with a soft binding that makes it discoverable.

The `c2pa.soft-binding` assertion records `alg` plus per-block `value`s, with an optional `timespan` (ms) and `region` per block. That fits per-segment video watermarks. Gen-AI is declared with `c2pa.created` plus IPTC `trainedAlgorithmicMedia`, and 2.4 adds a `c2pa.ai-disclosure` assertion.

Generator, driver and session claims belong in the COSE-signed manifest, not in the watermark bits.

### Cited Findings
- **Versions.** The 2.2 Technical Specification is dated 2025-05-01 and its Explainer 2025-04-22 ([C2PA 2.2 spec PDF](https://spec.c2pa.org/specifications/specifications/2.2/specs/_attachments/C2PA_Specification.pdf); [2.2 Explainer](https://spec.c2pa.org/specifications/specifications/2.2/explainer/_attachments/Explainer.pdf)). The 2.3 version history (Sec. 5.3.1) reads "2.3 – December 2025", and one listed change is "Introduced specifications for live video streaming support". 2.4 is confirmed in the next bullet ([C2PA 2.3 spec](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html)). C2PA announced "Content Credentials 2.3" and said it is now "enabled for live video" for broadcast and streaming ([C2PA announcement](https://c2pa.org/the-c2pa-launches-content-credentials-2-3-and-celebrates-5-years-of-impact-across-the-digital-ecosystem/)).
- **2.4 (April 2026) is current.** Its version history, Sec. 5.3.1 "2.4 - April 2026", lists:
  - new crJSON (JSON-LD) serialization, which is "not independently verifiable";
  - a new Repository Receipt assertion (`c2pa.repository-receipt`, proof that a manifest was ingested by a Manifest Repository);
  - a new **AI Disclosure assertion (`c2pa.ai-disclosure`)** "for machine-readable AI transparency info";
  - an Environmental Sustainability assertion;
  - HTML and structured-text embedding;
  - the mandatory actions assertion now only in `created_assertions`;
  - a new `relatedAssertions` action parameter;
  - "a recommendation that `c2pa.watermarked.bound` actions reference their corresponding soft binding assertion(s)";
  - `digitalSourceType` allowed in ingredient assertions;
  - Live Video extended to dynamically packaged content, with a recommendation for deterministic signature algorithms (e.g., ISO/IEC 23009-9 REaP) to avoid breaking segment caching.
  
  Source: spec HTML retrieved by curl and grepped, 2026-10-16 ([C2PA 2.4 spec](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)). I did not read the field contents of `c2pa.ai-disclosure` (Sec. 18.28).
- **Soft-binding assertion schema (2.4 CDDL, Sec. 18.10).** Primary source ([C2PA 2.4 spec](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)).
  - `soft-binding-map` has these fields:
    - `alg`: from the algorithm list, else the claim's `alg_soft`; no default.
    - `blocks`: one or more of `{scope, value}`.
    - Optional: `pad`/`pad2`, `name`, `alg-params` (bstr), `bindingMetadata` (description/contact), `metadata`.
    - `url` is "Unused and deprecated".
  - `value` is a "CBOR byte string describing, in algorithm specific format, the value of the soft binding computed over this block".
  - `scope` may contain:
    - `timespan` = {`start`, `end`} in **milliseconds from media start**;
    - `region` (regions-of-interest);
    - `extent`, which is deprecated.
- **Soft binding definition.** A soft binding is a content identifier that is "not statistically unique, such as a fingerprint," or is embedded as an invisible watermark. Sec. 9.3.1 says: "Because they serve a different purpose, a soft binding shall not be used as a hard binding." It also says that if a manifest is stripped but a copy survives in a provenance store, the two can be re-associated through soft bindings ([C2PA 2.2 spec](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)).
- **Invisible watermark as a manifest pointer.** Sec. 2.4.3 defines an invisible watermark as information embedded "in a substantially human imperceptible way" that can "store a reference to a C2PA Manifest" ([C2PA 2.2 spec](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)).
- **Durable Content Credential.** Sec. 2.4.1 defines it as a Content Credential for which there exist "one or more soft bindings that enable its discovery in a manifest repository." Sec. 2.4.5 defines a Manifest Repository as a store searchable by content binding ([C2PA 2.2 spec](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html); [2.3 spec](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html)). The 2.2 Explainer describes durable credentials as hard binding plus soft binding ([2.2 Explainer](https://spec.c2pa.org/specifications/specifications/2.2/explainer/_attachments/Explainer.pdf)).
- **Soft Binding Resolution API.** 2.2 added a supplementary spec standardising how a client sends a soft-binding value, a manifest ID or the asset itself to an endpoint and receives manifest stores back. 2.2 also added ingredient-assertion fields for soft-binding manifest recovery ([C2PA Soft Binding API](https://spec.c2pa.org/specifications/specifications/2.2/softbinding/Decoupled.html); [2.2 Guidance](https://spec.c2pa.org/specifications/specifications/2.2/guidance/Guidance.html)).
- **Approved algorithm list.** Sec. 9.3.2 says: "All soft bindings shall be generated using one of the algorithms listed in the soft binding algorithm list" ([C2PA 2.2 spec](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)). Entries are added by pull request and approved by the C2PA Technical Working Group ([GitHub list repo](https://github.com/c2pa-org/softbinding-algorithm-list)). On 2026-10-16 the published JSON had 28 entries ([softbinding-algorithm-list.json](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json)).
  - Video-capable entries: Digimarc Validate, ATSC A/336, ISCC (fingerprint, ISO 24138), Steg.AI, Kinetiq Watercast, castLabs, NAGRA NexGuard, Mentaport, SonicOrigin, Microsoft InvisMark (image+video), Microsoft WavMark (audio, video), MarkAny and Verimatrix.
  - Adobe TrustMark (variants Q, C and P) is listed for images only.
  - The JSON gives no payload sizes.
  - Meta's VideoSeal/PixelSeal do **not** appear on the list.
- **Cross-layer contradiction risk.** Nemecek et al. (arXiv 2603.02378, v1 2 March 2026, v2 18 April 2026, CVPR 2026 APAI Workshop) describe the "Integrity Clash": a valid C2PA manifest claiming human authorship can coexist with pixels carrying an AI watermark, and each check passes independently because "neither conditions on the output of the other". They say "metadata washing" can produce such "authenticated fakes" just by omitting one assertion field, which the spec permits. They propose a cross-layer audit protocol that jointly evaluates manifest and watermark status, reporting 100% classification on 3,500 images (authors' claim) ([arXiv 2603.02378](https://arxiv.org/abs/2603.02378)).
- **AI-generation source type.** The 2.2 change log introduces the URI form `http://c2pa.org/digitalsourcetype/trainedAlgorithmicData`, replacing the short label `c2pa.trainedAlgorithmicData`, plus a new `.../empty` value. Since 2.1 (September 2024), "Either a c2pa.created or a c2pa.opened is now mandatory in a standard manifest." Claim generators "shall not redact assertions with a label of c2pa.actions or c2pa.actions.v2" ([C2PA 2.2 spec](https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html)). For **media**, the 2.4 spec's example for a gen-AI asset is a `c2pa.actions` assertion "starting with a c2pa.created action" whose `digitalSourceType` is `http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia` (IPTC vocabulary). C2PA's own `trainedAlgorithmicData` "differs ... in that the result isn't a media type ... but is a data format (e.g., CSV, pickle)". For "trained algorithmic" assets, "one or more ingredients may be added" (e.g., the source photo or driving video) ([C2PA 2.4 spec](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)).
- **Live video.** 2.3 Sec. 19 "Live Video" contains: Introduction; Architecture; a per-segment "C2PA Manifest Box" method; a "Verifiable Segment Info" method; a generation process; and a validation process. Sec. 9.2.3 says fMP4 assertions are "combined with chunk-specific hashing information" ([C2PA 2.3 spec](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html)). **Primary text from 2.4 Sec. 19:**
  - It applies to ISO BMFF and CMAF and "does not support MPEG Transport Streams".
  - Each segment is validated independently. Segment hashes use a standard `bmff-hash-map`, and the manifest store sits in a `uuid` "C2PA Manifest Box".
  - There are two signing methods: (a) a per-segment C2PA Manifest Box; (b) "Verifiable Segment Info", carried in an `emsg` box "along with session keys". Validators need not support both.
  - The init segment's uuid box hashes the `moov` box "to ensure that the C2PA Manifest corresponds to the specific media content, which prevents replay attacks and content substitution".
  - A `c2pa.livevideo.segment` assertion carries `sequenceNumber`, `streamId` (e.g., a UUID) and `continuityMethod`. The only defined method, `c2pa.manifestId`, chains each segment to the previous via `previousManifestId` ([C2PA 2.4 spec](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)).
  
  The spec text confirms per-segment signing and no MPEG-TS support. It says the approach is "agnostic of manifest and delivery protocols", which partly supports the claim that HLS M3U8 and DASH MPD manifests need no changes. Still secondary only: typical segment length of 1–10 s, and that non-C2PA players safely ignore the data ([Irdeto blog](https://irdeto.com/blog/extending-trust-into-live-video-with-c2pa); [5centsCDN](https://www.5centscdn.net/blog/what-is-c2pa-content-provenance/); [TechRxiv preprint](https://www.techrxiv.org/users/900344/articles/1275834/master/file/data/Preprint/Preprint.pdf?inline=true)).
- **Identity in manifests (CAWG).** The CAWG identity assertion (label `cawg.identity`) binds a credential holder's verified identity to their role in the asset. There are two modes:
  - X.509/COSE signature (`sig_type` `cawg.x509.cose`).
  - Identity claims aggregator (`cawg.identity_claims_aggregation`). The aggregator verifies claims from identity providers and issues an asset-specific credential. Per secondary sources, version 1.1 introduced an aggregator that maps a long-lived identifier to locally significant identifiers.
  
  The Rust SDK treats aggregator issuers as untrusted unless they are on an allow-list ([CAI open-source docs: CAWG identity](https://opensource.contentauthenticity.org/docs/manifest/cawg-id); [Rust SDK CAWG docs](https://opensource.contentauthenticity.org/docs/rust-sdk/docs/cawg-identity/)). One secondary source says CAWG Identity 1.2 was DIF-ratified on 15 December 2025 ([docs.rs encypher-c2pa](https://docs.rs/crate/encypher-c2pa/1.0.0); [DIF CAWG progress report](https://blog.identity.foundation/progress-report-from-the-creator-assertions-wg/)). A secondary commentary discusses the privacy risks of identity assertions in Content Credentials ([SoftwareSeni](https://www.softwareseni.com/c2pa-identity-assertions-and-the-privacy-risks-of-content-credentials)).

### Inferences
- **Payload-as-pointer architecture, which matches C2PA's model.** The watermark carries a short identifier (for example a 32–64-bit manifest or record ID). The resolver uses it to fetch a COSE-signed C2PA manifest from a repository through the Soft Binding Resolution API. That manifest holds:
  - (a) `c2pa.actions` with `c2pa.created` and an AI digitalSourceType;
  - (b) a custom assertion (e.g., `org.<project>.reenactment.v1`) with `target_id_commitment`, `driver_id_commitment`, `generator` (model name, version, weights hash), `session_id`, `nonce`, `epoch` and `consent_record_ref`;
  - (c) a hard binding (BMFF hash) and optionally a fingerprint;
  - (d) a `c2pa.soft-binding` assertion recording the watermark algorithm and value.
  
  Authenticity comes from the manifest signature, never from the watermark bits.
- **The watermark ID alone proves nothing.** An attacker can copy a valid watermark onto other content (transplant) or replay it. A verifier must therefore re-check the content it holds against the resolved manifest:
  - hard-binding hash if the file is intact;
  - otherwise a perceptual fingerprint or a per-segment content hash stored in the manifest;
  - and, for this project, a face-identity check that the rendered face matches the claimed target.
  
  This is the cross-layer audit idea from arXiv 2603.02378 applied to transplant attacks.
- **Generator, driver and session claims go in the manifest.** Putting them in watermark bits spends capacity and leaks information to anyone holding the detector.
- **Registering the algorithm.** To be C2PA-conformant, the project's watermark algorithm would need an entry on the soft-binding list. For a B.Tech prototype it is reasonable to emit a non-registered `alg` and document this as a deviation.
- **Live video.** For streamed reenactment (video calls), per-segment manifests (Sec. 19) give a natural place to carry per-segment session nonce and epoch values, which aligns with segment-wise watermark decoding.

- **Mapping onto the soft-binding schema.** One `blocks[]` entry per watermarked segment or time-window (`timespan` start/end ms; optionally `region` = face bounding area), with `value` = the decoded payload ID bytes. Add a `c2pa.watermarked.bound` action referencing that soft-binding assertion (2.4 recommendation). The live-video `streamId` and `sequenceNumber` serve naturally as session ID and per-segment counter, so these need not consume watermark bits. The `previousManifestId` chain gives replay and reordering detection at the manifest layer.
- **Ingredients.** List the target reference image and driving video as ingredients, ideally redacted or hashed for privacy, and mark the reenactment as `trainedAlgorithmicMedia`. The new `c2pa.ai-disclosure` assertion (2.4) is the forward-looking place for AI transparency fields once its schema is checked.

### Gaps
- I did not read the body of Sec. 18.28 (`c2pa.ai-disclosure` fields), Sec. 19.4 (Verifiable Segment Info details), or the Soft Binding Resolution API endpoints.
- I found no source specifying a recommended watermark payload length for C2PA manifest IDs. Payload size is not in the algorithm list JSON.

## 2. Payload design: capacity, authenticated encoding, nonces/replay resistance, ECC

### Takeaway
Open-source video watermarks carry 96–256 raw bits:
- VideoSeal 96-bit (now "legacy");
- VideoSeal v1.0 256-bit;
- PixelSeal 256;
- ChunkySeal 1024;
- TrustMark 100;
- MBRS 256.

After error-correction overhead, the usable payload is smaller. With ~64–96 usable bits, the sound design is a random or keyed ID, plus an optional truncated MAC, plus ECC. Nonces and epochs live in the signed manifest. The MAC only helps a verifier who holds the key; public verifiability comes from the C2PA signature.

### Cited Findings
- **VideoSeal releases.** Meta's repo lists the initial December 2024 release as a "96-bit baseline model" (now labelled legacy) and "VideoSeal v1.0 with improved 256-bit model and enhanced robustness" (March 2025) as the default. It also lists PixelSeal (256 bits) and ChunkySeal (1024 bits, "High Capacity") ([facebookresearch/videoseal](https://github.com/facebookresearch/videoseal)).
- **VideoSeal paper.** The paper (arXiv 2412.09492) reports higher robustness than baselines "especially under challenging distortions combining geometric transformations and video compression". It trains with differentiable augmentations including H.264. It notes that "MBRS and TrustMark offer higher message capacities (256 and 100 bits)" but degrade under common transformations ([Video Seal paper, HF mirror](https://huggingface.co/papers/2412.09492); [Meta AI publication](https://ai.meta.com/research/publications/video-seal-open-and-efficient-video-watermarking)).
- **PixelSeal.** The PixelSeal paper (arXiv 2512.16874) reports TrustMark-P is "significantly less robust than PIXEL SEAL" ([PixelSeal](https://arxiv.org/pdf/2512.16874)).
- **Capacity critique.** A third-party paper (arXiv 2510.12812) reports that retrained VideoSeal fails to encode 1024 bits in an image task ([arXiv 2510.12812](https://arxiv.org/abs/2510.12812v1)).
- **MoSign (arXiv 2609.29603).** Che, Carr, Xu, Lu and Yuan; submitted 30 August 2026; cs.CR; accepted at the SASHIMI 2026 workshop (MICCAI); submitted to NeurIPS 2026 (per the listing).
  - It embeds a keyed, time-varying message in a motion model's style latent for challenge-response authentication of *anonymous VR users*.
  - The message is bound to an epoch counter and session nonce for replay resistance.
  - It identifies a "recapture" attack (render, record, re-estimate) as the main realistic threat.
  - It reports a false-accept rate of 10^-4 on clean and most channels, and detection AUC 0.51 (near chance, meaning the watermark is undetectable to an observer).
  - Caveat: abstract/listing only; the domain is VR motion, not pixel video ([arXiv 2609.29603](https://arxiv.org/abs/2609.29603)).
- **ATSC A/336.** ATSC A/334–A/336 broadcast watermarking is a C2PA-listed soft binding for audio, video and image ([softbinding-algorithm-list.json](https://spec.c2pa.org/softbinding-alg-list/softbinding-algorithm-list.json)).

### Inferences
- **Bit budget example for a 96-bit raw channel.**
  - ID field (~48–64 bits). A random or keyed record ID. 2^48 gives roughly 2.8×10^14 IDs; collisions are negligible for a project, and IDs are unguessable if random.
  - Truncated tag (~16–32 bits). Example: HMAC-SHA256(K, ID ‖ epoch) truncated. It lets a key-holding verifier (the generator operator, or a regulator given the key) reject forged or random IDs offline with probability 2^-16 to 2^-32 per guess. It adds no public verifiability.
  - ECC. A BCH or Reed-Solomon outer code is common practice. Alternatively, rely on the model's own bit accuracy and use repetition across frames or segments with majority voting.
  - With 256-bit VideoSeal v1.0 there is room for a 128-bit ID, a 64-bit tag and strong ECC.
- **Use a MAC, not a signature, in the bits.** Even a short EdDSA signature (64 bytes = 512 bits) exceeds capacity, so a MAC is the only in-band authenticator that fits. Signatures belong in the manifest.
- **Replay and transplant resistance.** The watermark should not be the only proof. Bind the manifest to the content with a hard hash plus a perceptual fingerprint. Optionally derive the per-segment watermark from (ID, segment index), so a segment copied into a different position or video fails the MAC or index check. This applies MoSign's epoch/nonce idea to segments; it is an inference, and MoSign itself does not address video.
- **Session nonce placement.** The nonce goes in the manifest. In the bits it would cost ≥32 bits and add nothing that the ID→manifest lookup doesn't already provide.
- **Avoid deterministic IDs derived from identity.** If the ID is a hash of (target, driver), every video of the same pair carries the same mark and becomes linkable. Use fresh random IDs per session or clip.

### Gaps
- I found no measured bit-accuracy figures for the 96-bit VideoSeal under specific attacks here; they are in arXiv 2412.09492, which I did not fully read.
- I did not read MoSign's full paper, so the exact MAC construction and nonce sizes are unverified.
- I found no standard that prescribes ECC or MAC truncation lengths for media watermark payloads.

## 3. Identity commitments: why not derive them from face embeddings, and safer alternatives

### Takeaway
Do not put any function of a face embedding into a public watermark or manifest. Deep face templates have low entropy and can be inverted:
- fuzzy commitments are reversible (Keller et al.);
- IronMask leaks the template across multiple enrolments (Zhu & Wang, PoPETs 2025);
- score-only reconstruction has been reported.

Use enrollment-issued pseudonymous IDs (random), committed with a salted or keyed hash, and resolve them to real identity only through an access-controlled registry.

### Cited Findings
- **Keller, Osadchy & Dunkelman (arXiv 2012.13293).** "Fuzzy Commitments Offer Insufficient Protection to Biometric Templates Produced by Deep Learning".
  - Deep face templates have "too little entropy". They present a reconstruction attack that recovers a face image from a protected template.
  - More than 78% of reconstructed templates unlock the account at 0.1% FAR in the simplest scenario; cross-system success is roughly 50–120× FAR.
  - Conclusion: fuzzy commitment is insufficient to offer either irreversibility or unlinkability. The attack assumes white-box access to the feature extractor ([arXiv 2012.13293](https://arxiv.org/pdf/2012.13293); [abstract](https://arxiv.org/abs/2012.13293v1)).
- **Zhu & Wang (arXiv 2409.12884; PoPETs 2025, pp. 728–744).** "Hypersphere Secure Sketch Revisited: Probabilistic Linear Regression Attack on IronMask in Multiple Usage".
  - IronMask is a hypersphere fuzzy-commitment scheme for face templates. The attack exploits the linearity of the error-correcting code to recover the original template from multiple protected templates, breaking renewability and unlinkability.
  - On ArcFace (n=512, α=16): ~5.3 days with 511 templates; ~621 days with 2 templates (SVD solver).
  - The attack still applies under noise. The authors propose two mitigations ([arXiv 2409.12884](https://arxiv.org/abs/2409.12884v1); [PoPETs](https://petsymposium.org/popets/2025/popets-2025-0154.php)).
- **Score-only reconstruction (arXiv 2601.17620, 2026).** Reported to reconstruct a biometric template by observing only authentication success/failure. Abstract-level only; unverified ([arXiv 2601.17620](https://www.arxiv.org/pdf/2601.17620)).
- **Alternative template protections.** SlerpFace (arXiv 2407.03043) and FaceCloak (arXiv 2504.06131, FG 2025) are newer face template protection schemes. I did not see them tested against Keller-style attacks ([SlerpFace](https://arxiv.org/html/2407.03043v2); [FaceCloak](https://arxiv.org/pdf/2504.06131v2)).
- **Avatar Fingerprinting (Prashnani et al., ECCV 2024, NVIDIA).** Verifies *who is driving* a synthetic talking head from facial-motion signatures, independent of the rendered appearance. Average AUC 0.85, and 0.83 on unseen generators ([ECCV 2024 paper](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/2330_ECCV_2024_paper.php); [NVIDIA project page](https://research.nvidia.com/labs/nxp/avatar-fingerprinting)).

### Inferences
- **Recommended scheme.**
  - At enrollment (with consent), issue `pid = random 128-bit`. Store (pid → person, consent scope) in a private registry.
  - In the manifest, put `commit = HMAC(K_registry, pid ‖ session_salt)`, or a hash commitment `H(pid ‖ r)` with `r` revealed only to authorised verifiers.
  - Keyed hashes are only as strong as the secrecy of the key. Unkeyed hashes of low-entropy identifiers (phone or Aadhaar numbers, names) are brute-forceable.
- **Per-video salts give unlinkability.** Without them, the same commitment across videos lets anyone link all videos of a person, which is itself a privacy harm.
- **Publishing the target identity is a disclosure.** Putting the target identity in a publicly resolvable manifest discloses that this person's likeness was reenacted. Use tiered resolution:
  - public: "AI-generated, consented reenactment, generator X";
  - authorised (victim, platform, regulator): commitment opening.
  
  CAWG identity-aggregator patterns (local identifiers mapped by a trusted aggregator) fit this model.
- **Matching the face, privately.** A verifier can still check "does the rendered face match the claimed target?" by comparing with a template held privately by the registry. The template is never put in the content.
- **Declared driver.** The driver claim can be cross-checked by motion signatures (avatar fingerprinting) rather than by embedding biometrics in the payload.
- **ISO/IEC 24745.** The principles commonly cited from it are irreversibility, unlinkability and renewability. The schemes above fail exactly these: Keller breaks irreversibility, and Zhu & Wang break unlinkability and renewability.

### Gaps
- ISO/IEC 24745 (Biometric information protection): I did not retrieve the ISO page or text in this session, so its requirement wording (irreversibility, unlinkability, renewability, and the edition year, believed to be 2022) is unsourced here and should be verified at iso.org.
- There is no primary source on attacks specifically against commitments embedded in watermarks or manifests. The risk is inferred from template-inversion literature.

## 4. Consent and authorized-use frameworks for avatars and digital likeness

### Takeaway
"Authorized use" in the research literature comes mainly from NVIDIA's ECCV 2024 avatar-fingerprinting paper. It frames the problem as verifying that a synthetic talking head is driven by the person authorised to use that likeness. I found no NVIDIA policy or product framework beyond that paper and a general Trustworthy-AI blog. The legal side is a patchwork of licensing and consent rules (NO FAKES proposal, California AB 2602, New York digital replica law), an industry "Digital Likeness Directive", and data-protection consent (GDPR; India's DPDP Act).

### Cited Findings
- **NVIDIA's framing.** The paper frames the need for "a mechanism to verify whether a rendered avatar is trustworthy". It built the first large-scale dataset of real calls plus synthetic videos in which one person's appearance is driven by another's expressions ([ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/2330_ECCV_2024_paper.php); [NVIDIA PDF](https://research.nvidia.com/labs/nxp/avatar-fingerprinting/media/avatar_fingerprinting.pdf)).
- **NVIDIA policy.** The Trustworthy AI blog says developers should check for appropriate consent before using a person's image or voice, and mentions avatar fingerprinting research ([NVIDIA blog](https://blogs.nvidia.com/blog/what-is-trustworthy-ai/)).
- **Digital Likeness Directive.** StoryFile / Authentic Interactions launched it as "an open standard giving people control over AI recreations" (vendor announcement; I did not review its contents) ([StoryFile](https://www.storyfile.com/news/digital-likeness-directive)).
- **US law (secondary, MoFo, Sept 2025).**
  - The NO FAKES Act would create a federal digital-replication right that is licensable but not assignable during the person's lifetime.
  - California AB 2602 limits contract clauses that let a digital replica replace a performer's services unless the performer had independent representation and specific disclosures.
  - New York has a digital-replica law for performer contracts ([MoFo](https://www.mofo.com/resources/insights/250922-digital-avatars-deep-dive-series-navigating)).
- **Consent practice (law-firm commentary).** Firms recommend separate, specific, written consent per material use. A single checkbox may not satisfy GDPR for biometric data ([wcr.legal](https://wcr.legal/ai-avatar-licensing-agreement-checklist/); [Traverse Legal](https://www.traverselegal.com/blog/ai-avatar-legal-risks/)).
- **India DPDP Rules 2025.** Notified 13/14 November 2025. Phasing:
  - Board provisions immediately.
  - Consent Manager (Rule 4) after 1 year, around 13 November 2026.
  - Notice, verifiable consent, security and breach rules (Rules 3, 5–16, 22–23) after 18 months, around May 2027.
  
  Notices must be standalone, in plain language, with an itemised description of data and purpose. I found nothing about biometric-specific rules in these sources ([PIB DPDP Rules PDF](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf); [Hogan Lovells](https://www.hoganlovells.com/en/publications/indias-digital-personal-data-protection-act-2023-brought-into-force-); [DSK Legal](https://dsklegal.com/?p=26455)).

### Inferences
- **Make consent a first-class signed artifact.** The target signs (or the platform attests on their behalf) a consent record scoped to {driver(s) allowed, generator(s), purpose, validity period, revocation endpoint}. The manifest references it by hash (`consent_record_ref`). The watermark ID resolves to the manifest. Verification checks: the consent record is valid and unrevoked at the generation timestamp, and the declared driver and generator are within its scope.
- **Consent covers both people.** For an Indian deployment, collecting the target's face and the driver's face or motion is processing of personal data under the DPDP Act. Specific, itemised consent from *both* target and driver is the conservative design, even before the 2027 compliance date.
- **Revocation.** Renewable pseudonymous IDs (Sec. 3) let a consent withdrawal invalidate future generations without re-issuing biometrics.

### Gaps
- I found no NVIDIA "authorized-use framework" document beyond the research paper and blog. If the user's reference is to something else (e.g., NVIDIA ACE / Audio2Face licence terms), it was not located.
- DPDP Act treatment of biometric data and children's data was not covered by the sources retrieved.
- I did not review the contents of the Digital Likeness Directive or any consent-receipt standard (e.g., Kantara).

## 5. Regulation (status as of 2026-10-16): EU, India, US, China

### Takeaway
- **EU.** AI Act Art. 50 applies from 2 August 2026. The voluntary Code of Practice (final, published ~10 June 2026) asks generative-AI providers for at least two machine-readable marks (e.g., signed metadata plus imperceptible watermark) and a free detection mechanism. Deployers must label deepfakes visibly.
- **India.** IT Rules amendments (notified 10 February 2026, in force 20 February 2026) require prominent labels plus, "where feasible", permanent metadata or unique identifiers on synthetically generated audio/visual content. They also forbid removing labels or metadata.
- **US.** The TAKE IT DOWN Act's platform duties are enforced from 19 May 2026. NO FAKES is still only proposed.
- **China.** Labeling Measures plus GB 45438-2025 have applied since 1 September 2025, with mandatory implicit (metadata) labels.

### Cited Findings

**EU**
- **Code of Practice.** The final Code on marking and labelling AI-generated content was published 10 June 2026. It is voluntary, but Art. 50 is binding.
  - Section 1 (providers) covers Art. 50(2) marking; Section 2 (deployers) covers Art. 50(4) deepfake labelling.
  - Providers must use at least two machine-readable techniques (e.g., digitally signed, tamper-evident metadata plus imperceptible watermarking) and prohibit users from stripping metadata.
  - Label: the "AI" acronym is mandatory (Measure 1.1); "GENERATED"/"MODIFIED" is encouraged ([Addleshaw Goddard](https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-code-practice-marking-labelling-ai-generated-content/); [artificialintelligenceact.eu](https://artificialintelligenceact.eu/transparency-rules-article-50/); [FELD M](https://www.feld-m.de/en/blog/ai-labeling-code-of-practice-guide/); [EC FAQ on signing](https://digital-strategy.ec.europa.eu/en/faqs/signing-code-practice-transparency-ai-generated-content)). The June 10 date is from secondary sources.
- **Paul Weiss summary (secondary).**
  - Commission Art. 50 Guidelines were published 20 July 2026. These are a separate, non-binding instrument from the Code.
  - Art. 50 applies from 2 August 2026.
  - A single technique suffices for free-form text and for closed physical products; text under ~200 tokens is exempt from watermarking.
  - Providers must offer a detection mechanism, free in principle. Providers with fewer than 1M monthly users may charge for high-volume use. Regulators, law enforcement, media, fact-checkers, researchers and civil society get free access.
  - Forensic detection of stripped content is optional for now.
  - Watermark interoperability is required by 2 February 2027.
  - Deployer labels must be recognisable without interaction and perceivable at first exposure. The Commission finalised three EU icons (fully AI-generated, AI-modified, and basic plus interactive layer).
  - The provider's marking does not discharge the deployer's labelling duty.
  - About 190 signatories by 31 July 2026.
  - Fines up to the greater of €15M or 3% of worldwide turnover.
  - The memo does not name C2PA.
  
  ([Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content))
- **AI Omnibus deferral (status unconfirmed).** Art. 50(2) obligations for systems on the market before 2 August 2026 are deferred to 2 December 2026, and interoperability to 2 February 2027. Paul Weiss states this as fact. Another source calls it a provisional deal from May 2026 that applies "if adopted". I did not confirm its enactment in the Official Journal ([Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content); [getactready](https://getactready.com/blog/eu-ai-act-code-of-practice-marking-ai-content); [Bird & Bird](https://www.twobirds.com/en/insights/2026/taking-the-eu-ai-act-to-practice-the-final-transparency-code-of-practice), paywalled/402 on fetch).
- **Technology readiness.** Paul Weiss notes that the technology for certain aspects of the 50(2)/50(4) obligations "is not yet up to the task" ([Paul Weiss](https://www.paulweiss.com/insights/client-memos/eu-finalises-transparency-rules-for-ai-generated-content)).

**India (enacted)**
- **Notification.** The IT (Intermediary Guidelines and Digital Media Ethics Code) Amendment Rules 2026 were notified 10 February 2026 and are in force from 20 February 2026 ([MediaNama](https://www.medianama.com/2026/02/223-meity-amendments-it-rules-synthetic-media-deepfakes/); [Freshfields](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn)). The number G.S.R. 120(E) comes from a search-result summary only and is unverified. I did not read the Gazette text. A MeitY FAQ PDF exists ([MeitY FAQ, uploaded Oct 2025](https://www.meity.gov.in/static/uploads/2025/10/065b6deb585441b5ccdf8be42502a49c.pdf)), but its upload path suggests it accompanies the October 2025 *draft*, not the final rules.
- **Definition of SGI.** Audio, visual or audio-visual information "artificially or algorithmically created, generated, modified or altered using a computer resource" that appears real or authentic and depicts a person or event as indistinguishable from reality. Text is excluded.
  - Exclusions: good-faith editing (formatting, colour, compression, etc. without materially altering "substance, context or meaning"); documents and educational material; accessibility.
  
  ([Freshfields](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn))
- **Duties on intermediaries offering SGI tools.** This directly covers a reenactment generator offered as a service.
  - "reasonable and appropriate technical measures" to prevent unlawful SGI;
  - "clearly and prominently labelled" (visual label for visual content, audio disclosure for audio);
  - where feasible, embed **permanent metadata or unique identifiers** that can identify the generating computer resource;
  - prevent removal or modification of labels and metadata.
  
  The October 2025 draft's fixed 10%-of-display label size was dropped ([Freshfields](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn); [Hogan Lovells](https://www.hlc.com/en/publications/india-introduces-mandatory-labelling-for-ai-and-3hour-takedown-for-illegal-content); [S.S. Rana](https://ssrana.in/articles/india-tightens-oversight-on-ai-generated-content-under-it-rules/)).
- **Significant social media intermediaries (>5M users).** They must obtain user declarations of SGI, verify them with technical measures (they "cannot rely solely on user representations"), and label SGI.
- **Takedown timelines.**
  - 3 h after a court or government order (was 36 h);
  - 2 h for nudity, NCII, impersonation or morphed images (was 24 h);
  - 36 h for individual complaints (was 72 h);
  - 7 days for general grievances (was 15).
  
  Non-compliance risks loss of safe harbour ([Freshfields](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/india-targets-deepfakes-and-ai-generated-content-key-changes-under-meitys-2026-102mjwn)). Some summaries describe only "3-hour takedown" ([Veritect](https://veritect.ai/digital-data-ai-law/it-rules-synthetic-media-amendment-feb-2026); [iPleaders](https://blog.ipleaders.in/it-rules-2026/)).
- **March–April 2026 draft amendments (PROPOSED, not notified as far as found).** Primary source: a MeitY Notice dated 21 April 2026.
  - MeitY published draft amendments to the IT Rules 2021 on 30 March 2026 "in relation to strengthening intermediary compliance with clarifications, advisories and directions issued by the Ministry ... and digital media oversight". The comment deadline was first extended to 29 April 2026.
  - The Notice adds a further proposed change to **Rule 3(3)(a)(ii)**, which "requires continuous and clearly visible display of label for synthetically generated information throughout the duration of the content in visual display".
  - Comments were due to itrules.consultation@meity.gov.in by **7 May 2026** ([MeitY Notice, 21 Apr 2026](https://www.meity.gov.in/static/uploads/2026/04/ec197f1206279efb4964965f0dede6c1.pdf)).
  - I found no evidence that this draft has been notified as of 2026-10-16.
- **MeitY advisory of 8 October 2026 (MediaNama only).** Reported as an advisory from MeitY's Cyber Laws Division (signed by JS Ajit Kumar) to all social media intermediaries.
  - It asks platforms to "identify and appropriately label/contextualise" manipulated, synthetic *or misleading* content, especially content depicting current events.
  - The labelling clause is not limited to the February SGI definition.
  - It takes effect "with immediate effect", with no stated consequences.
  - It is an advisory, not an amended rule ([MediaNama, Oct 2026](https://www.medianama.com/2026/10/223-meity-labelling-social-media-synthetic-content/)).

**US**
- **TAKE IT DOWN Act (enacted 2025).** FTC enforcement of the platform notice-and-removal duty began 19 May 2026.
  - Valid requests require removal of NCII, including AI deepfakes, plus known identical copies within 48 h.
  - The FTC sent letters to 15 platforms and launched the portal TakeItDown.ftc.gov.
  
  ([FTC press release](https://www.ftc.gov/news-events/news/press-releases/2026/05/ftc-begins-enforcing-take-it-down-act); [FTC business blog](https://www.ftc.gov/business-guidance/blog/2026/05/take-it-down-act-enforcement-starts-now-what-know-about-ftc-tida); [Skadden](https://www.skadden.com/insights/publications/2025/06/take-it-down-act))
- **NO FAKES Act (proposed, not enacted).** Reported reintroduced in both chambers in May 2026, with backing from AFL-CIO, Google/YouTube, IBM, MPA, OpenAI and RIAA. The only source is SAG-AFTRA; committee status is unknown ([SAG-AFTRA](https://www.sagaftra.org/contracts-industry-resources/member-resources/artificial-intelligence)).
- **State laws.** California AB 2602 and New York's digital-replica law (performer contracts) ([MoFo](https://www.mofo.com/resources/insights/250922-digital-avatars-deep-dive-series-navigating)). A tracker exists ([StackCyber](https://stackcyber.com/posts/ai-deepfake-laws)), but I did not review it.

**China (enacted)**
- **The Measures.** The Measures for Labeling AI-Generated Synthetic Content were issued by CAC, MIIT, MPS and NRTA (14 articles, building on the 2023 Deep Synthesis Provisions). They took effect 1 September 2025, together with the mandatory national standard **GB 45438-2025**.
  - **Explicit labels** must be perceivable (e.g., "AI" text, superscript or voice).
  - **Implicit labels** are embedded in file metadata and carry content attributes, the provider name and a content number. Distribution platforms must check for implicit labels and add explicit ones where they are missing.
  - The reported issuance date varies across sources (7, 14 or 17 March 2025).
  
  ([Loeb & Loeb](https://www.loeb.com/en/insights/publications/2025/03/chinas-ai-labeling-measures-and-mandatory-national-standards-take-effect-september-1); [Allen & Gledhill](https://www.allenandgledhill.com/sg/publication/articles/30284/further-regulates-ai-generated-content); [Technology's Legal Edge](https://www.technologyslegaledge.com/2025/03/china-released-new-measures-for-labelling-ai-generated-and-synthetic-content/))

### Inferences
- **Design satisfies multiple regimes.** A visible "AI" label, a signed C2PA manifest (metadata layer) and an invisible watermark carrying a manifest-resolving ID together match:
  - the EU Code's "≥2 machine-readable techniques" plus visible deepfake label;
  - India's "label + permanent metadata/unique identifier, non-removable";
  - China's explicit plus implicit labels (with the content number ≈ manifest ID).
- **India specifics.** For an India-based B.Tech demo, the 2026 IT Rules apply to *intermediaries*, so a research prototype is not itself regulated. A deployed service would be. The watermark ID is a practical way to make the metadata "permanent", since it survives metadata stripping, which plain metadata does not. The 2-hour takedown for impersonation or morphed content makes rapid ID→manifest→consent lookup operationally valuable for platforms.
- **EU detection requirement.** The EU Code's free detection mechanism means a public verifier endpoint (watermark decode → manifest → "AI-generated") is expected. Identity-revealing fields should remain behind access control (Sec. 3).

### Gaps
- EU: final adoption of the AI Omnibus deferrals is unconfirmed. I did not read the Code text on the Commission site (exact measure numbers, whether it references C2PA or ISO/IEC standards).
- India:
  - I did not read the Gazette text of the February 2026 rules, and the G.S.R. number is unverified.
  - Whether the March/April 2026 draft (including the continuous-label proposal in Rule 3(3)(a)(ii)) has been finalised is unknown. I did not search for a later notification.
  - The 8 October 2026 advisory is single-sourced (MediaNama).
- US: I did not survey individual state deepfake laws (election deepfakes, NCII, right of publicity, e.g., Tennessee ELVIS Act) in this session. I found no confirmation of NO FAKES committee action.
- China: I did not read the primary CAC text or GB 45438-2025, including whether it specifies watermark (versus metadata) implicit labels for video and the exact metadata fields.
