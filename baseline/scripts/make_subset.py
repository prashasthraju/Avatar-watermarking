"""Pick a reproducible subset of CREMA-D LivePortrait TEST target identities for stages 2-3."""
import csv, json, os, random, sys
ROOT = "/home/hp/btp_avatar/AVAPrintDB"
N_TARGETS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
vids = set(os.listdir(f"{ROOT}/database/data/videos/TEST/LIVE"))
lms = set(f[:-4] + ".mp4" for f in os.listdir(f"{ROOT}/database/data/landmarks/TEST/LIVE"))
rows = list(csv.DictReader(open(f"{ROOT}/benchmark/eval_files/evaluation_pairs_CREMA-D_LIVE.csv")))
targets = sorted({r["enrolment_sample"].split("--")[0] for r in rows})
random.Random(0).shuffle(targets)
chosen = sorted(targets[:N_TARGETS])
sub = [r for r in rows if r["enrolment_sample"].split("--")[0] in chosen]
files = sorted({r["enrolment_sample"] for r in sub} | {r["test_sample"] for r in sub})
missing = [f for f in files if f not in vids or f not in lms]
assert not missing, f"missing {len(missing)} files"
os.makedirs("subset", exist_ok=True)
with open("subset/pairs_subset.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["enrolment_sample", "test_sample", "label"]); w.writeheader(); w.writerows(sub)
json.dump({"targets": chosen, "videos": files, "n_pairs": len(sub),
           "n_genuine": sum(r["label"] == "1" for r in sub), "n_impostor": sum(r["label"] == "0" for r in sub)},
          open("subset/subset.json", "w"), indent=1)
print(chosen, len(files), "videos", len(sub), "pairs")
