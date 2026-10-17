#!/bin/bash
# Stage 1: AVAPrintDB graph (landmark GCN) baseline, released landmarks.
# Usage: run_stage1.sh <DATASET: CREMA-D|RAVDESS> <TRAIN_GEN: GAGA|LIVE|HUNY> <TEST_GEN>
set -e
ROOT=/home/hp/btp_avatar/AVAPrintDB
OUT=/home/hp/btp_avatar/Watemark/baseline/stage1_biometric/evals
PY=/home/hp/miniconda3/envs/avatar_fingerprinting/bin/python
declare -A GEN=( [GAGA]=gagavatar [LIVE]=liveportrait [HUNY]=hunyuan )
declare -A DS=( [CREMA-D]=cremad [RAVDESS]=ravdess )
D=$1; TR=$2; TE=$3
cd $ROOT/benchmark/code/graph_model
PYTHONPATH=$ROOT/benchmark/code/graph_model PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True $PY /home/hp/btp_avatar/Watemark/baseline/scripts/evaluate_lowmem.py \
  --experiment graph_${D}_train${TR}_test${TE} \
  --dataset $( [ $D = CREMA-D ] && echo CREMAD || echo RAVDESS ) \
  --generators $TE \
  --output-dir-eval $OUT \
  --eval-root-data $ROOT/database/data/landmarks/TEST/$TE \
  --csv-data-file $ROOT/benchmark/eval_files/evaluation_pairs_${D}_${TE}.csv \
  --edges-csv delaunay_edges.csv \
  --checkpoint $ROOT/benchmark/checkpoints/graph-based/checkpoint_graph_trained_${DS[$D]}_${GEN[$TR]}.pt \
  --batch-size 64 --num-frames 70 --window-stride 35 --hidden-dim 64 --embedding-dim 256
