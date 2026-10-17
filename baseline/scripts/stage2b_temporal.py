"""Stage 2b: per-segment keyed payloads on top of VideoSeal for temporal-integrity checking.

Untested configuration flagged in the research report: instead of one message for the whole video,
segment s (SEG frames) carries m_s = HMAC-SHA256(key, video_id || s)  (exactly 256 bits).
The verifier knows key + video_id (from the manifest) and the expected number of segments K.
Each received frame is assigned to the segment whose message best matches its per-frame bit logits;
the decoded segment sequence is then checked for completeness and order.

Tamper operations on the delivered video:
  none, drop one whole segment, swap two segments, insert a foreign segment (from another video), shuffle frames.
Output: stage2_watermark/temporal_raw.csv
"""
import csv
import hashlib
import hmac
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
import wm_lib as W

BASE = Path(__file__).resolve().parents[1]
SRC = Path("/home/hp/btp_avatar/AVAPrintDB/database/data/videos/TEST/LIVE")
KEY = b"btp-demo-key-not-secret"
SEG = 16  # frames per segment (~0.55 s at 29 fps); multiple of VideoSeal step_size=4
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100


def seg_msg(video_id, s):
    d = hmac.new(KEY, f"{video_id}|{s}".encode(), hashlib.sha256).digest()
    bits = np.unpackbits(np.frombuffer(d, np.uint8)).astype(np.float32)
    return bits  # 256


def embed_segments(model, fr, video_id):
    out = []
    for s, start in enumerate(range(0, len(fr), SEG)):
        msg = torch.from_numpy(seg_msg(video_id, s)).view(1, -1)
        out.append(W.embed(model, fr[start:start + SEG], msg))
    return np.concatenate(out, 0)


def assign(logits, msgs):
    """logits (F,256); msgs (K,256) in {0,1}. Return per-frame best segment, its agreement, and segment-level calls."""
    signs = (logits.numpy() > 0).astype(np.float32)
    agree = (signs[:, None, :] == msgs[None]).mean(-1)  # F,K
    return agree.argmax(1), agree.max(1)


def runs(seq):
    """Collapse a per-frame segment sequence into runs, smoothing isolated mis-assignments with a median filter."""
    from scipy.ndimage import median_filter
    sm = median_filter(seq, size=5, mode="nearest")
    r = [sm[0]]
    for x in sm[1:]:
        if x != r[-1]:
            r.append(x)
    return r, sm


def verdict(run_list, K, frame_conf, thr):
    """Tamper flags: missing segment, out-of-order, or low-confidence (foreign) frames."""
    ok_order = all(b > a for a, b in zip(run_list, run_list[1:]))
    complete = sorted(set(run_list)) == list(range(K))
    foreign = int((frame_conf < thr).sum())
    tampered = (not ok_order) or (not complete) or foreign >= 4
    return tampered, ok_order, complete, foreign


def main():
    meta = [json.loads(l) for l in open(BASE / "videos/meta.jsonl")]
    rng0 = np.random.default_rng(7)
    sel = [meta[i] for i in sorted(rng0.choice(len(meta), size=min(N, len(meta)), replace=False))]
    model = W.load_videoseal()
    tmp = BASE / "tmp_attacks"
    tmp.mkdir(exist_ok=True)
    # per-frame agreement threshold for "this frame carries one of our segment messages":
    # binomial(256, 0.5) has sd 8 bits -> 0.5 + 4.5*sd/256 ~= 0.64 gives ~3e-6 per-frame false match per candidate.
    THR = 0.64
    out = BASE / "stage2_watermark/temporal_raw.csv"
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["video", "tamper", "tampered_truth", "flagged", "order_ok", "complete", "foreign_frames",
                    "frame_assign_acc", "mean_conf_true_frames"])
        for j, m in enumerate(sel):
            vid = m["name"]
            fr, fps = W.read_video(SRC / vid)
            K = (len(fr) + SEG - 1) // SEG
            if K < 3:
                continue
            frw = embed_segments(model, fr, vid)
            path = tmp / "seg.mp4"
            W.write_video(frw, path, fps, crf=23)
            dv, _ = W.read_video(path)
            labels = np.repeat(np.arange(K), SEG)[: len(dv)]
            msgs = np.stack([seg_msg(vid, s) for s in range(K)])
            other = sel[(j + 1) % len(sel)]["name"]
            ofr, _ = W.read_video(SRC / other)
            ofw = embed_segments(model, ofr, other)[:SEG]  # a validly watermarked segment from another video
            rng = np.random.default_rng(j)
            s1, s2 = sorted(rng.choice(np.arange(1, K), size=2, replace=False)) if K > 2 else (1, 1)
            segs = [dv[s * SEG:(s + 1) * SEG] for s in range(K)]
            lab_segs = [labels[s * SEG:(s + 1) * SEG] for s in range(K)]
            cases = {
                "none": (dv, labels, False),
                "drop one segment": (np.concatenate(segs[:s1] + segs[s1 + 1:]),
                                     np.concatenate(lab_segs[:s1] + lab_segs[s1 + 1:]), True),
                "swap two segments": (np.concatenate([segs[s] for s in _swap(K, s1, s2)]),
                                      np.concatenate([lab_segs[s] for s in _swap(K, s1, s2)]), True),
                "insert foreign segment": (np.concatenate(segs[:s1] + [ofw] + segs[s1:]),
                                           np.concatenate(lab_segs[:s1] + [np.full(len(ofw), -1)] + lab_segs[s1:]), True),
                "shuffle frames": None,
            }
            perm = rng.permutation(len(dv))
            cases["shuffle frames"] = (dv[perm], labels[perm], True)
            for name, (vf, lab, truth) in cases.items():
                # every tampered video is re-encoded once more (as an attacker would have to)
                if name != "none":
                    vf, _ = W._ffmpeg_roundtrip(vf, fps, crf=23, tmpdir=str(tmp))
                lg = W.bit_logits(model, vf)
                best, conf = assign(lg, msgs)
                rl, sm = runs(best[conf >= THR] if (conf >= THR).any() else best)
                flagged, order_ok, complete, foreign = verdict(rl, K, conf, THR)
                true_mask = lab >= 0
                acc = float((best[true_mask] == lab[true_mask]).mean()) if true_mask.any() else float("nan")
                w.writerow([vid, name, truth, flagged, order_ok, complete, foreign, acc,
                            float(conf[true_mask].mean()) if true_mask.any() else float("nan")])
            f.flush()
            if j % 10 == 0:
                print(j, flush=True)


def _swap(K, a, b):
    order = list(range(K))
    order[a], order[b] = order[b], order[a]
    return order


if __name__ == "__main__":
    main()
