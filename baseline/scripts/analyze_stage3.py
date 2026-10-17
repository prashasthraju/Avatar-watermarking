"""Stage 3 analysis: compare fingerprinting scores across landmark conditions on identical pairs."""
import json
import os
import sys

import numpy as np
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(__file__))
import metrics as M

B = "stage3_interaction/evals"
CONDS = ["a_released", "b_reextract", "c_ctrl", "d_wm"]
dfs = {c: M.load_scores(f"{B}/{c}/scores.csv").set_index(["enrol", "test"]) for c in CONDS}
common = set.intersection(*[set(d.index) for d in dfs.values()])
common = sorted(common)
merged = dfs["a_released"].loc[common, ["labels"]].copy()
for c in CONDS:
    merged[c] = dfs[c].loc[common, "scores"].values
merged = merged.reset_index()

res = {"n_pairs_common": len(merged), "per_condition": {}, "deltas": {}}
for c in CONDS:
    res["per_condition"][c] = M.summary(merged["labels"].values, merged[c].values)

comparisons = {
    "watermark effect (d_wm - c_ctrl)": ("d_wm", "c_ctrl"),
    "re-encode effect (c_ctrl - b_reextract)": ("c_ctrl", "b_reextract"),
    "mediapipe drift (b_reextract - a_released)": ("b_reextract", "a_released"),
    "total vs released (d_wm - a_released)": ("d_wm", "a_released"),
}
for name, (x, y) in comparisons.items():
    def stat(df, x=x, y=y):
        return roc_auc_score(df["labels"], df[x]) - roc_auc_score(df["labels"], df[y])

    def stat_eer(df, x=x, y=y):
        return M.eer(df["labels"].values, df[x].values)[0] - M.eer(df["labels"].values, df[y].values)[0]

    bs = M.cluster_bootstrap(merged, stat, n=1000, seed=1)
    bs_e = M.cluster_bootstrap(merged, stat_eer, n=300, seed=2)
    thr = res["per_condition"][y]["EER_threshold"]
    flips = float(((merged[x] > thr) != (merged[y] > thr)).mean())
    res["deltas"][name] = {
        "dAUC": stat(merged), "dAUC_95CI": M.ci(bs),
        "dEER": stat_eer(merged), "dEER_95CI": M.ci(bs_e),
        "score_pearson_r": float(np.corrcoef(merged[x], merged[y])[0, 1]),
        "mean_abs_score_change": float(np.abs(merged[x] - merged[y]).mean()),
        "decision_flip_rate_at_ref_EER_thr": flips,
    }

json.dump(res, open("stage3_interaction/stage3_results.json", "w"), indent=1)
print(json.dumps(res, indent=1))
