"""Shared helpers for the VideoSeal baseline: video I/O via ffmpeg, embedding, extraction, attacks."""
import json
import subprocess
from pathlib import Path

import numpy as np
import torch

VS_CARD = Path(__file__).resolve().parents[1] / ".venv_vs/lib/python3.12/site-packages/videoseal/cards/videoseal_1.0.yaml"


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height,r_frame_rate", "-of", "json", str(path)],
        capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), float(num) / float(den)


def read_video(path):
    """Return uint8 array (F, H, W, 3) RGB and fps."""
    w, h, fps = probe(path)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
    return frames, fps


def write_video(frames, path, fps, crf=23, preset="medium"):
    """Encode uint8 (F, H, W, 3) RGB frames to H.264 yuv420p mp4."""
    f, h, w, _ = frames.shape
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", f"{fps}", "-i", "-",
           "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", str(path)]
    subprocess.run(cmd, input=np.ascontiguousarray(frames).tobytes(), check=True)


def to_tensor(frames):
    return torch.from_numpy(frames).permute(0, 3, 1, 2).float().div(255.0)


def to_uint8(t):
    return (t.clamp(0, 1) * 255.0).round().byte().permute(0, 2, 3, 1).cpu().numpy()


def load_videoseal(device="cuda"):
    import videoseal
    model = videoseal.load(VS_CARD)
    model.eval().to(device)
    return model


def random_msg(nbits, rng):
    return torch.from_numpy(rng.integers(0, 2, size=(1, nbits))).float()


@torch.no_grad()
def embed(model, frames_u8, msg, device="cuda"):
    """frames_u8: (F,H,W,3) uint8. Returns watermarked uint8 frames (before any encode)."""
    x = to_tensor(frames_u8)
    out = model.embed(x, msgs=msg.to(device), is_video=True)
    return to_uint8(out["imgs_w"])


@torch.no_grad()
def bit_logits(model, frames_u8, device="cuda"):
    """Per-frame soft bit predictions (F, K); >0 means bit 1."""
    x = to_tensor(frames_u8).to(device)
    preds = model.detect(x, is_video=True)["preds"]
    return preds[:, 1:].float().cpu()


def decode(logits):
    """Average logits across frames (VideoSeal 'avg' aggregation) and threshold."""
    return (logits.mean(0) > 0).float()


def bit_acc(decoded, msg):
    return float((decoded == msg.view(-1).cpu()).float().mean())


# ---------------------------------------------------------------- attacks
# Each attack maps (frames_u8, fps, rng) -> (frames_u8, fps). Codec attacks round-trip through ffmpeg.

def _ffmpeg_roundtrip(frames, fps, vf=None, crf=23, out_fps=None, tmpdir="/tmp"):
    import tempfile
    with tempfile.TemporaryDirectory(dir=tmpdir) as d:
        src = Path(d) / "in.mp4"
        dst = Path(d) / "out.mp4"
        write_video(frames, src, fps, crf=0, preset="ultrafast")  # lossless intermediate
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(src)]
        if vf:
            cmd += ["-vf", vf]
        if out_fps:
            cmd += ["-r", str(out_fps)]
        cmd += ["-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p", str(dst)]
        subprocess.run(cmd, check=True)
        return read_video(dst)


def make_attacks(tmpdir):
    def h264(crf):
        return lambda fr, fps, rng: _ffmpeg_roundtrip(fr, fps, crf=crf, tmpdir=tmpdir)

    def h265(crf):
        def f(fr, fps, rng):
            import tempfile
            with tempfile.TemporaryDirectory(dir=tmpdir) as d:
                src, dst = Path(d) / "in.mp4", Path(d) / "out.mp4"
                write_video(fr, src, fps, crf=0, preset="ultrafast")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libx265",
                                "-x265-params", "log-level=error", "-crf", str(crf),
                                "-pix_fmt", "yuv420p", str(dst)], check=True)
                return read_video(dst)
        return f

    def resize(scale):
        return lambda fr, fps, rng: _ffmpeg_roundtrip(
            fr, fps, vf=f"scale=trunc(iw*{scale}/2)*2:trunc(ih*{scale}/2)*2", tmpdir=tmpdir)

    def crop(frac):
        return lambda fr, fps, rng: _ffmpeg_roundtrip(
            fr, fps, vf=f"crop=trunc(iw*{frac}/2)*2:trunc(ih*{frac}/2)*2", tmpdir=tmpdir)

    def noise(sigma):
        def f(fr, fps, rng):
            n = rng.normal(0, sigma * 255.0, size=fr.shape)
            return _ffmpeg_roundtrip(np.clip(fr + n, 0, 255).astype(np.uint8), fps, tmpdir=tmpdir)
        return f

    def brightness(delta):
        def f(fr, fps, rng):
            return _ffmpeg_roundtrip(np.clip(fr.astype(np.int16) + int(delta * 255), 0, 255).astype(np.uint8),
                                     fps, tmpdir=tmpdir)
        return f

    def frame_drop(p):
        def f(fr, fps, rng):
            keep = rng.random(len(fr)) > p
            keep[0] = True
            return _ffmpeg_roundtrip(fr[keep], fps, tmpdir=tmpdir)
        return f

    def shuffle(fr, fps, rng):
        return _ffmpeg_roundtrip(fr[rng.permutation(len(fr))], fps, tmpdir=tmpdir)

    def temporal_crop(fr, fps, rng):
        return _ffmpeg_roundtrip(fr[: max(8, len(fr) // 4)], fps, tmpdir=tmpdir)

    def fps_change(out_fps):
        return lambda fr, fps, rng: _ffmpeg_roundtrip(fr, fps, out_fps=out_fps, tmpdir=tmpdir)

    def combined(fr, fps, rng):
        fr = np.clip(fr.astype(np.int16) + int(0.1 * 255), 0, 255).astype(np.uint8)
        return _ffmpeg_roundtrip(fr, fps, vf="crop=trunc(iw*0.8/2)*2:trunc(ih*0.8/2)*2", crf=30, tmpdir=tmpdir)

    return {
        "none (delivered CRF23)": lambda fr, fps, rng: (fr, fps),
        "H.264 CRF30": h264(30),
        "H.264 CRF40": h264(40),
        "H.265 CRF28": h265(28),
        "resize 0.5x": resize(0.5),
        "center crop 80%": crop(0.8),
        "gaussian noise s=0.05": noise(0.05),
        "gaussian noise s=0.15": noise(0.15),
        "brightness +0.2": brightness(0.2),
        "drop 50% frames": frame_drop(0.5),
        "shuffle frames": shuffle,
        "keep first 25% frames": temporal_crop,
        "fps 29->15": fps_change(15),
        "crop80+bright+CRF30": combined,
    }
