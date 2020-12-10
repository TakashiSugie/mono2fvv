import numpy as np
import cv2
import os
import scipy.io as sio
import re
from libs.variable import paraDict, LFName


def readCg(cgPath):
    patternList = ["focal_length_mm", "sensor_size_mm", "baseline_mm"]
    paraDict = {}
    with open(cgPath) as f:
        s = f.read()
        sLines = s.split("\n")
        for sLine in sLines:
            for pattern in patternList:
                if re.match(pattern, sLine):
                    sList = sLine.split()
                    paraDict[pattern] = float(sList[2])
    # print(paraDict)
    return paraDict


def matLoad(u, v):
    mat = sio.loadmat(
        "/home/takashi/Desktop/dataset/from_iwatsuki/mat_file/additional_disp_mat/%s.mat"
        % LFName
    )
    disp_gt = mat["depth"]
    return disp_gt[u][v]


def pix2m_disp(x, y, imgIdx):
    from libs.variable import dispImg2, dispImg1

    f_mm = paraDict["focal_length_mm"]
    s_mm = paraDict["sensor_size_mm"]
    b_mm = paraDict["baseline_mm"]
    longerSide = max(dispImg1.shape[0], dispImg1.shape[1])
    beta = b_mm * f_mm * longerSide
    f_pix = (f_mm * longerSide) / s_mm
    print("???")

    if imgIdx == 1 and dispImg1[x][y]:
        Z = float(beta * f_mm) / float((dispImg1[x][y] * f_mm * s_mm + beta))
    elif imgIdx == 2 and dispImg2[x][y]:
        Z = float(beta * f_mm) / float((dispImg2[x][y] * f_mm * s_mm + beta))
    else:
        print("zero!!")
        Z = 0
    X = (float(x) - float(dispImg1.shape[1] / 2.0)) * Z / f_pix
    Y = (float(y) - float(dispImg1.shape[0] / 2.0)) * Z / f_pix
    # X = float(x) * Z / f_pix
    # Y = float(y) * Z / f_pix
    return X, Y, -Z  # 単位はmm


def alphaCompositing(img1, img2):
    dst = cv2.addWeighted(img1, 0.5, img2, 0.5, 0)
    cv2.imwrite("appha.png", dst)
