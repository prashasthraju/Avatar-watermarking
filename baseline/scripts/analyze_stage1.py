"""Summarise Stage 1 score files: AUC (+cluster-bootstrap CI), EER, TAR@FAR."""
import glob, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import metrics as M
from sklearn.metrics import roc_auc_score

PAPER = {  # AVAPrintDB paper, Graph system, AUC %  (in-domain and LIVE-trained cross-generator = in-domain + delta)
    "graph_CREMA-D_trainLIVE_testLIVE": 90.8, "graph_RAVDESS_trainLIVE_testLIVE": 76.5,
    "graph_CREMA-D_trainLIVE_testGAGA": 90.8 - 14.3, "graph_CREMA-D_trainLIVE_testHUNY": 90.8 - 16.9,
}
res = {}
for d in sorted(glob.glob("stage1_biometric/evals/*/scores.csv")):
    name = d.split("/")[-2]
    df = M.load_scores(d)
    y, s = df["labels"].values, df["scores"].values
    r = M.summary(y, s)
    bs = M.cluster_bootstrap(df, lambda x: roc_auc_score(x["labels"], x["scores"]), n=300)
    r["AUC_95CI"] = M.ci(bs)
    r["paper_AUC_%"] = PAPER.get(name)
    res[name] = r
    print(name, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
json.dump(res, open("stage1_biometric/stage1_results.json", "w"), indent=1)
