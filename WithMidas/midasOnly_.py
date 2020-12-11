import numpy as np
import argparse
import glob
import os
from functools import partial
import vispy
import scipy.misc as misc
from tqdm import tqdm
import yaml
import time
import sys
from mesh import write_ply, read_ply, output_3d_photo
from utils import get_MiDaS_samples, read_MiDaS_depth
import torch
import cv2
from skimage.transform import resize
import imageio
import copy
from networks import Inpaint_Color_Net, Inpaint_Depth_Net, Inpaint_Edge_Net
from MiDaS.run import run_depth
from MiDaS.monodepth_net import MonoDepthNet
import MiDaS.MiDaS_utils as MiDaS_utils
from libsLink.variable import (
    imgName1,
    imgName2,
    basePath,
    LFName,
    imgPath1,
    imgPath2,
    require_midas,
    longerSideLen,
)

# npy形式でDepthもどきを出力する、形状は画像のサイズと同じ浮動小数の配列
# しかし、負の数も出てくるので厳密にはDepthではない
# 系は崩れていないと考えて、そのまま使用する
# print(basePath)

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
src_folder = os.path.join(basePath, LFName)
sample_list = get_MiDaS_samples(
    # config["src_folder"], config["depth_folder"], config, config["specific"]
    src_folder,
    config["depth_folder"],
    config,
    config["specific"],
    inputImgNames=[imgName1, imgName2],
)
normal_canvas, all_canvas = None, None

if isinstance(config["gpu_ids"], int) and (config["gpu_ids"] >= 0):
    device = config["gpu_ids"]
else:
    device = "cpu"
# print(f"running on device {device}")
device = torch.device("cpu")
for idx in tqdm(range(len(sample_list))):
    depth = None
    sample = sample_list[idx]
    # print("Current Source ==> ", sample["src_pair_name"])
    mesh_fi = os.path.join(config["mesh_folder"], sample["src_pair_name"] + ".ply")
    image = imageio.imread(sample["ref_img_fi"])
    if require_midas:
        # print(f"Running depth extraction at {time.time()}")
        ref_img_fi = [imgPath1, imgPath2]
        run_depth(
            # [sample["ref_img_fi"]],
            ref_img_fi,
            config["src_folder"],
            config["depth_folder"],
            config["MiDaS_model_ckpt"],
            MonoDepthNet,
            MiDaS_utils,
            target_w=512,
            longerSideLen=longerSideLen,
        )
