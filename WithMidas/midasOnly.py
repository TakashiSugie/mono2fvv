import numpy as np
import argparse
import glob
import os
import vispy
from tqdm import tqdm
import yaml
from utils import get_MiDaS_samples, read_MiDaS_depth
import torch
import imageio
from MiDaS.run import run_depth
from MiDaS.monodepth_net import MonoDepthNet

import MiDaS.MiDaS_utils as MiDaS_utils

parser = argparse.ArgumentParser()
parser.add_argument(
    "--config", type=str, default="argument.yml", help="Configure of post processing"
)
args = parser.parse_args()
config = yaml.load(open(args.config, "r"))
if config["offscreen_rendering"] is True:
    vispy.use(app="egl")
os.makedirs(config["mesh_folder"], exist_ok=True)
os.makedirs(config["video_folder"], exist_ok=True)
os.makedirs(config["depth_folder"], exist_ok=True)
sample_list = get_MiDaS_samples(
    config["src_folder"], config["depth_folder"], config, config["specific"]
)
normal_canvas, all_canvas = None, None

if isinstance(config["gpu_ids"], int) and (config["gpu_ids"] >= 0):
    device = config["gpu_ids"]
else:
    device = "cpu"
print(f"running on device {device}")
# device = "cpu"
# dev = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# "cpu"? "cuda:0"? torch.device('cpu')?
device = torch.device("cpu")
# Model = MonoDepthNet.to(device)
# Model = MonoDepthNet()
# summary(Model, (3, 384, 384))

for idx in tqdm(range(len(sample_list))):
    depth = None
    sample = sample_list[idx]
    print("Current Source ==> ", sample["src_pair_name"])
    mesh_fi = os.path.join(config["mesh_folder"], sample["src_pair_name"] + ".ply")
    image = imageio.imread(sample["ref_img_fi"])

    # print(f"Running depth extraction at {time.time()}")
    if config["require_midas"] is True:
        run_depth(
            [sample["ref_img_fi"]],
            config["src_folder"],
            config["depth_folder"],
            config["MiDaS_model_ckpt"],
            MonoDepthNet,
            MiDaS_utils,
            target_w=640,
        )
