"""Verification metrics for score CSVs written by AVAPrintDB evaluate.py (columns: labels, scores, enrol_path, test_path)."""
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, roc_curve


def eer(y, s):
    fpr, tpr, thr = roc_curve(y, s)
    fnr = 1 - tpr
    i = np.nanargmin(np.abs(fnr - fpr))
    return float((fpr[i] + fnr[i]) / 2), float(thr[i])


def tar_at_far(y, s, far):
    """TAR at the largest threshold whose impostor accept rate is <= far."""
    imp = np.sort(s[y == 0])[::-1]
    k = int(np.floor(far * len(imp)))
    thr = imp[k] if k < len(imp) else -np.inf
    return float((s[y == 1] > thr).mean())


def summary(y, s):
    e, t = eer(y, s)
    return {
        "n_pairs": int(len(y)), "n_genuine": int(y.sum()), "n_impostor": int((1 - y).sum()),
        "AUC": float(roc_auc_score(y, s)), "EER": e, "EER_threshold": t,
        "TAR@FAR=1e-1": tar_at_far(y, s, 1e-1), "TAR@FAR=1e-2": tar_at_far(y, s, 1e-2),
        "TAR@FAR=1e-3": tar_at_far(y, s, 1e-3),
    }


def load_scores(path):
    df = pd.read_csv(path)
    df["test"] = df["test_path"].astype(str).str.split("/").str[-1].str.replace(".npy", "", regex=False)
    df["enrol"] = df["enrol_path"].astype(str).str.split("/").str[-1].str.replace(".npy", "", regex=False)
    return df


def cluster_bootstrap(df, stat_fn, n=1000, seed=0, cluster="test"):
    """Resample test videos (clusters) with replacement; every pair involving a drawn test video is kept.
    Pairs sharing a test video are correlated, so a pair-level bootstrap would understate uncertainty."""
    rng = np.random.default_rng(seed)
    groups = df.groupby(cluster).indices
    keys = np.array(list(groups.keys()))
    out = []
    for _ in range(n):
        draw = rng.choice(len(keys), size=len(keys), replace=True)
        idx = np.concatenate([groups[keys[d]] for d in draw])
        out.append(stat_fn(df.iloc[idx]))
    return np.array(out)


def ci(arr, alpha=0.05):
    return float(np.percentile(arr, 100 * alpha / 2)), float(np.percentile(arr, 100 * (1 - alpha / 2)))
