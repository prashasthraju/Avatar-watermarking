"""Offline verifier for Stage 2b v2 dumps.

Verifier (knows key, video_id, expected segment count K):
  1. smooth per-frame bit logits with a centred moving average of w frames;
  2. per frame, agreement with each expected segment message -> best segment + confidence;
  3. frames with confidence >= thr_f are "ours"; their best-segment sequence is collapsed into runs,
     runs shorter than r frames are discarded as noise;
  4. flags: ORDER  - run sequence not strictly increasing;
            MISSING - some expected segment never appears (optionally the trailing partial segment is exempt);
            FOREIGN - a contiguous stretch of >= L low-confidence frames.
Parameters are chosen on the calibration split only (false-alarm budget on the re-encoded clean case),
then frozen and reported on the test split.
Output: stage2_watermark/temporal_v2_summary.csv, stage2_watermark/temporal_v2_results.json
"""
import glob
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from stage2b_temporal import SEG, seg_msg

D = "stage2_watermark/temporal_v2"
CASES = ["none", "none_reencode", "drop_segment", "swap_segments", "insert_foreign", "shuffle_frames"]
FA_BUDGET = float(os.environ.get("FA_BUDGET", "0.02"))


def load(split):
    out = []
    for f in sorted(glob.glob(f"{D}/{split}/*.npz")):
        d = np.load(f)
        vid = os.path.basename(f).replace(".npz", ".mp4")
        K = int(d["K"])
        msgs = np.stack([seg_msg(vid, s) for s in range(K)]).astype(bool)
        last_len = len(d["none__labels"]) - SEG * (K - 1)
        out.append({"vid": vid, "K": K, "msgs": msgs, "last_partial": last_len < SEG,
                    **{c: d[f"{c}__logits"].astype(np.float32) for c in CASES}})
    return out


def smooth(lg, w):
    if w <= 1:
        return lg
    k = np.ones(w) / w
    pad = np.pad(lg, ((w // 2, w - 1 - w // 2), (0, 0)), mode="edge")
    return np.stack([np.convolve(pad[:, i], k, mode="valid") for i in range(lg.shape[1])], 1)


def runs_of(seq):
    r = []
    for x in seq:
        if r and r[-1][0] == x:
            r[-1][1] += 1
        else:
            r.append([x, 1])
    return r


def verify(lg, msgs, K, last_partial, p):
    s = smooth(lg, p["w"])
    ag = ((s > 0)[:, None, :] == msgs[None]).mean(-1)
    best, conf = ag.argmax(1), ag.max(1)
    ours = conf >= p["thr_f"]
    seg_runs = [x for x, n in runs_of(best[ours]) if n >= p["r"]]
    order_bad = any(b <= a for a, b in zip(seg_runs, seg_runs[1:]))
    need = set(range(K - 1)) if (p["exempt_last"] and last_partial) else set(range(K))
    missing = not need.issubset(seg_runs)
    low = [n for x, n in runs_of(list(~ours)) if x]
    foreign = max(low, default=0) >= p["L"]
    return {"ORDER": order_bad, "MISSING": missing, "FOREIGN": foreign}


def evaluate(data, p):
    rows = []
    for v in data:
        for c in CASES:
            f = verify(v[c], v["msgs"], v["K"], v["last_partial"], p)
            rows.append({"video": v["vid"], "case": c, **f, "flagged": any(f.values())})
    return pd.DataFrame(rows)


GRID = [dict(w=w, thr_f=t, r=r, L=L, exempt_last=e)
        for w, t, r, L, e in itertools.product([1, 4, 8], [0.58, 0.60, 0.62, 0.64], [2, 4], [6, 8, 12], [False, True])]


def main():
    cal, test = load("calib"), load("test")
    print(f"calib videos {len(cal)}, test videos {len(test)}, FA budget {FA_BUDGET}")
    # rule: meet the budget on BOTH clean cases if possible; otherwise minimise the re-encoded-clean false alarm
    # (subject to the once-encoded clean case staying within budget), then maximise mean tamper detection.
    best = None
    for p in GRID:
        df = evaluate(cal, p)
        rate = df.groupby("case")["flagged"].mean()
        det = rate[["drop_segment", "swap_segments", "insert_foreign", "shuffle_frames"]].mean()
        key = (rate["none_reencode"] <= FA_BUDGET and rate["none"] <= FA_BUDGET, rate["none"] <= FA_BUDGET,
               -rate["none_reencode"], det, not p["exempt_last"])
        if best is None or key > best[0]:
            best = (key, p, rate)
    if not best[0][0]:
        print(f"NOTE: no setting meets the {FA_BUDGET} budget on re-encoded clean videos; using the minimum-false-alarm setting")
    _, p, cal_rate = best
    print("chosen params (calibration):", p)
    print("calibration flag rates:\n", cal_rate.round(3).to_string())
    df = evaluate(test, p)
    summ = df.groupby("case", sort=False)[["flagged", "ORDER", "MISSING", "FOREIGN"]].mean().reindex(CASES)
    summ.insert(0, "n", df.groupby("case").size().reindex(CASES))
    print("\nTEST:\n", summ.round(3).to_string())
    summ.reset_index().to_csv("stage2_watermark/temporal_v2_summary.csv", index=False)
    json.dump({"params": p, "budget_met_on_calib": bool(best[0][0]), "fa_budget_calib": FA_BUDGET, "n_calib": len(cal), "n_test": len(test),
               "calib_flag_rates": cal_rate.to_dict(), "test": summ.reset_index().to_dict(orient="records"),
               "last_segment_partial_frac_test": float(np.mean([v["last_partial"] for v in test]))},
              open("stage2_watermark/temporal_v2_results.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
