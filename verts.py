import os
import numpy as np
import cv2
from libs.plyClass import Ply

# mesh1とmesh2_1を作成
# mesh1の透明度を上げる
# mesh1とmesh2_1を統合

sameMin = []
sameMax = []
sigma = 1.0


def flatten(list):
    flattenArray = np.ravel(np.array(list))
    return flattenArray


def setMinMax(array):  # 最初のmeshの最大最小を覚えておくという関数
    global sameMax, sameMin
    for i in range(3):
        if len(sameMax) < 4:
            sameMax.append(np.max(array[:, i]))
            sameMin.append(np.min(array[:, i]))


def setSameXY(array):  # xとy最大値でxとyを正規化, Zだけわかんないから-1~1で正規化
    global sameMax, sameMin
    # for i in range(3):
    if len(sameMax) < 4:
        sameMax.append(np.max(array[:, :1]))
        sameMin.append(np.min(array[:, :1]))
        sameMax.append(np.max(array[:, :1]))
        sameMin.append(np.min(array[:, :1]))
        sameMax.append(np.max(array[:, 2]) * sigma)
        sameMin.append(np.min(array[:, 2]) * sigma)


def setSameXYZ(array):  # xとyとZ最大値でxとyとZを正規化, addなど、Zが既知の場合
    global sameMax, sameMin
    for i in range(3):
        if len(sameMax) < 4:
            sameMax.append(np.max(array[:, 3]))
            sameMin.append(np.min(array[:, 3]))


def mmNormal(array):
    setMinMax(array)
    # setSameXYZ(array)
    # print(sameMax, sameMin)
    scale = 0.5
    dst = np.zeros(array.shape)
    for i in range(3):
        for line in range(array.shape[0]):
            dst[line][i] = (
                scale
                * float(array[line][i] - sameMin[i])
                / float(sameMax[i] - sameMin[i])
                - scale / 2.0
            )
    return dst


def averageZero(array):
    average = np.average(array, axis=0)
    return array - average


def setVerts(mesh_fi):
    mesh = Ply(mesh_fi=mesh_fi)
    # print(mesh.verts_np[0:5])
    mesh.setInfos()
    mesh.changeAlpha(alpha=255)
    verts_np = mesh.verts_np
    colors_np = mesh.colors_np
    # verts_np = cvtXY(verts_np)
    verts_np = averageZero(verts_np)
    # print(np.average(verts_np))

    verts_np = mmNormal(verts_np)
    vertices = flatten(verts_np)
    colors = flatten(colors_np / 255.0)
    return colors, vertices


if __name__ == "__main__":
    mesh_fi = "./mesh/IMG_4652.ply"
    setVerts(mesh_fi)
