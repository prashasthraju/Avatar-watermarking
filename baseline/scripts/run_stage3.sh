#!/bin/bash
# Stage 3: does VideoSeal watermarking change avatar-fingerprinting scores?
# Conditions on the same 3-target subset and identical pairs:
#   a_released : landmarks shipped with AVAPrintDB
#   b_reextract: our re-extraction from the original mp4s (measures mediapipe-version drift)
#   c_ctrl     : re-extraction after decode -> H.264 CRF23 re-encode, no watermark
#   d_wm       : re-extraction after VideoSeal embed -> same H.264 CRF23 encode
# Watermark effect = d vs c.
set -e
B=/home/hp/btp_avatar/Watemark/baseline
ROOT=/home/hp/btp_avatar/AVAPrintDB
PY=/home/hp/miniconda3/envs/avatar_fingerprinting/bin/python
LM=$ROOT/database/preprocessing/landmarks_extraction
for c in orig_links:b_reextract ctrl:c_ctrl wm:d_wm; do
  src=${c%%:*}; dst=${c##*:}
  $PY $LM/landmark_extraction.py --input_folder $B/videos/$src --output_folder $B/stage3_interaction/landmarks/$dst \
      --max_workers 16 --model_path $LM/face_landmarker.task --database CREMAD 2>&1 | grep -E "Processing videos: 100|error" || true
done
mkdir -p $B/stage3_interaction/landmarks/a_released
for f in $(python3 -c "import json;print(' '.join(v[:-4] for v in json.load(open('$B/subset/subset.json'))['videos']))"); do
  ln -sf $ROOT/database/data/landmarks/TEST/LIVE/$f.npy $B/stage3_interaction/landmarks/a_released/$f.npy
done
cd $ROOT/benchmark/code/graph_model
for cond in a_released b_reextract c_ctrl d_wm; do
  PYTHONPATH=$ROOT/benchmark/code/graph_model PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  $PY $B/scripts/evaluate_lowmem.py --experiment $cond --dataset CREMAD --generators LIVE \
    --output-dir-eval $B/stage3_interaction/evals \
    --eval-root-data $B/stage3_interaction/landmarks/$cond \
    --csv-data-file $B/subset/pairs_subset.csv --edges-csv delaunay_edges.csv \
    --checkpoint $ROOT/benchmark/checkpoints/graph-based/checkpoint_graph_trained_cremad_liveportrait.pt \
    --batch-size 64 --num-frames 70 --window-stride 35 --hidden-dim 64 --embedding-dim 256 2>&1 | tail -1 | cut -c1-120
done
