"""Stage 2b (v2): per-segment keyed payloads — dump per-frame bit logits for offline verifier calibration.

Changes vs v1 (stage2b_temporal.py):
  * adds "none + re-encode": the clean video given the same extra CRF23 pass every tampered case gets,
    so false alarms are measured against the same codec history as the tampers;
  * dumps per-frame logits + ground-truth segment labels per case, so verdict rules are fit offline;
  * splits videos into a calibration set (seed 11, 50 videos) and a disjoint test set (v1's seed 7, 100 videos).
Output: stage2_watermark/temporal_v2/<split>/<video>.npz
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import wm_lib as W
from stage2b_temporal import KEY, SEG, SRC, _swap, embed_segments, seg_msg  # noqa: F401

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "stage2_watermark/temporal_v2"


def splits(meta):
    test = sorted(np.random.default_rng(7).choice(len(meta), size=100, replace=False))  # same as v1
    rest = np.setdiff1d(np.arange(len(meta)), test)
    calib = sorted(np.random.default_rng(11).choice(rest, size=50, replace=False))
    return {"calib": calib, "test": test}


def main():
    meta = [json.loads(l) for l in open(BASE / "videos/meta.jsonl")]
    model = W.load_videoseal()
    tmp = BASE / "tmp_attacks"
    tmp.mkdir(exist_ok=True)
    for split, idx in splits(meta).items():
        (OUT / split).mkdir(parents=True, exist_ok=True)
        sel = [meta[i] for i in idx]
        for j, m in enumerate(sel):
            vid = m["name"]
            dst = OUT / split / (vid.replace(".mp4", "") + ".npz")
            if dst.exists():
                continue
            fr, fps = W.read_video(SRC / vid)
            K = (len(fr) + SEG - 1) // SEG
            if K < 3:
                continue
            frw = embed_segments(model, fr, vid)
            path = tmp / "seg.mp4"
            W.write_video(frw, path, fps, crf=23)
            dv, _ = W.read_video(path)
            labels = np.repeat(np.arange(K), SEG)[: len(dv)]
            other = sel[(j + 1) % len(sel)]["name"]
            ofr, _ = W.read_video(SRC / other)
            ofw = embed_segments(model, ofr, other)[:SEG]
            rng = np.random.default_rng(j)
            s1, s2 = sorted(rng.choice(np.arange(1, K), size=2, replace=False))
            segs = [dv[s * SEG:(s + 1) * SEG] for s in range(K)]
            lab = [labels[s * SEG:(s + 1) * SEG] for s in range(K)]
            order = _swap(K, s1, s2)
            perm = rng.permutation(len(dv))
            cases = {
                "none": (dv, labels, False),
                "none_reencode": (dv, labels, True),
                "drop_segment": (np.concatenate(segs[:s1] + segs[s1 + 1:]), np.concatenate(lab[:s1] + lab[s1 + 1:]), True),
                "swap_segments": (np.concatenate([segs[s] for s in order]), np.concatenate([lab[s] for s in order]), True),
                "insert_foreign": (np.concatenate(segs[:s1] + [ofw] + segs[s1:]),
                                   np.concatenate(lab[:s1] + [np.full(len(ofw), -1)] + lab[s1:]), True),
                "shuffle_frames": (dv[perm], labels[perm], True),
            }
            save = {"K": K, "s1": s1, "s2": s2, "other": other}
            for name, (vf, lb, reenc) in cases.items():
                if reenc:
                    vf, _ = W._ffmpeg_roundtrip(vf, fps, crf=23, tmpdir=str(tmp))
                save[f"{name}__logits"] = W.bit_logits(model, vf).numpy().astype(np.float16)
                save[f"{name}__labels"] = lb[: len(vf)]
            np.savez_compressed(dst, **save)
            if j % 10 == 0:
                print(split, j, flush=True)


if __name__ == "__main__":
    main()
