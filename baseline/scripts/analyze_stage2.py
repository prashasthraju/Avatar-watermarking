"""Stage 2 analysis: bit accuracy, null distribution, detection TPR at fixed FPR, exact-payload recovery, temporal checks."""
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import binom

NB = 256
res = {}

# ---------------- robustness ----------------
df = pd.read_csv("stage2_watermark/robustness_raw.csv")
df["k"] = (df["bit_acc"] * NB).round().astype(int)
k_bin = {fpr: int(binom.isf(fpr, NB, 0.5)) + 1 for fpr in (1e-3, 1e-6, 1e-9)}  # P(X >= k) <= fpr under H0
null_all = df[df.condition == "ctrl"]["k"]
k_emp = int(null_all.max()) + 1  # zero empirical false positives across every null decode
res["thresholds_bits_of_256"] = {"binomial_FPR1e-3": k_bin[1e-3], "binomial_FPR1e-6": k_bin[1e-6],
                                 "binomial_FPR1e-9": k_bin[1e-9], "empirical_max_null_plus1": k_emp,
                                 "n_null_decodes": int(len(null_all))}
rows = []
for atk, g in df.groupby("attack", sort=False):
    wm, ct = g[g.condition == "wm"], g[g.condition == "ctrl"]
    rows.append({
        "attack": atk, "n_videos": len(wm),
        "bit_acc_mean": wm.bit_acc.mean(), "bit_acc_p10": wm.bit_acc.quantile(0.1), "bit_acc_min": wm.bit_acc.min(),
        "null_bit_acc_mean": ct.bit_acc.mean(), "null_bit_acc_max": ct.bit_acc.max(),
        "TPR@FPR1e-6": (wm.k >= k_bin[1e-6]).mean(), "TPR@FPR1e-9": (wm.k >= k_bin[1e-9]).mean(),
        "FPR_obs@1e-6thr": (ct.k >= k_bin[1e-6]).mean(),
        "exact_256bit_recovery": (wm.k == NB).mean(),
        "frames_after_mean": wm.n_frames_after.mean(),
    })
rob = pd.DataFrame(rows)
rob.to_csv("stage2_watermark/robustness_summary.csv", index=False)
res["robustness"] = rob.to_dict(orient="records")
print(rob.round(4).to_string(index=False))
print(res["thresholds_bits_of_256"])

# ---------------- imperceptibility ----------------
meta = pd.DataFrame([json.loads(l) for l in open("videos/meta.jsonl")])
q = {c: {"mean": float(meta[c].mean()), "std": float(meta[c].std()), "min": float(meta[c].min())}
     for c in ["psnr_wm_raw", "ssim_wm_raw", "psnr_wm_vs_ctrl", "ssim_wm_vs_ctrl", "lpips_wm_vs_ctrl",
               "psnr_ctrl_vs_orig", "psnr_wm_vs_orig"]}
q["n_videos"] = len(meta)
res["imperceptibility"] = q
print(json.dumps(q, indent=1))

# ---------------- temporal (per-segment keyed payloads) ----------------
if os.path.exists("stage2_watermark/temporal_raw.csv"):
    t = pd.read_csv("stage2_watermark/temporal_raw.csv")
    tt = t.groupby("tamper", sort=False).agg(
        n=("video", "count"), flagged_rate=("flagged", "mean"), order_ok_rate=("order_ok", "mean"),
        complete_rate=("complete", "mean"), mean_foreign_frames=("foreign_frames", "mean"),
        frame_assign_acc=("frame_assign_acc", "mean"), mean_conf=("mean_conf_true_frames", "mean")).reset_index()
    tt.to_csv("stage2_watermark/temporal_summary.csv", index=False)
    res["temporal"] = tt.to_dict(orient="records")
    print(tt.round(4).to_string(index=False))

json.dump(res, open("stage2_watermark/stage2_results.json", "w"), indent=1, default=float)
