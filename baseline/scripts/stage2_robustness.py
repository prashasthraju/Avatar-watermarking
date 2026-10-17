"""Stage 2: VideoSeal-1.0 robustness on LivePortrait renders.

For N delivered watermarked videos (videos/wm) and their unwatermarked controls (videos/ctrl),
apply each attack, decode 256 bits and compare with the video's own message.
Control decodes give the null distribution (no watermark present) used to set detection thresholds.
Output: stage2_watermark/robustness_raw.csv
"""
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import wm_lib as W

BASE = Path(__file__).resolve().parents[1]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150


def main():
    meta = [json.loads(l) for l in open(BASE / "videos/meta.jsonl")]
    rng0 = np.random.default_rng(123)
    sel = sorted(rng0.choice(len(meta), size=min(N, len(meta)), replace=False))
    tmp = BASE / "tmp_attacks"
    tmp.mkdir(exist_ok=True)
    attacks = W.make_attacks(str(tmp))
    model = W.load_videoseal()
    out = BASE / "stage2_watermark/robustness_raw.csv"
    out.parent.mkdir(exist_ok=True, parents=True)
    t0 = time.time()
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["video", "attack", "condition", "bit_acc", "n_frames_after"])
        for j, i in enumerate(sel):
            m = meta[i]
            msg = np.array([int(c) for c in m["msg"]], dtype=np.float32)
            for cond in ("wm", "ctrl"):
                fr, fps = W.read_video(BASE / "videos" / cond / m["name"])
                for k, (aname, atk) in enumerate(attacks.items()):
                    rng = np.random.default_rng(1000 * int(i) + k)  # same attack randomness for wm and ctrl
                    fa, _ = atk(fr, fps, rng)
                    dec = W.decode(W.bit_logits(model, fa)).numpy()
                    w.writerow([m["name"], aname, cond, float((dec == msg).mean()), len(fa)])
            f.flush()
            if j % 10 == 0:
                print(f"{j}/{len(sel)} {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
