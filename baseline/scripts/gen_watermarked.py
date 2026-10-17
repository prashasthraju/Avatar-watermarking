"""Stage 2/3 data generation.

For every subset video writes:
  videos/ctrl/<name>.mp4  original frames re-encoded with the delivery codec (H.264 CRF23), no watermark
  videos/wm/<name>.mp4    VideoSeal-1.0 (256-bit) watermarked frames, same codec settings
and records per-video message + imperceptibility metrics in videos/meta.jsonl.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from skimage.metrics import structural_similarity

sys.path.insert(0, str(Path(__file__).parent))
import wm_lib as W

BASE = Path(__file__).resolve().parents[1]
SRC = Path("/home/hp/btp_avatar/AVAPrintDB/database/data/videos/TEST/LIVE")
OUT = BASE / "videos"
CRF = 23


def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return float(10 * np.log10(255.0 ** 2 / max(mse, 1e-12)))


def ssim(a, b, step=4):
    return float(np.mean([structural_similarity(a[i], b[i], channel_axis=2, data_range=255)
                          for i in range(0, len(a), step)]))


def main():
    import lpips
    lp = lpips.LPIPS(net="alex", verbose=False).cuda()

    def lpips_score(a, b, step=8):
        ta = W.to_tensor(a[::step]).cuda() * 2 - 1
        tb = W.to_tensor(b[::step]).cuda() * 2 - 1
        with torch.no_grad():
            return float(lp(ta, tb).mean())

    videos = json.load(open(BASE / "subset/subset.json"))["videos"]
    (OUT / "wm").mkdir(parents=True, exist_ok=True)
    (OUT / "ctrl").mkdir(parents=True, exist_ok=True)
    meta_path = OUT / "meta.jsonl"
    done = set()
    if meta_path.exists():
        done = {json.loads(l)["name"] for l in open(meta_path)}
    model = W.load_videoseal()
    t0 = time.time()
    with open(meta_path, "a") as meta:
        for i, name in enumerate(videos):
            if name in done:
                continue
            seed = int.from_bytes(name.encode(), "little") % (2 ** 32)
            msg = W.random_msg(256, np.random.default_rng(seed))
            fr, fps = W.read_video(SRC / name)
            frw = W.embed(model, fr, msg)
            W.write_video(frw, OUT / "wm" / name, fps, crf=CRF)
            W.write_video(fr, OUT / "ctrl" / name, fps, crf=CRF)
            wm_dec, _ = W.read_video(OUT / "wm" / name)
            ctrl_dec, _ = W.read_video(OUT / "ctrl" / name)
            rec = {
                "name": name, "fps": fps, "frames": len(fr),
                "msg": "".join(str(int(b)) for b in msg.view(-1).tolist()),
                # imperceptibility of the watermark itself (pre-codec) and as delivered (post-codec)
                "psnr_wm_raw": psnr(fr, frw), "ssim_wm_raw": ssim(fr, frw),
                "psnr_wm_vs_ctrl": psnr(ctrl_dec, wm_dec), "ssim_wm_vs_ctrl": ssim(ctrl_dec, wm_dec),
                "lpips_wm_vs_ctrl": lpips_score(ctrl_dec, wm_dec),
                "psnr_ctrl_vs_orig": psnr(fr, ctrl_dec), "psnr_wm_vs_orig": psnr(fr, wm_dec),
            }
            meta.write(json.dumps(rec) + "\n")
            meta.flush()
            if i % 25 == 0:
                print(f"{i}/{len(videos)} {time.time() - t0:.0f}s psnr_raw={rec['psnr_wm_raw']:.1f}", flush=True)


if __name__ == "__main__":
    main()
