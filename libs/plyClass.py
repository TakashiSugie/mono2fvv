import numpy as np
from libs.libs import pix2m_disp
import cv2

# v_infos 行の情報,色を含む
# verts_np np配列 vx,vy,vzを含む(n,3)の配列
# colors_np np配列 rgbの(n,3)配列
# v_lineいる？いらん


class Ply:
    def __init__(self, mesh_fi=None, img=None, imgIdx=None):
        if mesh_fi:
            self.plyName = mesh_fi
            self.ClassReadPly()
            self.setAlpha = False
            self.setInfos()
        elif imgIdx:
            # img = cv2.imread(imgPath)

            self.PlyFromImg(img, imgIdx)
        else:
            print("Ply init  error")

    def ClassReadPly(self):
        self.ply_fi = open(self.plyName, "r")
        self.f_infos = []
        self.v_infos = []
        while True:
            line = self.ply_fi.readline().split("\n")[0]
            if line.startswith("element vertex"):
                self.num_vertex = int(line.split(" ")[-1])
            elif line.startswith("element face"):
                self.num_face = int(line.split(" ")[-1])
            elif line.startswith("comment"):
                if line.split(" ")[1] == "H":
                    self.Height = int(line.split(" ")[-1].split("\n")[0])
                if line.split(" ")[1] == "W":
                    self.Width = int(line.split(" ")[-1].split("\n")[0])
                if line.split(" ")[1] == "hFov":
                    self.hFov = float(line.split(" ")[-1].split("\n")[0])
                if line.split(" ")[1] == "vFov":
                    self.vFov = float(line.split(" ")[-1].split("\n")[0])
            elif line.startswith("end_header"):
                break
        contents = self.ply_fi.readlines()
        vertex_infos = contents[: self.num_vertex]
        face_infos = contents[self.num_vertex :]

        for vertex_info in vertex_infos:
            self.v_infos.append(vertex_info)

        for f_info in face_infos:
            self.f_infos.append(f_info)

    def ClassWritePly(self, save_fi, npyPath=None):
        if npyPath == None:
            self.infos2str()
        else:
            self.dotsM(npyPath)
        # self.changeRound(roundV=4)
        print("Writing mesh file %s ..." % save_fi)
        with open(save_fi, "w") as ply_fi:
            ply_fi.write("ply\n" + "format ascii 1.0\n")
            ply_fi.write("comment H " + str(self.Height) + "\n")
            ply_fi.write("comment W " + str(self.Width) + "\n")
            ply_fi.write("comment hFov " + str(self.hFov) + "\n")
            ply_fi.write("comment vFov " + str(self.vFov) + "\n")
            ply_fi.write("element vertex " + str(self.num_vertex) + "\n")
            ply_fi.write(
                "property float x\n"
                + "property float y\n"
                + "property float z\n"
                + "property uchar red\n"
                + "property uchar green\n"
                + "property uchar blue\n"
                + "property uchar alpha\n"
            )
            ply_fi.write("element face " + str(self.num_face) + "\n")
            ply_fi.write("property list uchar int vertex_index\n")
            ply_fi.write("end_header\n")
            ply_fi.writelines(self.v_line + "\n")
            ply_fi.writelines(self.f_line)
        ply_fi.close()

    def setInfos(self):
        # self.verts_npとself.colors_npをセット
        # verts_np.shape=(len,3)
        # colors_np.shape=(len,3)
        vertsList = []
        colorsList = []
        for v_info in self.v_infos:
            str_info = [float(v) for v in v_info.split("\n")[0].split(" ")]
            if len(str_info) == 6:
                vx, vy, vz, r, g, b = str_info
                colorsList.append([r, g, b])

            else:
                vx, vy, vz, r, g, b, alpha = str_info
                colorsList.append([r, g, b, alpha])
                self.setAlpha = True

            vertsList.append([vx, vy, vz])
        self.verts_np = np.array(vertsList)
        self.colors_np = np.array(colorsList)

    def infos2str(self):  # listで来たv_infosの各要素を取り出して、変換を行わずにstr型に変換する
        self.v_line = "".join(self.v_infos)
        self.f_line = "".join(self.f_infos)

    def np2infos(self):
        infoList = []
        ones = np.ones((self.verts_np.shape[0], 1))
        infos = np.concatenate((self.verts_np, self.colors_np, ones), axis=1)
        for idx in range(infos.shape[0]):
            infoList.append(" ".join(list(map(str, infos[idx]))) + "\n")
        self.v_infos = infoList

    def dotsM(self, npyPath):
        M = np.load(npyPath)
        ones = np.ones((len(self.verts_np), 1))
        oldV = np.concatenate((self.verts_np, ones), axis=1)
        NewV = np.dot(M, oldV.T)
        self.verts_np = NewV
        return self

    def integrate(self, add_infos):
        # self.v_infos = np.concatenate((self.verts_np, add_infos[0]), axis=0)
        self.v_infos = np.concatenate((self.v_infos, add_infos[0]), axis=0)
        self.num_vertex += add_infos[1]

    def PlyFromImg(self, img, imgIdx):
        v_list = []
        for y in range(img.shape[1]):
            for x in range(img.shape[0]):
                X, Y, Z = pix2m_disp(x, y, imgIdx)
                v_list.append(
                    " ".join(
                        list(
                            map(
                                str,
                                [X, Y, Z, img[x][y][2], img[x][y][1], img[x][y][0], 1,],
                            )
                        )
                    )
                    + "\n"
                )
        self.num_vertex = len(v_list)
        self.num_face = len(v_list)
        self.v_infos = v_list
        self.f_infos = []
        self.Height = img.shape[0]
        self.Width = img.shape[1]
        self.hFov = 0.9272952180016122
        self.vFov = 0.9272952180016122

    # 色を変更したり、輝度値を全体的に変化させたり
    def changeColor(self, r=255, g=255, b=255, sigma=1):

        if sigma < 1:
            self.colors_np *= sigma
        else:
            colors = np.tile(np.array([r, g, b]), (self.colors_np.shape[0], 1))
            self.colors_np = colors

    # 小数点以下をどれくらい丸めるか
    def changeRound(self, roundV=4, roundC=0):
        self.verts_np = np.round(self.verts_np, decimals=roundV)
        self.colors_np = np.round(self.colors_np, decimals=roundC)

    def changeAlpha(self, alpha=255):
        alpha = np.full(len(self.colors_np), alpha)
        self.colors_np[:, 3] = alpha


if __name__ == "__main__":
    mesh_fi = "./mesh/input_Cam000.ply"
    mesh1 = Ply(mesh_fi)
    # print(mesh1.num_vertex)
