import sys, time, numpy as np, torch
sys.path.insert(0, "scripts")
import wm_lib as W
v = "/home/hp/btp_avatar/AVAPrintDB/database/data/videos/TEST/LIVE/C1003--C1003--00826d2d-c9a6-58bf-96d7-fe6df0b39743--LIVE.mp4"
t=time.time(); m = W.load_videoseal(); print("load", time.time()-t, "nbits", m.embedder.msg_processor.nbits if hasattr(m.embedder,'msg_processor') else '?')
fr, fps = W.read_video(v); print(fr.shape, fps)
rng = np.random.default_rng(0); msg = W.random_msg(256, rng)
t=time.time(); frw = W.embed(m, fr, msg); torch.cuda.synchronize(); print("embed s", time.time()-t)
print("raw acc", W.bit_acc(W.decode(W.bit_logits(m, frw)), msg))
W.write_video(frw, "/tmp/claude-1001/-home-hp-btp-avatar-Watemark/df87b481-7192-4af4-b09d-8314ff88322a/scratchpad/w.mp4", fps)
frw2,_ = W.read_video("/tmp/claude-1001/-home-hp-btp-avatar-Watemark/df87b481-7192-4af4-b09d-8314ff88322a/scratchpad/w.mp4")
print("crf23 acc", W.bit_acc(W.decode(W.bit_logits(m, frw2)), msg))
print("orig acc (null)", W.bit_acc(W.decode(W.bit_logits(m, fr)), msg))
d = fr.astype(float)-frw2.astype(float); print("psnr", 10*np.log10(255**2/np.mean(d**2)))
print("mem GB", torch.cuda.max_memory_allocated()/1e9)
